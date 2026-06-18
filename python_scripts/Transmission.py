# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 09:19:19 2023

@author: tmad
"""

import os
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from technology_data_loading import load_technology_data
from pybalmorel import IncFile
def balmorel_generate_transmission_data() -> None:
    ### KEY OPTIONS AND ASSUMPTIONS FOR TRANSMISSION ASSUMPTIONS ###
    ## TRANSMISSION
    land_cables = {1: 'Investment, OH lines  AC [kEUR/km/MW], 4000 MW capacity', # overhead AC lines}
                    2: 'Investment, OH lines  DC [kEUR/km/MW], 4000 MW capacity', # overhead DC cables
                    3: 'AC onshore cables [kEUR/km/MW], 500 MW capacity', # underground AC cables
                    4: 'DC onshore cables [kEUR/km/MW], 1500-2000 MW capacity'} # underground DC cables

    sea_cables = {1: 'DC offshore cables [kEUR/km/MW], 1500-2000 MW capacity', # DC cables
                2: 'AC offshore cables [kEUR/km/MW], 500 MW capacity'} # AC cables


    Fixed_OM_OH = "Fixed O&M [% of capex  per year]"
    Fixed_OM_UG = "Fixed O&M [% of capex per year]"

    land_cable = 1 # Assuming overhead AC lines for land connections
    sea_cable = 1 # Assuming DC cables for sea connections

    if land_cable == 1 or land_cable == 2:
        land_cable_key = "111 6 el trans OH " # overhead AC and DC lines
    else:
        land_cable_key = "111 7 el trans AC&DC cables" # underground AC and DC cables
    subsea_cable_key = "111 7 el trans AC&DC cables" # underground AC and DC cables, onshore and offshore

    # Assumed loss factor from https://doi.org/10.1016/j.apenergy.2022.118859
    loss_factor_AC = (5/100)/1000 # 5% losses per 1000 km for AC lines -> 0.005% per km
    loss_factor_DC = (3/100)/1000 # 3% losses per 1000 km for DC lines -> 0.003% per km

    if land_cable == 1 or land_cable == 3:
        land_loss_factor = loss_factor_AC
    else:
        land_loss_factor = loss_factor_DC

    sea_loss_factor = loss_factor_DC

    load_factor = 0.5 # average load factor for transmission lines

    ## HYDROGEN
    hydrogen_pipe_key = "H2 70" # 70 bar hydrogen pipeline --- NOTE: in the current build, we don't extract investment cost, but use the numbers from Ioannis' paper (A Unified...).


    ## GENERAL
    rerouting_factor = 1.3 # factor to account for rerouting of lines due to terrain, urban areas, etc.
    years = [2030, 2040, 2050] # years for which to extract costs and write data --- NOTE: in the current build, only these 3 years are supported for data extraction.

    print("----- TRANSMISSION ASSUMPTIONS -----")
    print("Selected land cable type:", land_cables[land_cable])
    print("Selected sea cable type:", sea_cables[sea_cable])
    print("Rerouting factor for distances:", rerouting_factor)
    print("Average load factor for transmission lines:", load_factor)
    print("Years for cost data extraction:", years)
    print("-----------------------------------")

    ### PREPARE DISTANCE MATRIX BETWEEN REGIONS ###

    # get current working directory
    cwd = os.getcwd()

    # load regions and coordinates for regions
    coordinates = pd.read_csv(cwd + '\\data\\coordinates_RRR.csv')
    regions = pd.read_excel(cwd + '\\data\\RRR.xlsx')
    # make sure RRR columns are strings and strip any whitespace
    regions['RRR'] = regions['RRR'].astype(str).str.strip()
    coordinates['RRR'] = coordinates['RRR'].astype(str).str.strip()
    # merge regions with coordinates on RRR column
    regions = regions.merge(coordinates, on="RRR")
    labels = regions['RRR'].tolist()
    # Prepare a list of tuples with (latitude, longitude) for each region
    region_coords = [(row['Lat'], row['Lon']) for _, row in regions.iterrows()]

    # Calculate distances between regions using coordinates
    s = len(regions)
    distances = np.zeros((s, s))
    for i in range(s):
        for j in range(s):
            distances[i, j] = geodesic(region_coords[i], region_coords[j]).km * rerouting_factor
    df_dist = pd.DataFrame(distances, index=labels, columns=labels)

    ### LOAD COST ASSUMPTIONS FOR NEW TRANSMISSION ###

    # Load prices for transmission cost calculation
    data = load_technology_data()

    energy_transport = data.get('energy_transport_datasheet.xlsx')

    land_cable_data = energy_transport[energy_transport['ws'] == land_cable_key]
    subsea_cable_data = energy_transport[energy_transport['ws'] == subsea_cable_key]
    hydrogen_data = energy_transport[energy_transport['ws'] == hydrogen_pipe_key]


    land_cable_investment_cost = land_cable_data[(land_cable_data['par'] == land_cables[land_cable]) & (land_cable_data['est'] == 'ctrl')].loc[:, ['year','val']] #          kEUR/km/MW
    land_cable_investment_cost.set_index('year', inplace=True)
    land_cable_investment_cost = land_cable_investment_cost[land_cable_investment_cost.index.isin(years)]
    subsea_cable_investment_cost = subsea_cable_data[(subsea_cable_data['par'] == sea_cables[sea_cable]) & (subsea_cable_data['est'] == 'ctrl')].loc[:, ['year','val']] #    kEUR/km/MW
    subsea_cable_investment_cost.set_index('year', inplace=True)
    subsea_cable_investment_cost = subsea_cable_investment_cost[subsea_cable_investment_cost.index.isin(years)]
    land_cable_fixed_om = land_cable_data[(land_cable_data['par'] == Fixed_OM_OH) & (land_cable_data['est'] == 'ctrl')].loc[:, ['val']].mean() #                             % of capex/year
    subsea_cable_fixed_om = subsea_cable_data[(subsea_cable_data['par'] == Fixed_OM_UG) & (subsea_cable_data['est'] == 'ctrl')].loc[:, ['val']].mean() #                     % of capex/year
    # hydrogen_investment_cost = hydrogen_data[(hydrogen_data['par'] == 'Investment costs; single line, 1000-4000 MW [€/MW/m]') & (hydrogen_data['est'] == 'ctrl')].loc[:, ['year','val']] # EUR/MW/km
    # hydrogen_investment_cost.set_index('year', inplace=True)
    # hydrogen_investment_cost = hydrogen_investment_cost[hydrogen_investment_cost.index.isin(years)]
    land_pipeline_investment_cost = np.array([[2030, 536.17], [2040, 263.08], [2050, 263.08]]) # EUR/MW/km, from Ioannis' paper (A Unified...)
    sea_pipeline_investment_cost = np.array([[2030, 902.13], [2040, 450.77], [2050, 450.77]]) # EUR/MW/km, from Ioannis' paper (A Unified...)
    pipeline_fixed_om = hydrogen_data[(hydrogen_data['par'] == 'Fixed O&M [€/km/year/MW]') & (hydrogen_data['est'] == 'ctrl') & (hydrogen_data['year'] == 2030)].loc[:, ['val']] # EUR/km/MW/year

    ### CALCULATE TRANSMISSION COSTS ###
    land_connections = pd.read_excel(cwd + '\\data\\RRR_connections.xlsx', sheet_name='land connections')
    sea_connections = pd.read_excel(cwd + '\\data\\RRR_connections.xlsx', sheet_name='subsea connections')

    land_connections.set_index(land_connections.columns[0], inplace=True)
    land_connections.index.name = None

    sea_connections.set_index(sea_connections.columns[0], inplace=True)
    sea_connections.index.name = None

    all_connections = land_connections.add(sea_connections, fill_value=0)
    all_connections.fillna(0, inplace=True) # fill NaN values with 0 for connections that do not exist

    ### CALCULATE INVESTMENT COSTS ###
    x_investment = pd.DataFrame()
    xh2_investment = pd.DataFrame()
    for year in years:
        x_investment_year = pd.DataFrame(0, index=df_dist.index, columns=df_dist.columns)
        xh2_investment_year = pd.DataFrame(0, index=df_dist.index, columns=df_dist.columns)
        x_investment_year_land = df_dist * land_connections * land_cable_investment_cost.loc[year, 'val'] * 1000 # convert kEUR to EUR
        x_investment_year_sea = df_dist * sea_connections * subsea_cable_investment_cost.loc[year, 'val'] * 1000 # convert kEUR to EUR
        xh2_investment_year_land = df_dist * land_connections * land_pipeline_investment_cost[land_pipeline_investment_cost[:,0] == year, 1][0] # EUR/MW/km
        xh2_investment_year_sea = df_dist * sea_connections * sea_pipeline_investment_cost[sea_pipeline_investment_cost[:,0] == year, 1][0] # EUR/MW/km
        x_investment_year = x_investment_year_land.add(x_investment_year_sea, fill_value=0)
        x_investment_year.index = str(year) + '.' + x_investment_year.index
        x_investment = pd.concat([x_investment, x_investment_year])
        xh2_investment_year = xh2_investment_year_land.add(xh2_investment_year_sea, fill_value=0)
        xh2_investment_year.index = str(year) + '.' + xh2_investment_year.index
        xh2_investment = pd.concat([xh2_investment, xh2_investment_year])
    x_investment.fillna('', inplace=True)
    xh2_investment.fillna('', inplace=True)

    ### CALCULATE FIXED O&M COSTS ###
    x_land_avg_OM_cost = ((land_cable_fixed_om / 100) * land_cable_investment_cost.loc[2040,'val'] * 1000) / (8760*load_factor) # 1) O&M as percentage of capex 2) convert kEUR to EUR 3) convert to MWh cost from MW assuming  load factor
    x_subsea_avg_OM_cost = ((subsea_cable_fixed_om / 100) * subsea_cable_investment_cost.loc[2040,'val'] * 1000) / (8760*load_factor) # 1) O&M as percentage of capex 2) convert kEUR to EUR 3) convert to MWh cost from MW assuming  load factor

    x_fixed_OM_land = df_dist * land_connections * x_land_avg_OM_cost.iloc[0]
    x_fixed_OM_sea = df_dist * sea_connections * x_subsea_avg_OM_cost.iloc[0]
    x_fixed_OM = x_fixed_OM_land.add(x_fixed_OM_sea, fill_value=0)
    x_fixed_OM.fillna('', inplace=True) # fill NaN values with 0 for connections that do not exist

    xh2_fixed_OM = df_dist * all_connections * pipeline_fixed_om.iloc[0,0] / (8760*load_factor) # 1) EUR/MW/km/year converted to EUR/MW/year using distances 2) converting to EUR/MWh using load factor and hours per year
    xh2_fixed_OM.fillna(0, inplace=True) # fill NaN values with 0 for connections that do not exist

    ### CALCULATE LOSSES ###
    x_losses_land = df_dist * land_connections * land_loss_factor
    x_losses_sea = df_dist * sea_connections * sea_loss_factor
    x_losses = x_losses_land.add(x_losses_sea, fill_value=0)
    x_losses.fillna('', inplace=True) # fill NaN values with 0 for connections that do not exist

    ### WRITE TO INC FILE
    filename = "XCOST"
    incfile = IncFile(name=filename,
                    prefix="TABLE XCOST(IRRRE,IRRRI)   'Transmission cost between regions (EUR/MWh)'\n",
                    suffix="\n;\n",
                    path=cwd + '\\incfiles_transmission\\')
    incfile.body = pd.DataFrame(index=x_fixed_OM.index,
                                columns=x_fixed_OM.columns,
                            data=x_fixed_OM.values)
    incfile.save()

    filename = "XINVCOST"
    incfile = IncFile(name=filename,
                    prefix="TABLE XINVCOST(YYY,IRRRE,IRRRI)  'Investment cost in new transmission capacity (Money/MW)'\n",
                    suffix="\n;\n",
                    path=cwd + '\\incfiles_transmission\\')
    incfile.body = pd.DataFrame(index=x_investment.index,
                                columns=x_investment.columns,
                            data=x_investment.values)
    incfile.save()

    filename = "XLOSS"
    incfile = IncFile(name=filename,
                        prefix="TABLE XLOSS(IRRRE,IRRRI)   'Transmission loss between regions (fraction)'\n",
                        suffix="\n;\n",
                        path=cwd + '\\incfiles_transmission\\')
    incfile.body = pd.DataFrame(index=x_losses.index,
                                columns=x_losses.columns,
                            data=x_losses.values)
    incfile.save()

    filename = "HYDROGEN_XH2COST"
    incfile = IncFile(name=filename,
                        prefix="TABLE XH2COST(IRRRE,IRRRI)  'H2 transmission cost between regions (calculated from exported quantity) (Money/MWh)'\n",
                        suffix="\n;\n",
                        path=cwd + '\\incfiles_transmission\\')
    incfile.body = pd.DataFrame(index=xh2_fixed_OM.index,
                                columns=xh2_fixed_OM.columns,
                                data=xh2_fixed_OM.values)
    incfile.save()

    filename = "HYDROGEN_XH2INVCOST"
    incfile = IncFile(name=filename,
                        prefix="TABLE XH2INVCOST(YYY,IRRRE,IRRRI)  'Investment cost in new H2 transmission capacity (Money/MW)'\n",
                        suffix="\n;\n",
                        path=cwd + '\\incfiles_transmission\\')
    incfile.body = pd.DataFrame(index=xh2_investment.index,
                                columns=xh2_investment.columns,
                                data=xh2_investment.values)
    incfile.save()

if __name__ == "__main__":
    balmorel_generate_transmission_data()