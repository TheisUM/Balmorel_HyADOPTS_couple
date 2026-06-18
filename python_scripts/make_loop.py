import numpy as np
import pandas as pd
import pysd
import os
from time import time
from pybalmorel import IncFile, MainResults

# from compute_balmorel_distances import compute_balmorel_distances
import python_scripts.write_functions as sd_write
import python_scripts.balmorel_loading as bal_load

def make_loop(gdx_file = 'MainResults_Ex1.gdx',
              in_path = 'gdxfiles',
              model = pd.DataFrame,
              final_year = 2050,
              model_years = [2030, 2040, 2050],
              out_path = 'incfiles/loop1',
              distribution_key = pd.DataFrame,
              electricity_demand = pd.DataFrame,
              hydrogen_data = pd.DataFrame,
              electricity_tariff = 14.36,
              hydrogen_tariff = 25,
              time_step = 0.25,
              ):
    """
    Perform a loop iteration for the H2Sim model.
    Inputs:
    - vensim_model.mdl : Vensim model file representing the H2Sim model.
    - capture_price : Series with the electricity price seen by the electrolyzers (from Balmorel).
    - electricity_price : Series with the average electricity price in the system (from Balmorel).
    - final_year : The final year to run the model until.
    - model_years : List of years to use in Balmorel.
    - path : Path to save the include files for Balmorel.
    - distribution_key : Dataframe with the distribution key for demand distribution.
    - electricity_demand : Dataframe with the electricity demand.
    - hydrogen_data : Dataframe with the hydrogen data.
    Outputs:
    - SD_results     : Results file from the H2Sim model.
    - data.inc       : Results from the H2Sim model in include format for Balmorel.
    """

    capture_price, electricity_price = bal_load.load_balmorel_electricity_prices(gdx_file = gdx_file,
                                                                          path=in_path,
                                                                           )
    hydrogen_tariff = bal_load.load_balmorel_hydrogen_tariff(gdx_file = gdx_file,
                                                                          path=in_path,
                                                                            )
    electricity_tariff = bal_load.load_balmorel_electricity_tariff(gdx_file = gdx_file,
                                                                          path=in_path,
                                                                            )
    electrolyser_fullloadhours = bal_load.load_balmorel_fullloadhours(gdx_file = gdx_file,
                                                                          path=in_path,
                                                                            )
    capture_price = capture_price + electricity_tariff # Adding electricity tariff to the electrolyzer electricity price
    electricity_price = electricity_price + electricity_tariff # Adding electricity tariff to the average electricity price in the system

    new_model = model.copy()
    new_model.set_components({"RENEWABLE ELECTRICITY PRICE": capture_price})
    new_model.set_components({"GRID ELECTRICITY PRICE": electricity_price})
    new_model.set_components({"Green H2 tariff": hydrogen_tariff})
    new_model.set_components({"electrolyser operating hours": electrolyser_fullloadhours})
    final_year = final_year
    new_model_results = new_model.run(final_time=final_year, time_step=time_step) # Run from 2022 to 2050
    path = out_path
    print("Checkpoint 1: Model has run")
    sd_write.write_fuel_demand(model_results=new_model_results,
                                        distribution_keys=distribution_key,
                                        model_years=model_years,
                                        filename="SOSIBUBOUND",
                                        sub_path=path
                                        )
    sd_write.write_hydrogen_demand(model_results=new_model_results,
                                        distribution_keys=distribution_key,
                                        model_years=model_years,
                                        sub_path=path
                                        )
    sd_write.write_electricity_demand(model_results=new_model_results,
                                            distribution_keys=distribution_key,
                                            electricity_demand=electricity_demand,
                                            model_years=model_years,
                                            sub_path=path
                                            )
    sd_write.write_electrolyzer_capex(model_results=new_model_results,
                                                        hydrogen_data=hydrogen_data,
                                                        model_years=model_years,
                                                        sub_path=path
                                                        )
    sd_write.write_hydrogen_production(model_results=new_model_results,
                                                        distribution_keys=distribution_key,
                                                        model_years=model_years,
                                                        sub_path=path
                                                        )
    return new_model_results, new_model

if __name__ == "__main__":
    gdx_file = 'MainResults_mandate3.gdx'
    in_path = 'gdxfiles'
    capture_price, electricity_price = bal_load.load_balmorel_electricity_prices(gdx_file = gdx_file,
                                                                          path=in_path,
                                                                           )
    hydrogen_tariff = bal_load.load_balmorel_hydrogen_tariff(gdx_file = gdx_file,
                                                                          path=in_path,
                                                                            )
    electricity_tariff = bal_load.load_balmorel_electricity_tariff(gdx_file = gdx_file,
                                                                          path=in_path,
                                                                            )
    electrolyser_fullloadhours = bal_load.load_balmorel_fullloadhours(gdx_file = gdx_file,
                                                                          path=in_path,
                                                                            )
    capture_price = capture_price + electricity_tariff # Adding electricity tariff to the electrolyzer electricity price
    electricity_price = electricity_price + electricity_tariff # Adding electricity tariff to the average electricity price in the system
    print("Capture price:")
    print(capture_price.loc[[2025, 2030, 2040, 2050]])
    print("Electricity price:")
    print(electricity_price.loc[[2025, 2030, 2040, 2050]])
    print("Fullload hours:")
    print(electrolyser_fullloadhours.loc[[2025, 2030, 2040, 2050]])