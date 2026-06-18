import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import numpy as np

installed_cap = np.logspace(0,10,num=100,base=2)
lrs = [0.1, 0.12, 0.15, 0.18, 0.2, 0.25]

init_capex = np.linspace(1000, 2500, 5)

# Create subplots
fig, axes = plt.subplots(nrows=1, ncols=len(init_capex), figsize=(4*len(init_capex), 5), sharey=True)
 
# Iterate over electricity cost values and plot
for i, c in enumerate(init_capex):
    ax = axes[i]
    ax.set_title(f'Initial CAPEX: {c:.2f} €/kW')
    ax.set_xlabel('Installed capacity [GW]')
    ax.set_ylabel('Capital cost [€/kW]')
    ax.grid(True)
 
    # Set y-axis limits
    #ax.set_ylim(0, 10)
    
    # Plot each CAPEX value as a separate line
    for lr in lrs:
        x = installed_cap
        y = [c * (ins/0.5)**(np.log2(1-lr)) for ins in installed_cap]

        ax.plot(x, y, label=f'{lr*100:.1f}')
    
    # Add a horizontal line at LCOH = 1 USD/kg
    #ax.axhline(y=1, color='red', linestyle='--', linewidth=2)
    
# Create a single legend outside the last plot on the right
handles, labels = axes[-1].get_legend_handles_labels()
fig.legend(handles, labels, loc='center', bbox_to_anchor=(0.5, -0.05), title='Learning rate [%]', ncol=len(lrs))
 
plt.tight_layout()

filename = f"results/capex_assumptions.png"
save_plot = os.path.join(os.getcwd(), filename)
 
fig.savefig(save_plot, dpi=300, bbox_inches='tight')