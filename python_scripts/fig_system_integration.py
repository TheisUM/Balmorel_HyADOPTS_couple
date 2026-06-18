from pybalmorel import MainResults
import pandas as pd
import matplotlib.pyplot as plt
from balmorel_loading import compute_balmorel_distances

def plot_system_integration(gdx_file='MainResults.gdx',
                     path='gdxfiles',
                     ) -> None:
    """
    Plot hourly electricity prices from Balmorel GDX files for a specific year, country, and region.
    Inputs:
     - gdx file to read from
     - path to the gdx file
     - year to plot
     Outputs:
     - A plot of hourly electricity prices, VRE production, and electrolyser consumption for the specified year.
     """
    
    capacity_data = {}
    econ_data = {}

    for i, gdx in enumerate(gdx_file):
        ### Load Balmorel results
        res = MainResults(files=gdx, paths=path)
        g_cap = res.get_result('G_CAP_YCRAF')
        g_sto = res.get_result('G_STO_YCRAF')
        prod = res.get_result('PRO_YCRAGF')
        xh2_cap = res.get_result('XH2_CAP_YCR')
        x_cap = res.get_result('X_CAP_YCR')
        eco_g = res.get_result('ECO_G_YCRAG')
        eco_x = res.get_result('ECO_X_YCR')
        eco_xh2 = res.get_result('ECO_XH2_YCR')

        ### G_CAP
        g_cap = g_cap[g_cap['Technology'].isin(['WIND-ON', 'WIND-OFF', 'SOLAR-PV','ELECTROLYZER'])]
        g_cap = g_cap.groupby(['Year','Technology']).agg({'Value':'sum'}).reset_index()
        ### G_STO
        g_sto = g_sto[g_sto['Technology'].isin(['INTRASEASONAL-ELECT-STORAGE'])]
        g_sto = g_sto.groupby(['Year','Technology']).agg({'Value':'sum'}).reset_index()

        prod = prod[prod['Technology'].isin(['WIND-ON', 'WIND-OFF', 'SOLAR-PV','ELECTROLYZER'])]
        prod = prod.groupby(['Year','Technology']).agg({'Value':'sum'}).reset_index()
        prod = prod.pivot(index='Year', columns='Technology', values='Value').reset_index()

        ### X_CAP and XH2_CAP
        distances = compute_balmorel_distances()
        # pipelines
        xh2_cap['CapDistance'] = xh2_cap.apply(lambda row: distances[row['From']][row['To']] * row['Value'], axis=1)
        xh2_cap = xh2_cap.groupby('Year').agg({'CapDistance':'sum'}).reset_index()
        xh2_cap['CapDistance'] = xh2_cap['CapDistance'] / 2 / 1000  # Convert to TWkm
        # transmission
        x_cap['CapDistance'] = x_cap.apply(lambda row: distances[row['From']][row['To']] * row['Value'], axis=1)
        x_cap = x_cap.groupby('Year').agg({'CapDistance':'sum'}).reset_index()
        x_cap['CapDistance'] = x_cap['CapDistance'] / 2 / 1000  # Convert to TWkm
        
        g_cap = g_cap.pivot(index='Year', columns='Technology', values='Value').reset_index()
        g_cap['PIPELINE'] = xh2_cap['CapDistance']
        g_cap['TRANSMISSION'] = x_cap['CapDistance']
        g_cap['INTRASEASONAL-ELECT-STORAGE'] = g_sto['Value']

        capacity_data[gdx] = g_cap

        ### ECON
        eco_g = eco_g[eco_g['SUBCATEGORY'].isin(['GENERATION_CAPITAL_COSTS',
                                                 'GENERATION_FIXED_COSTS',
                                                 'GENERATION_OPERATIONAL_COSTS',
                                                 'GENERATION_FUEL_COSTS',
                                                 'GENERATION_CO2_TRANSPORT'])]
        tech_to_keep = ['WIND-ON', 'WIND-OFF', 'SOLAR-PV', 'ELECTROLYZER', 'INTRASEASONAL-ELECT-STORAGE']
        eco_g['TECH_TYPE'] = eco_g['TECH_TYPE'].apply(lambda x: x if x in tech_to_keep else 'OTHER')
        eco_g = eco_g.groupby(['Scenario','Y','TECH_TYPE']).agg({'Value':'sum'}).reset_index()
        eco_x = eco_x[eco_x['SUBCATEGORY'].isin(['TRANSMISSION_CAPITAL_COSTS',
                                                 'TRANSMISSION_OPERATIONAL_COSTS'])]
        eco_x = eco_x.groupby(['Scenario','Y']).agg({'Value':'sum'}).reset_index()
        eco_x['TECH_TYPE'] = 'TRANSMISSION'
        eco_xh2 = eco_xh2[eco_xh2['SUBCATEGORY'].isin(['H2_TRANSMISSION_CAPITAL_COSTS',
                                                        'H2_TRANSMISSION_OPERATIONAL_COSTS'])]
        eco_xh2 = eco_xh2.groupby(['Scenario','Y']).agg({'Value':'sum'}).reset_index()
        eco_xh2['TECH_TYPE'] = 'PIPELINE'

        eco = pd.concat([eco_g, eco_x, eco_xh2], ignore_index=True)
        eco = eco.pivot(index='Y', columns='TECH_TYPE', values='Value').reset_index()
        eco.set_index('Y', inplace=True)
        eco = eco/1000  # Convert to B€/year

        econ_data[gdx] = eco

        # if i == 3:
        print(g_cap)
        print(eco)
        print(prod)

    
    colors = {
        'WIND-ON': '#828BF2',
        'WIND-OFF': '#2F3EEA',
        'SOLAR-PV': '#F6D04D',
        'ELECTROLYZER': '#1FD082',
        'TRANSMISSION': '#E97132',
        'PIPELINE': "#66EEB3",
        'INTRASEASONAL-ELECT-STORAGE': '#F6C6AD',
        'OTHER': '#D9D9D9',
    }
    tech_names = {
        'WIND-ON': 'Onshore Wind (GW or B€/year)',
        'WIND-OFF': 'Offshore Wind (GW or B€/year)',
        'SOLAR-PV': 'Solar PV (GW or B€/year)',
        'ELECTROLYZER': 'Electrolyser (GW or B€/year)',
        'INTRASEASONAL-ELECT-STORAGE': 'Electricity storage (GWh or B€/year)',
        'TRANSMISSION': 'Transmission (TWkm or B€/year)',
        'PIPELINE': 'Pipeline (TWkm or B€/year)',
        'OTHER': 'Other',
    }
    tech_names_2 = {
        'WIND-ON': 'Onshore Wind',
        'WIND-OFF': 'Offshore Wind',
        'SOLAR-PV': 'Solar PV',
        'ELECTROLYZER': 'Electrolyser',
        'PIPELINE': 'Pipeline',
        'TRANSMISSION': 'Transmission',
        'INTRASEASONAL-ELECT-STORAGE': 'Electricity storage',
        'OTHER': 'Other',
    }

    eco_order = tech_names.keys()

    ### Plotting
    fig, axs = plt.subplots(2,4,figsize=(12,7))

    titles = ['Baseline (1)', 'Premium (2)', 'Auction (3)', 'Mandate (4)']
    techs = ['WIND-ON', 'WIND-OFF', 'SOLAR-PV','ELECTROLYZER','PIPELINE','TRANSMISSION','INTRASEASONAL-ELECT-STORAGE','OTHER']
    tech_markers = ['o','o','o','o','D','D','s','x']
    tech_linestyles = ['-','-','-','-','--','--',':','-']

    for i, gdx in enumerate(gdx_file):
        g_cap = capacity_data[gdx]
        eco = econ_data[gdx]
        for tech in techs:
            if tech != 'OTHER':
                g_cap.plot(x='Year', y=tech, kind='line', ax=axs[(0,i)], stacked=False,
                        marker=tech_markers[techs.index(tech)], linestyle=tech_linestyles[techs.index(tech)], linewidth=2,
                        color=colors[tech], label=tech_names[tech],legend=False)
        eco = eco[eco_order]  # Reorder columns to match the desired order
        eco = eco.drop(columns='OTHER')  # Drop the 'OTHER' category from the plot
        colors_eco = [colors[tech] for tech in eco.columns if tech in colors]
        labels_eco = [tech_names_2[tech] for tech in eco.columns if tech in tech_names_2]
        eco.plot(kind='bar', ax=axs[(1,i)], stacked=True, color=colors_eco,label=labels_eco, width=0.8,legend=False,zorder=10)

        handles, labels = axs[(0,i)].get_legend_handles_labels()
        labels = [tech_names.get(label, label) for label in labels]
        handles2, labels2 = axs[(1,i)].get_legend_handles_labels()
        labels2 = [tech_names_2.get(label, label) for label in labels2]

        if i == 0:
            axs[(0,i)].set_ylabel('Capacity (GW / TWkm / GWh)', fontsize=10)
            axs[(1,i)].set_ylabel('Annualized cost (B€/year)', fontsize=10)
            axs[(1,i)].legend(handles, labels, loc='upper left', bbox_to_anchor=(-0.1, -0.25), ncol=4, frameon=False, fontsize=9)
        else:  
            axs[(0,i)].set_yticklabels([])
            axs[(1,i)].set_yticklabels([])

        # if i==len(gdx_file)-1:
        #     axs[(0,i)].legend(handles, labels, loc='upper left', bbox_to_anchor=(1, 1),ncols=1,frameon=False, fontsize=10)
        #     axs[(1,i)].legend(handles2, labels2, loc='upper left', bbox_to_anchor=(1, 1), ncol=1, frameon=False, fontsize=10)

        axs[(0,i)].set_title(titles[i], fontsize=10)
        axs[(0,i)].set_xlabel('', fontsize=10)
        axs[(0,i)].set_xticklabels([])
        axs[(1,i)].set_xlabel('Year', fontsize=10)
        axs[(0,i)].set_ylim(0,2000)
        axs[(1,i)].set_ylim(0, 300)
        axs[(0,i)].grid(axis='y', linestyle='--', alpha=0.7, linewidth=0.7, zorder=-10)
        axs[(1,i)].grid(axis='y', linestyle='--', alpha=0.7, linewidth=0.7, zorder=-10)

    
    fig.subplots_adjust(hspace=0.05, wspace=0.07, bottom=0.2, top=0.95, left=0.08, right=0.95)
    plt.show()

    return None

if __name__ == "__main__":
    gdx_files = ['MainResults_base.gdx','MainResults_subsidy.gdx','MainResults_hba.gdx','MainResults_mandate.gdx']
    path = 'C:\\GitHub\\h2_system_dynamics_paper\\gdxfiles'
    plot_system_integration(gdx_file=gdx_files,path=path)