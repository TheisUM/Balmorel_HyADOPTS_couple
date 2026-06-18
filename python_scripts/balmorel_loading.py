import pandas as pd
import seaborn as sns
import numpy as np
import os
import pysd
import pybalmorel
from pybalmorel import IncFile
from pybalmorel import MainResults
from geopy.distance import geodesic
# import compute_balmorel_distances

def compute_balmorel_distances(path_to_coordinates='\\data\\coordinates_RRR.csv',
                               path_to_regions='\\data\\RRR.xlsx',
                               path_to_connections='\\data\\RRR_connections.xlsx'):
    """
    Computes distances for Balmorel model based on input data.

    Parameters:
    data (list of tuples): Each tuple contains coordinates (x, y) of a point.

    Returns:
    list of list: A matrix representing distances between each pair of points.
    """
    
    # get current working directory
    cwd = os.getcwd()

    # load regions and coordinates for regions
    coordinates = pd.read_csv(cwd + path_to_coordinates)
    regions = pd.read_excel(cwd + path_to_regions)
    land_connections = pd.read_excel(cwd + path_to_connections, sheet_name='land connections')
    sea_connections = pd.read_excel(cwd + path_to_connections, sheet_name='subsea connections')

    # make sure RRR columns are strings and strip any whitespace
    regions['RRR'] = regions['RRR'].astype(str).str.strip()
    coordinates['RRR'] = coordinates['RRR'].astype(str).str.strip()
    # merge regions with coordinates on RRR column
    regions = regions.merge(coordinates, on="RRR")
    labels = regions['RRR'].tolist()
    # Prepare a list of tuples with (latitude, longitude) for each region
    region_coords = [(row['Lat'], row['Lon']) for _, row in regions.iterrows()]

    # Calculate distances between regions using coordinates
    rerouting_factor = 1.3 # factor to account for rerouting of lines due to terrain, urban areas, etc.
    s = len(regions)
    distances = np.zeros((s, s))
    for i in range(s):
        for j in range(s):
            distances[i, j] = geodesic(region_coords[i], region_coords[j]).km * rerouting_factor
    df_dist = pd.DataFrame(distances, index=labels, columns=labels)

    land_connections.set_index(land_connections.columns[0], inplace=True)
    land_connections.index.name = None

    sea_connections.set_index(sea_connections.columns[0], inplace=True)
    sea_connections.index.name = None

    all_connections = land_connections.add(sea_connections, fill_value=0)
    all_connections.fillna(0, inplace=True) # fill NaN values with 0 for connections that do not exist
    all_connections

    distance_matrix = df_dist * all_connections

    return distance_matrix

def load_balmorel_electricity_prices(gdx_file = 'MainResults.gdx',
                                    path = 'gdxfiles',
                                    final_year = 2050,
                                    ):
    """
    Load electricity price data from Balmorel GDX files.
    Inputs:
     - gdx file to read from
     - path to the gdx file
    Outputs:
     - average electricity price seen by electrolyzers in the system (Y) (dataframe)
     - average electricity price in the system (Y) (dataframe)
    """
    res = MainResults(files=gdx_file, paths=path)

    hourly_electricity_prices = res.get_result('EL_PRICE_YCRST')
    #
    #CO2_price_national = res.get_result('CO2_PRICE_C')
    #CO2_price_system = res.get_result('CO2_PRICE_NA')
    fuel_consumption = res.get_result('F_CONS_YCRAST')
    el_demand = res.get_result('EL_DEMAND_YCRST')

    ### Electricity price seen by the electrolyzer
    fuel_consumption_electrolyzer = fuel_consumption[fuel_consumption['Technology'] == 'ELECTROLYZER']
    fuel_consumption_electrolyzer.drop(columns=['Area','Generation','Fuel','Unit','Technology'], inplace=True)
    hourly_electricity_prices.drop(columns=['Unit'], inplace=True)
    # Merge the two dataframes on all common columns except 'Value'
    merge_cols = ['Scenario', 'Year', 'Country', 'Region', 'Season', 'Time']
    el_price_electrolyzer = pd.merge(fuel_consumption_electrolyzer, hourly_electricity_prices, on=merge_cols, suffixes=('_el_consumption', '_el_price'))

    # Multiply the 'Value' columns together to get the electricity payments
    el_price_electrolyzer['Value_el_purchased'] = el_price_electrolyzer['Value_el_consumption'] * el_price_electrolyzer['Value_el_price']
    # Aggregate the time dimensions, to get yearly values
    capture_price_regional = el_price_electrolyzer.groupby(['Scenario', 'Year', 'Country', 'Region']).agg({'Value_el_consumption':'sum','Value_el_purchased': 'sum'}).reset_index()
    capture_price_system = el_price_electrolyzer.groupby(['Scenario', 'Year']).agg({'Value_el_consumption':'sum','Value_el_purchased': 'sum'}).reset_index()
    # Find an average electricity price for the year used when consuming the electricity
    capture_price_regional['Value_elprice'] = capture_price_regional['Value_el_purchased'] / capture_price_regional['Value_el_consumption']
    capture_price_regional.drop(columns=['Scenario','Value_el_consumption', 'Value_el_purchased'], inplace=True)
    capture_price_system['Value_elprice'] = capture_price_system['Value_el_purchased'] / capture_price_system['Value_el_consumption']
    capture_price_system.drop(columns=['Scenario','Value_el_consumption', 'Value_el_purchased'], inplace=True)

    el_demand.drop(columns=['Category','Unit'], inplace=True)
    electricity_price_system = pd.merge(el_demand, hourly_electricity_prices, on=merge_cols, suffixes=('_el_demand', '_el_price'))
    electricity_price_system['Value_el_purchased'] = electricity_price_system['Value_el_demand'] * electricity_price_system['Value_el_price']
    electricity_price_system = electricity_price_system.groupby(['Scenario', 'Year']).agg({'Value_el_demand':'sum','Value_el_purchased': 'sum'}).reset_index()
    electricity_price_system['Value_elprice'] = electricity_price_system['Value_el_purchased'] / electricity_price_system['Value_el_demand']
    electricity_price_system.drop(columns=['Value_el_demand', 'Value_el_purchased'], inplace=True)

    capture_price = capture_price_system.set_index('Year')['Value_elprice']
    capture_price['2022'] = capture_price['2030']
    capture_price = capture_price.sort_index()
    capture_price = capture_price.astype(float)
    capture_price = capture_price.reindex(
        pd.Series(np.arange(2022, final_year + 1), name='Year').astype(str)
    ).interpolate(method='linear')
    capture_price.index = capture_price.index.astype(float)

    electricity_price = electricity_price_system.set_index('Year')['Value_elprice']
    electricity_price['2022'] = electricity_price['2030']
    electricity_price = electricity_price.sort_index()
    electricity_price = electricity_price.astype(float)
    electricity_price = electricity_price.reindex(
        pd.Series(np.arange(2022, final_year + 1), name='Year').astype(str)
    ).interpolate(method='linear')
    electricity_price.index = electricity_price.index.astype(float)
    
    return capture_price, electricity_price

def load_balmorel_hydrogen_tariff(gdx_file = 'MainResults.gdx',
                                    path = 'gdxfiles',
                                    final_year = 2050,
                                    ):
    """
    Load hydrogen tariff data from Balmorel GDX files.
    Inputs:
     - gdx file to read from
     - path to the gdx file
    Outputs:
     - hydrogen tariff (Y) (dataframe)
    """
    res = MainResults(files=gdx_file, paths=path)
    # Calculate total costs and total flow for hydrogen transmission, to calculate the implied tariff in euros/MWh
    # Calculate cost
    pipeline_cost = res.get_result('ECO_XH2_YCR')
    pipeline_cost = pipeline_cost[pipeline_cost['SUBCATEGORY'].isin(['H2_TRANSMISSION_CAPITAL_COSTS', 'H2_TRANSMISSION_OPERATIONAL_COSTS'])]
    pipeline_cost = pipeline_cost.groupby(['Y']).agg({'Value':'sum'}).reset_index()
    pipeline_cost['Value'] = pipeline_cost['Value'] * 1e6 # Convert from million euros to euros
    pipeline_cost = pipeline_cost.rename(columns={'Y': 'Year', 'Value': 'Value_cost'})
    # Calculate flow
    pipeline_flow = res.get_result('XH2_FLOW_YCR')
    pipeline_flow.drop(columns=['Scenario','Country','Unit'], inplace=True)
    pipeline_flow = pipeline_flow.groupby(['Year']).agg({'Value':'sum'}).reset_index()
    pipeline_flow['Value'] = pipeline_flow['Value'] * 1e6 # Convert from TWh to MWh
    pipeline_flow = pipeline_flow.rename(columns={'Value': 'Value_flow'})
    # Merge the cost and flow dataframes to calculate the tariff
    df_pipeline = pd.merge(pipeline_cost, pipeline_flow, on=['Year'], suffixes=('_cost', '_flow'))
    df_pipeline['Value_tariff'] = (df_pipeline['Value_cost'] / df_pipeline['Value_flow']) * 33.33/1000 # Calculate the tariff in euros/kg instead of euros/MWh, using the energy content of hydrogen (33.33 kWh/kg)
    df_pipeline = df_pipeline[['Year', 'Value_tariff']]
    df_pipeline = df_pipeline.set_index('Year')['Value_tariff']
    df_pipeline['2022'] = df_pipeline['2030']
    df_pipeline = df_pipeline.sort_index()
    df_pipeline = df_pipeline.astype(float)
    df_pipeline = df_pipeline.reindex(
        pd.Series(np.arange(2022, final_year + 1), name='Year').astype(str)
    ).interpolate(method='linear')
    df_pipeline.index = df_pipeline.index.astype(float)
    return df_pipeline

def load_balmorel_electricity_tariff(gdx_file = 'MainResults.gdx',
                                    path = 'gdxfiles',
                                    final_year = 2050,
                                    ):
    """
    Load electricity tariff data from Balmorel GDX files.
    Inputs:
     - gdx file to read from
     - path to the gdx file
    Outputs:
     - electricity tariff (Y) (dataframe)
    """
    res = MainResults(files=gdx_file, paths=path)
    # Calculate total costs and total flow for electricity transmission, to calculate the implied tariff in euros/MWh
    # Calculate cost
    transmission_cost = res.get_result('ECO_X_YCR')
    transmission_cost = transmission_cost[transmission_cost['SUBCATEGORY'].isin(['TRANSMISSION_CAPITAL_COSTS', 'TRANSMISSION_OPERATIONAL_COSTS'])]
    transmission_cost = transmission_cost.groupby(['Y']).agg({'Value':'sum'}).reset_index()
    transmission_cost['Value'] = transmission_cost['Value'] * 1e6 # Convert from million euros to euros
    transmission_cost = transmission_cost.rename(columns={'Y': 'Year', 'Value': 'Value_cost'})
    # Calculate flow
    transmission_flow = res.get_result('X_FLOW_YCR')
    transmission_flow.drop(columns=['Scenario','Country','Unit'], inplace=True)
    transmission_flow = transmission_flow.groupby(['Year']).agg({'Value':'sum'}).reset_index()
    transmission_flow['Value'] = transmission_flow['Value'] * 1e6 # Convert from TWh to MWh
    transmission_flow = transmission_flow.rename(columns={'Value': 'Value_flow'})
    # Get the existing capacities to annualise the costs
    transmission_capacity = res.get_result('X_CAP_YCR')
    transmission_capacity = transmission_capacity[transmission_capacity['Category'] == 'EXOGENOUS'].reset_index()
    regions = transmission_capacity['From'].unique()
    distances = compute_balmorel_distances(path_to_coordinates='\\data\\coordinates_RRR.csv',
                                            path_to_regions='\\data\\RRR.xlsx',
                                            path_to_connections='\\data\\RRR_connections.xlsx')
    x_capex = 0.75 * 1000 *1000 # €/km/GW 1) to € from k€ 2) to GW from MW
    x_capex_distance = x_capex * distances # Capex in €/GW, multiplied by the distance in km
    annuity_factor = 0.04 / (1 - (1 + 0.04) ** -40) # Annuity factor for 40 years lifetime and 4% discount rate
    for i in range(len(transmission_capacity)):
        from_region = transmission_capacity.iloc[i]['From']
        to_region = transmission_capacity.iloc[i]['To']
        distance_capex = x_capex_distance.loc[from_region, to_region]
        try:
            transmission_capacity.at[i, 'Value'] = transmission_capacity.at[i, 'Value'] * distance_capex * 0.5 * annuity_factor # Total investment cost of existing capacity before annualisation, multiplied by 0.5 to not count both directions of the transmission line
        except KeyError:
            print(f"KeyError for regions: {from_region} to {to_region}, i={i}")
    transmission_capacity = transmission_capacity.groupby(['Year']).agg({'Value':'sum'}).reset_index()
    transmission_capacity = transmission_capacity.rename(columns={'Value': 'Value_cost'})
    transmission_cost['Value_cost'] = transmission_capacity['Value_cost'] + transmission_cost['Value_cost'] # Add the annualised existing capacity costs to the new investments and operational costs to get the total cost of transmission in each year
    # Merge the cost and flow dataframes to calculate the tariff
    df_transmission = pd.merge(transmission_cost, transmission_flow, on=['Year'], suffixes=('_cost', '_flow'))
    df_transmission['Value_tariff'] = df_transmission['Value_cost'] / df_transmission['Value_flow'] # Calculate the tariff in euros/MWh
    df_transmission = df_transmission[['Year', 'Value_tariff']]
    df_transmission = df_transmission.set_index('Year')['Value_tariff']
    df_transmission['2022'] = df_transmission['2030']
    df_transmission = df_transmission.sort_index()
    df_transmission = df_transmission.astype(float)
    df_transmission = df_transmission.reindex(
        pd.Series(np.arange(2022, final_year + 1), name='Year').astype(str)
    ).interpolate(method='linear')
    df_transmission.index = df_transmission.index.astype(float)
    return df_transmission

def load_balmorel_fullloadhours(gdx_file = 'MainResults.gdx',
                                    path = 'gdxfiles',
                                    final_year = 2050,
                                    ):
    """
    Load full load hours data from Balmorel GDX files.
    Inputs:
     - gdx file to read from
     - path to the gdx file
    Outputs:
     - full load hours (Y) (dataframe)
    """
    res = MainResults(files=gdx_file, paths=path)
    generation = res.get_result('PRO_YCRAGF')
    capacity = res.get_result('G_CAP_YCRAF')

    generation = generation[(generation['Technology'] == 'ELECTROLYZER') & (generation['Commodity'] == 'HYDROGEN')].reset_index()
    generation = generation.groupby(['Year']).agg({'Value':'sum'}).reset_index()
    capacity = capacity[(capacity['Technology'] == 'ELECTROLYZER') & (capacity['Commodity'] == 'HYDROGEN')].reset_index()
    capacity = capacity.groupby(['Year']).agg({'Value':'sum'}).reset_index()

    df_fullloadhours = pd.merge(generation, capacity, on=['Year'], suffixes=('_generation', '_capacity'))
    df_fullloadhours['Value_fullloadhours'] = (df_fullloadhours['Value_generation'] * 1000) / df_fullloadhours['Value_capacity'] # Calculate full load hours as generation divided by capacity, multiplied by the number of hours in a year
    df_fullloadhours = df_fullloadhours[['Year', 'Value_fullloadhours']]
    df_fullloadhours = df_fullloadhours.set_index('Year')['Value_fullloadhours']
    df_fullloadhours['2022'] = df_fullloadhours['2030']
    df_fullloadhours = df_fullloadhours.sort_index()
    df_fullloadhours = df_fullloadhours.astype(float)
    df_fullloadhours = df_fullloadhours.reindex(
        pd.Series(np.arange(2022, final_year + 1), name='Year').astype(str)
    ).interpolate(method='linear')
    df_fullloadhours.index = df_fullloadhours.index.astype(float)
    return df_fullloadhours

if __name__ == "__main__":
    out1,out2 = load_balmorel_electricity_prices(gdx_file='MainResults_loop4.gdx',
                                        path='C:\\GitHub\\h2_system_dynamics_paper\\gdxfiles')
    print(out2)