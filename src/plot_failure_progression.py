"""Fixed-seed random-demand trajectories, continued beyond the 30-node threshold."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from final_validation import setup, cascade

def make_progression(output='results/validation', runs=50, horizon=300):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    histories=[];records=[]
    for seed in range(3000,3000+runs):
        _,adj,c,state=setup(seed,'random',spread=.3)
        loads,active,lost=state
        initial=loads.sum();injected=0.
        rng=np.random.default_rng(np.random.SeedSequence([seed,20261030,77]))
        demands=rng.uniform(.5,1.5,horizon)
        failed=[0]
        records.append(dict(seed=seed,step=0,new_demand=0,failed_nodes=0,unserved=0))
        for t,x in enumerate(demands,1):
            if active.any():
                injected+=x
                loads[active]+=x/active.sum()
                (loads,active,lost),_=cascade(adj,c,(loads,active,lost))
                assert np.isclose(loads.sum()+lost, initial+injected)
            else:
                x=0. # terminal all-failed state: no further load is injected
            count=int(len(active)-active.sum());failed.append(count)
            records.append(dict(seed=seed,step=t,new_demand=float(x),failed_nodes=count,unserved=float(lost)))
        histories.append(failed)
    with (out/'random_demand_failure_trajectories.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    values=np.array(histories);time=np.arange(horizon+1)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(12,4.5))
    lo,hi=np.percentile(values,[10,90],axis=0)
    axes[0].fill_between(time,lo,hi,step='post',color='#2563eb',alpha=.15,label='10th–90th percentile across runs')
    axes[0].step(time,values.mean(axis=0),where='post',color='#2563eb',linewidth=2.4,label='Mean across 50 runs')
    axes[0].step(time,np.median(values,axis=0),where='post',color='#0d9488',linewidth=1.7,label='Median across runs')
    axes[0].set_title('Failures accumulate under random demand')
    for j in range(5):
        axes[1].step(time,values[j],where='post',linewidth=1.8,label=f'Seed {3000+j}')
    axes[1].set_title('Early damage detail: first five seeds')
    # Same time window on both panels, retaining all quiet and failure periods.
    for ax in axes:
        if ax is axes[0]: ax.axhline(30,color='#be123c',linestyle=':',linewidth=1.5,label='30-node collapse threshold')
        ax.set(xlabel='Simulation step',ylabel='Failed nodes out of 100',ylim=(0,103),xlim=(0,180))
        ax.grid(alpha=.2);ax.legend(fontsize=7,loc='upper left')
    axes[1].set_ylim(0,15)
    axes[1].set_ylabel('Failed nodes (zoom: 0–15)')
    axes[1].get_legend().remove()
    axes[1].legend(fontsize=7,loc='upper left')
    fig.tight_layout()
    fig.savefig(out/'random_demand_failure_progression.pdf')
    fig.savefig(out/'random_demand_failure_progression.png',dpi=180)
    plt.close(fig)
    def first_cross(v,k):
        idx=np.flatnonzero(v>=k);return int(idx[0]) if len(idx) else None
    first=[first_cross(v,1) for v in values];collapse=[first_cross(v,30) for v in values];full=[first_cross(v,100) for v in values]
    print('First 5 trajectories (first failure, 30-node threshold, complete failure):')
    for j in range(5):print(3000+j,first[j],collapse[j],full[j])
    print('Full failures by horizon:',sum(t is not None for t in full),'/',runs)
    return out/'random_demand_failure_progression.png'

if __name__=='__main__':
    import sys
    make_progression(sys.argv[1] if len(sys.argv)>1 else 'results/validation')
