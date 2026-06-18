from pybalmorel import MainResults
import pandas as pd
import matplotlib.pyplot as plt
from balmorel_loading import load_balmorel_electricity_tariff

def plot_bal_hourly(gdx_file='MainResults.gdx',
                     path='gdxfiles',
                     year=2050,
                     y_axis_range=(-500,1500),
                     highest_price=500,
                     electricity_tariff=14.36
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
    # Select year
    el_balance = el_balance[el_balance['Year'] == str(year)]
    # Select data of interest
    vre_and_h2 = el_balance[el_balance['Technology'].isin(['WIND-ON', 'WIND-OFF', 'SOLAR-PV','DEMAND_P2G'])]
    el_price = el_balance[el_balance['Technology'] == 'PRICE']
    electricity_consumption = el_balance[el_balance['Technology'].isin(['DEMAND_P2H', 'DEMAND_P2G', 'DEMAND_EXO','DEMAND_CCS'])]

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

    electricity_tariff = load_balmorel_electricity_tariff(gdx_file = gdx_file, path = path)
    electricity_tariff = electricity_tariff[electricity_tariff.index == year].values[0]

    el_price['Electricity tariff'] = electricity_tariff
    el_price.drop(columns=['Value_el_demand', 'Value_el_purchased','Season','Time'], inplace=True)
    ### Aggregate data for VRE and electrolyser consumption
    vre_and_h2 = vre_and_h2.groupby(['Technology','Season','Time']).agg({'Value':'sum'}).reset_index()
    vre_and_h2.loc[vre_and_h2['Technology'] == 'DEMAND_P2G', 'Value'] = vre_and_h2.loc[vre_and_h2['Technology'] == 'DEMAND_P2G', 'Value'] * -1  # Make consumption negative for plotting

    vre_and_h2['Season_Time'] = vre_and_h2['Season'].astype(str) + '_' + vre_and_h2['Time'].astype(str)
    vre_and_h2['Value'] = vre_and_h2['Value'] / 1e3  # Convert to GWh
    vre_and_h2.index = vre_and_h2['Season_Time']
    vre_and_h2.drop(columns=['Season_Time','Season','Time'], inplace=True)
    vre_and_h2 = vre_and_h2.pivot(columns='Technology', values='Value').reset_index()
    
    colors = {
        'WIND-ON': '#828BF2',
        'WIND-OFF': '#2F3EEA',
        'SOLAR-PV': '#F6D04D',
        'DEMAND_P2G': '#1FD082'
    }
    tech_names = {
        'WIND-ON': 'Onshore Wind',
        'WIND-OFF': 'Offshore Wind',
        'SOLAR-PV': 'Solar PV',
        'DEMAND_P2G': 'Electrolyser'
    }

    ### Plotting
    fig, ax1 = plt.subplots(figsize=(10,7))
    vre_and_h2.plot(x='Season_Time',kind='bar', ax=ax1,stacked=True,width=1,
                    color=[colors.get(x, '#333333') for x in vre_and_h2.columns if x != 'Season_Time'])
    ax1.set_ylabel('Electricity production/consumption (GWh)', fontsize=12)
    ax1.set_xlabel('Hour of the year', fontsize=12)
    ax1.set_ylim(y_axis_range[0], y_axis_range[1])
    ax1.grid(axis='y', linestyle='--', alpha=0.7, linewidth=0.7, zorder=-10)
    ax1.xaxis.set_ticks([])
    ax2 = ax1.twinx()
    el_price.plot(x='Season_Time', ax=ax2, color=['black','grey'], linewidth=2,stacked=False,style='--',zorder=-10)
    handles, labels = ax1.get_legend_handles_labels()
    labels = [tech_names.get(label, label) for label in labels]
    ax1.legend(handles, labels, loc='lower left')
    ax2.set_ylabel('Electricity Price (EUR/MWh)', fontsize=12)
    plusminus_range = -y_axis_range[1] / y_axis_range[0]
    ax2.set_ylim(-highest_price/plusminus_range,highest_price)
    ax2.yaxis.set_ticks([i for i in range(int(-highest_price/plusminus_range)+1,int(highest_price)+1, int(250/plusminus_range))])
    ax2.legend(loc='lower right')
    # ax1.set_title(f'Hourly Electricity Prices, VRE Production and Electrolyser Consumption in {year}')
    fig.tight_layout()
    plt.show()

    return None

if __name__ == "__main__":
    plot_bal_hourly(gdx_file='MainResults_loop4.gdx',path='C:\\GitHub\\h2_system_dynamics_paper\\gdxfiles',highest_price=250)


