from pathlib import Path
import csv
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def make_figures(directory='results/validation'):
    root=Path(directory)
    rows=list(csv.DictReader((root/'topology_runs.csv').open()))
    summary=json.loads((root/'summary.json').read_text())
    tops=['random','small_world','scale_free']; colors=['#2563eb','#d97706','#0d9488']
    titles=['Random','Small-world','Scale-free (BA)']
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    for ti,(top,col,title) in enumerate(zip(tops,colors,titles)):
        groups=[[float(r['collapse_step']) for r in rows if r['topology']==top and float(r['spread'])==s] for s in (0.,.2,.3)]
        x=np.arange(3)+(ti-1)*.23
        b=axes[0].boxplot(groups,positions=x,widths=.2,patch_artist=True,manage_ticks=False,
                          medianprops={'color':'black'})
        for box in b['boxes']:box.set(facecolor=col,alpha=.65)
        axes[0].plot([],[],color=col,linewidth=6,label=title)
        gaps=[[float(r['gap']) for r in rows if r['topology']==top and float(r['spread'])==s] for s in (0.,.2,.3)]
        axes[1].plot(np.arange(3),[np.median(g) for g in gaps],marker='o',color=col,label=title)
    for ax in axes:ax.set_xticks([0,1,2],['Equal: 10','Mild: 8–12','Larger: 7–13']);ax.grid(axis='y',alpha=.2)
    axes[0].set_ylabel('Collapse step');axes[0].set_title('Collapse timing across 50 matched seeds');axes[0].legend(fontsize=8)
    axes[1].set_ylabel('Median steps from first failure to collapse');axes[1].set_title('Damage can precede threshold crossing');axes[1].legend(fontsize=8)
    fig.tight_layout();fig.savefig(root/'topology_comparison.png',dpi=180);fig.savefig(root/'topology_comparison.pdf');plt.close(fig)
    metrics=summary['forecast_summaries']
    fig,axes=plt.subplots(1,2,figsize=(12,4.8))
    for ai,a in enumerate((.2,.5)):
        values=[next(r for r in metrics if r['topology']==top and r['amplitude']==a) for top in tops]
        x=np.arange(3)+(ai-.5)*.14
        y=np.array([r['coverage'] for r in values])*100
        low=np.array([r['coverage_95_wilson'][0] for r in values])*100
        high=np.array([r['coverage_95_wilson'][1] for r in values])*100
        axes[0].errorbar(x,y,yerr=[np.maximum(y-low,0),np.maximum(high-y,0)],fmt='o',capsize=4,label=f'Demand variability a={a}')
    axes[0].axhline(80,color='gray',ls='--',label='Nominal 80% interval');axes[0].set_ylim(0,105)
    axes[0].set_ylabel('Observed interval coverage (%)');axes[0].set_title('30 independent futures per group; 95% Wilson bars')
    axes[0].set_xticks(range(3),titles);axes[0].legend(fontsize=8)
    x=np.arange(6)
    axes[1].bar(x-.18,[r['mae'] for r in metrics],.36,color='#2563eb',label='Full-state model forecast')
    axes[1].bar(x+.18,[r['baseline_mae'] for r in metrics],.36,color='#94a3b8',label='Training-median lifetime baseline')
    axes[1].set_xticks(x,[f"{titles[tops.index(r['topology'])]}\na={r['amplitude']}" for r in metrics],fontsize=8)
    axes[1].set_ylabel('Mean absolute error (steps)');axes[1].set_title('Remaining-time accuracy at observation step 20');axes[1].legend(fontsize=8)
    axes[1].tick_params(axis='x', labelrotation=25)
    for label in axes[1].get_xticklabels(): label.set_ha('right')
    for ax in axes:ax.grid(axis='y',alpha=.2)
    fig.tight_layout();fig.savefig(root/'uncertainty_validation.png',dpi=180);fig.savefig(root/'uncertainty_validation.pdf');plt.close(fig)
    return [root/'topology_comparison.png',root/'uncertainty_validation.png']

if __name__=='__main__':
    import sys
    print(make_figures(sys.argv[1] if len(sys.argv)>1 else 'results/validation'))
