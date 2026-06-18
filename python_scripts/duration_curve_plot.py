from pybalmorel import MainResults
import pandas as pd
import matplotlib.pyplot as plt
from balmorel_loading import compute_balmorel_distances

def plot_duration_curve(gdx_file='MainResults.gdx',
                     path='gdxfiles',
                     year=2050,
                     y_axis_range=(-500,1500),
                     highest_price=500,
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

    ### Load Balmorel results
    res = MainResults(files=gdx_file, paths=path)
    el_balance = res.get_result('EL_BALANCE_YCRST')
    g_cap = res.get_result('G_CAP_YCRAF')
    xh2_cap = res.get_result('XH2_CAP_YCR')
    # Select year
    el_balance = el_balance[el_balance['Year'] == str(year)]
    # g_cap = g_cap[g_cap['Year'] == str(year)]
    # xh2_cap = xh2_cap[xh2_cap['Year'] == str(year)]
    # Select data of interest
    vre_and_h2 = el_balance[el_balance['Technology'].isin(['WIND-ON', 'WIND-OFF', 'SOLAR-PV','DEMAND_P2G'])]
    el_price = el_balance[el_balance['Technology'] == 'PRICE']
    electricity_consumption = el_balance[el_balance['Technology'].isin(['DEMAND_P2H', 'DEMAND_P2G', 'DEMAND_EXO','DEMAND_CCS'])]
    cap_vre_and_h2 = g_cap[g_cap['Technology'].isin(['WIND-ON', 'WIND-OFF', 'SOLAR-PV','ELECTROLYZER'])]

    ### Prepare electricity price with a weighted average based on consumption
    electricity_consumption = electricity_consumption.groupby(['Scenario', 'Year', 'Country', 'Region', 'Season', 'Time']).agg({'Value':'sum'}).reset_index()
    el_price.drop(columns=['Technology','Unit'], inplace=True)
    # Merge electricity consumption with prices
    el_price = pd.merge(electricity_consumption, el_price, on=['Scenario', 'Year', 'Country', 'Region', 'Season', 'Time'], suffixes=('_el_demand', '_el_price'))
    el_price['Value_el_purchased'] = el_price['Value_el_demand'] * el_price['Value_el_price']
    # Calculate average electricity price
    el_price = el_price.groupby(['Season','Time']).agg({'Value_el_demand':'sum','Value_el_purchased': 'sum'}).reset_index()
    el_price['Average price'] = el_price['Value_el_purchased'] / el_price['Value_el_demand']
    el_price['Season_Time'] = el_price['Season'].astype(str) + '_' + el_price['Time'].astype(str)

    el_price.drop(columns=['Value_el_demand', 'Value_el_purchased','Season','Time'], inplace=True)
    ### Aggregate data for VRE and electrolyser consumption
    vre_and_h2 = vre_and_h2.groupby(['Technology','Season','Time']).agg({'Value':'sum'}).reset_index()
    vre_and_h2.loc[vre_and_h2['Technology'] == 'DEMAND_P2G', 'Value'] = vre_and_h2.loc[vre_and_h2['Technology'] == 'DEMAND_P2G', 'Value'] * -1  # Make consumption negative for plotting

    vre_and_h2['Season_Time'] = vre_and_h2['Season'].astype(str) + '_' + vre_and_h2['Time'].astype(str)
    vre_and_h2['Value'] = vre_and_h2['Value'] / 1e3  # Convert to GWh
    vre_and_h2.index = vre_and_h2['Season_Time']
    vre_and_h2.drop(columns=['Season_Time','Season','Time'], inplace=True)
    vre_and_h2 = vre_and_h2.pivot(columns='Technology', values='Value').reset_index()

    df_plotting = pd.merge(vre_and_h2, el_price, left_on='Season_Time', right_on='Season_Time')
    # df_plotting['VRE production+H2production'] = df_plotting['SOLAR-PV']
    # df_plotting.sort_values('VRE production+H2production', inplace=True, ascending=False)
    df_plotting.reset_index(inplace=True, drop=True)
    df_plotting['Rolling average price'] = df_plotting['Average price'].rolling(window=1, min_periods=1).mean()

    ### Prepare data on capacities for VRE, electrolyser, and pipelines
    # VRE and electrolyser capacities
    cap_vre_and_h2 = cap_vre_and_h2.groupby(['Year','Technology']).agg({'Value':'sum'}).reset_index()
    # pipelines
    distances = compute_balmorel_distances()
    xh2_cap['CapDistance'] = xh2_cap.apply(lambda row: distances[row['From']][row['To']] * row['Value'], axis=1)
    xh2_cap = xh2_cap.groupby('Year').agg({'CapDistance':'sum'}).reset_index()
    xh2_cap['CapDistance'] = xh2_cap['CapDistance'] / 2 / 1000  # Convert to TWkm
    # combine the two
    cap_vre_and_h2 = cap_vre_and_h2.pivot(index='Year', columns='Technology', values='Value').reset_index()
    cap_vre_and_h2['Pipeline capacity (TWkm)'] = xh2_cap['CapDistance']
    
    colors = {
        'WIND-ON': '#828BF2',
        'WIND-OFF': '#2F3EEA',
        'SOLAR-PV': '#F6D04D',
        'DEMAND_P2G': '#1FD082',
        'ELECTROLYZER': '#1FD082',
    }
    tech_names = {
        'WIND-ON': 'Onshore Wind',
        'WIND-OFF': 'Offshore Wind',
        'SOLAR-PV': 'Solar PV',
        'DEMAND_P2G': 'Electrolyser',
        'ELECTROLYZER': 'Electrolyser',
    }

    ### Plotting
    fig, (ax,ax1) = plt.subplots(1,2,figsize=(10,5), gridspec_kw={'width_ratios': [3, 1]})
    df_plotting.plot(x='Season_Time', y=['WIND-ON', 'WIND-OFF', 'SOLAR-PV','DEMAND_P2G'], kind='bar', ax=ax, stacked=True, width=1,
                     color=[colors.get(x, '#333333') for x in ['WIND-ON', 'WIND-OFF', 'SOLAR-PV','DEMAND_P2G']])
    # vre_and_h2.plot(x='Season_Time',kind='bar', ax=ax1,stacked=True,width=1,
    #                 color=[colors.get(x, '#333333') for x in vre_and_h2.columns if x != 'Season_Time'])
    ax.set_ylabel('Electricity production/consumption (GWh)', fontsize=10)
    ax.set_xlabel('Time, sorted (hours)', fontsize=10)
    ax.set_ylim(y_axis_range[0], y_axis_range[1])
    ax.grid(axis='y', linestyle='--', alpha=0.7, linewidth=0.7, zorder=-10)
    ax.xaxis.set_ticks([])
    ax2 = ax.twinx()
    df_plotting.plot(x='Season_Time', y=['Rolling average price'], ax=ax2, color=['black'], linewidth=2,stacked=False,style='-',zorder=-10)
    handles, labels = ax.get_legend_handles_labels()
    labels = [tech_names.get(label, label) for label in labels]
    ax.legend(handles, labels, loc='upper left')
    ax2.set_ylabel('Rolling average electricity price (EUR/MWh)', fontsize=10)
    plusminus_range = -y_axis_range[1] / y_axis_range[0]
    ax2.set_ylim(-highest_price/plusminus_range,highest_price)
    ax2.yaxis.set_ticks([-40, 0, 40,80,120])
    ax2.legend(loc='upper right')
    cap_vre_and_h2.plot(x='Year', y=['WIND-ON', 'WIND-OFF', 'SOLAR-PV','ELECTROLYZER'], kind='line', ax=ax1, stacked=False, marker='o',
                     color=[colors.get(x, '#333333') for x in ['WIND-ON', 'WIND-OFF', 'SOLAR-PV','ELECTROLYZER']])
    ax1.set_ylabel('Installed capacity (GW)', fontsize=10)
    ax1.set_xlabel('Year', fontsize=10)
    ax1.set_ylim(0,1400)
    handles, labels = ax1.get_legend_handles_labels()
    labels = [tech_names.get(label, label) for label in labels]
    ax1.legend(handles, labels, loc='upper left')
    ax1.grid(axis='y', linestyle='--', alpha=0.7, linewidth=0.7, zorder=-10)
    ax3 = ax1.twinx()
    cap_vre_and_h2.plot(x='Year', y=['Pipeline capacity (TWkm)'], kind='line', ax=ax3, color='black', linewidth=2, marker='o')
    ax3.set_ylabel('Pipeline capacity (TWkm)', fontsize=10)
    ax3.legend(['Pipeline capacity'], loc='lower right')
    ax3.set_ylim(0, 140)

    ax.set_title('a) Duration curve', fontsize=12, loc='left')
    ax1.set_title('b) Installed capacities', fontsize=12, loc='left')
    fig.tight_layout()
    plt.show()

    return None

if __name__ == "__main__":
    plot_duration_curve(gdx_file='MainResults_base.gdx',path='C:\\GitHub\\h2_system_dynamics_paper\\gdxfiles',highest_price=100)