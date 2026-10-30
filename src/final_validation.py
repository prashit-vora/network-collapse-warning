"""Reproducible, simulation-internal validation. No fitted ML predictor."""
from pathlib import Path
import csv
import json
import numpy as np
import networkx as nx

TOPOLOGIES = ('random', 'small_world', 'scale_free')

def setup(seed, topology, spread=.3, n=100):
    graph_rng = np.random.default_rng(np.random.SeedSequence([seed, 11]))
    for attempt in range(10000):
        gs = int(graph_rng.integers(0, 2**32-1))
        if topology == 'random': g = nx.gnp_random_graph(n, 6/(n-1), seed=gs)
        elif topology == 'small_world': g = nx.watts_strogatz_graph(n, 6, .1, seed=gs)
        elif topology == 'scale_free': g = nx.barabasi_albert_graph(n, 3, seed=gs)
        else: raise ValueError(topology)
        if nx.is_connected(g): break
    else: raise RuntimeError('Connectivity conditioning exhausted')
    # Shared initial loads/capacities across topologies for each seed.
    rng = np.random.default_rng(np.random.SeedSequence([seed, 12]))
    loads = rng.uniform(4, 7, n)
    crng = np.random.default_rng(np.random.SeedSequence([seed, 13]))
    offsets = crng.uniform(0, 1, n//2)
    offsets = np.r_[offsets, -offsets]; crng.shuffle(offsets)
    capacity = 10*(1+spread*offsets)
    assert np.isclose(capacity.sum(), 1000) and np.all(loads < capacity)
    neighbors = [np.array(sorted(g.neighbors(i)), dtype=int) for i in range(n)]
    return g, neighbors, capacity, (loads, np.ones(n, dtype=bool), 0.)

def cascade(neighbors, capacity, state):
    loads, active, lost = state
    rounds = []
    while True:
        failing = np.flatnonzero(active & (loads > capacity))
        if not len(failing): break
        active[failing] = False
        additions = np.zeros(len(loads))
        for i in failing:
            recipients = neighbors[i][active[neighbors[i]]]
            if len(recipients): additions[recipients] += loads[i]/len(recipients)
            else: lost += loads[i]
        loads[failing] = 0
        loads += additions
        rounds.append(len(failing))
    return (loads, active, lost), rounds

def advance(neighbors, capacity, initial, demands, accelerated=True):
    """Strict overload after whole steps. Returns first 30%-failure crossing."""
    loads, active, lost = initial
    loads, active = loads.copy(), active.copy()
    start_total = loads.sum()+lost
    initial_failed = len(active)-active.sum()
    threshold = int(np.ceil(.3*len(active)))
    cursor = 0; first = None; largest = 0
    if initial_failed >= threshold:
        return dict(time=0, first_failure=0, largest_cascade=0, failed=int(initial_failed)), (loads,active,lost)
    while cursor < len(demands):
        nactive = int(active.sum())
        if accelerated:
            required = nactive*np.min(capacity[active]-loads[active])
            cumulative = np.cumsum(demands[cursor:])
            k = int(np.searchsorted(cumulative, required, side='right'))+1
            k = min(k, len(cumulative))
            injected = float(cumulative[k-1])
        else:
            k=1; injected=float(demands[cursor])
        loads[active] += injected/nactive
        cursor += k
        before = int(active.sum())
        (loads, active, lost), rounds = cascade(neighbors, capacity, (loads,active,lost))
        failed_now = before-int(active.sum())
        if failed_now and first is None: first=cursor
        largest=max(largest,failed_now)
        assert np.isclose(loads.sum()+lost, start_total+np.sum(demands[:cursor]), rtol=1e-10,atol=1e-8)
        if len(active)-active.sum() >= threshold: break
    time = cursor if len(active)-active.sum() >= threshold else None
    return dict(time=time, first_failure=first, largest_cascade=largest,
                failed=int(len(active)-active.sum())), (loads,active,lost)

def draws(seed, amplitude, horizon=1000):
    return np.random.default_rng(seed).uniform(1-amplitude,1+amplitude,horizon)

def write_csv(path, rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def wilson(k,n,z=1.96):
    if not n:return [None,None]
    p=k/n; d=1+z*z/n
    center=(p+z*z/(2*n))/d
    half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0,center-half),min(1,center+half)]

def run(output='results/validation', topology_runs=50, calibration_runs=30, paths=300):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    # Validate optimization against whole-step reference on independent cases.
    matched=0
    for top in TOPOLOGIES:
        for seed in range(7000,7010):
            _,adj,c,s=setup(seed,top)
            d=draws(seed,.5)
            fast,_=advance(adj,c,s,d)
            slow,_=advance(adj,c,s,d,False)
            assert fast==slow,(top,seed,fast,slow)
            matched+=1
    print(f'Accelerated vs whole-step reference: {matched} matched cases',flush=True)
    topo=[]
    for top in TOPOLOGIES:
        for seed in range(2000,2000+topology_runs):
            for spread in (0.,.2,.3):
                g,adj,c,s=setup(seed,top,spread)
                r,_=advance(adj,c,s,np.ones(1000))
                topo.append(dict(topology=top,seed=seed,spread=spread,mean_degree=2*g.number_of_edges()/len(g),
                    collapse_step=r['time'],first_failure=r['first_failure'],
                    gap=r['time']-r['first_failure'] if r['time'] is not None else None,
                    largest_cascade=r['largest_cascade'],failed_at_collapse=r['failed']))
        print('Topology completed:',top,flush=True)
    write_csv(out/'topology_runs.csv',topo)
    # Independent training seeds for a simple constant-total-lifetime baseline.
    # At fixed observation step 20 it predicts training median remaining lifetime.
    training={}
    for ti,top in enumerate(TOPOLOGIES):
        for a in (.2,.5):
            lifetimes=[]
            for seed in range(10000,10030):
                _,adj,c,s=setup(seed,top)
                r,_=advance(adj,c,s,draws(seed+300000,a))
                if r['time'] is not None and r['time']>20:lifetimes.append(r['time']-20)
            training[(top,a)]=float(np.median(lifetimes))
    forecasts=[]
    for ti,top in enumerate(TOPOLOGIES):
        for a in (.2,.5):
            for seed in range(3000,3000+calibration_runs):
                _,adj,c,s=setup(seed,top)
                # The actual prefix/future are independent increments of one stream.
                actual=draws(np.random.SeedSequence([seed,ti,int(a*100),21]),a,1020)
                prefix,state=advance(adj,c,s,actual[:20])
                if prefix['time'] is not None:
                    forecasts.append(dict(topology=top,amplitude=a,seed=seed,status='collapsed_before_observation'))
                    continue
                truth,_=advance(adj,c,state,actual[20:])
                times=[]
                rng=np.random.default_rng(np.random.SeedSequence([seed,ti,int(a*100),22]))
                for j in range(paths):
                    r,_=advance(adj,c,state,rng.uniform(1-a,1+a,1000))
                    times.append(r['time'])
                if any(t is None for t in times) or truth['time'] is None:
                    raise RuntimeError('Censoring requires survival-aware summaries; do not drop censored paths')
                lo,med,hi=np.quantile(times,[.1,.5,.9],method='inverted_cdf')
                row=dict(topology=top,amplitude=a,seed=seed,status='evaluated',actual_remaining=truth['time'],
                    median=float(med),lower=float(lo),upper=float(hi),covered=bool(lo<=truth['time']<=hi),
                    absolute_error=float(abs(med-truth['time'])),interval_width=float(hi-lo),
                    lifetime_baseline=training[(top,a)],baseline_error=abs(training[(top,a)]-truth['time']))
                for h in (25,50):
                    row[f'p{h}']=float(np.mean(np.array(times)<=h));row[f'y{h}']=int(truth['time']<=h)
                forecasts.append(row)
            print('Conditional forecast checks:',top,a,flush=True)
    # Fixed fields allow pre-observation exclusions without inventing outcomes.
    fields=set().union(*(r.keys() for r in forecasts))
    full=[{k:r.get(k) for k in sorted(fields)} for r in forecasts]
    write_csv(out/'forecast_checks.csv',full)
    summaries=[]
    for top in TOPOLOGIES:
        for a in (.2,.5):
            rows=[r for r in forecasts if r['topology']==top and r['amplitude']==a and r['status']=='evaluated']
            k=sum(r['covered'] for r in rows); n=len(rows)
            summaries.append(dict(topology=top,amplitude=a,n=n,coverage=k/n if n else None,
                coverage_95_wilson=wilson(k,n),mae=float(np.mean([r['absolute_error'] for r in rows])),
                baseline_mae=float(np.mean([r['baseline_error'] for r in rows])),
                mean_width=float(np.mean([r['interval_width'] for r in rows])),
                brier25=float(np.mean([(r['p25']-r['y25'])**2 for r in rows])),
                brier50=float(np.mean([(r['p50']-r['y50'])**2 for r in rows]))))
    report=dict(optimization_checks=matched,topology_runs=len(topo),forecast_paths=paths,
                observation_step=20,forecast_summaries=summaries,
                pre_observation_exclusions=sum(r['status']!='evaluated' for r in forecasts))
    (out/'summary.json').write_text(json.dumps(report,indent=2))
    return topo,forecasts,report

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',default='results/validation');args=p.parse_args()
    _,_,report=run(args.output)
    print(json.dumps(report,indent=2))
