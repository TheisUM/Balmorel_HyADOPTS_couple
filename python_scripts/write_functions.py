import pandas as pd
import seaborn as sns
import numpy as np
import os
import pysd
import pybalmorel
from pybalmorel import IncFile
from python_scripts.result_loading import result_loading_class
from python_scripts.data_loading import data_loading_class
# import write_functions as sd_write

rl = result_loading_class()
dl = data_loading_class()

def load_sectoral_production(model_results: pd.DataFrame):
    """
    Load production results from the SD model output.
    This function reads the SD model output and returns a dictionary with DataFrames with the production data.
    """
    sectoral_production = {}

    for main_sector in rl.sector_dict.keys():
        for i, (sub_sector, sub_dict) in enumerate(rl.sector_dict[main_sector].items()):
            if sub_dict["unit"] == "GWh":
                unit = "TWh"
                df = model_results[sub_dict["stocks"]] / 1000
            else:
                unit = sub_dict["unit"]
                df = model_results[sub_dict["stocks"]]
            df.index = model_results.index
            df.columns = list(map(lambda x: rl.pretty_names_technologies[x], df.columns ))
            sectoral_production[sub_sector] = df

    return sectoral_production

def write_fuel_demand(model_results:pd.DataFrame,
                      distribution_keys: pd.DataFrame,
                      model_years:list = [2030, 2040, 2050],
                      filename:str = "",
                      sub_path: str = "",
                      ):
    """
    Write fuel demand results to an IncFile. This fuction takes the model results from a SD run and writes them to the SOSIBUBOUND.inc or MINFLOW.inc file.
    
    Possible filenames are:
    - SOSIBUBOUND
    - MINFLOW

    Returns:
    - IncFile with the regional fuel demand results for the chosen years.
    """

    # Step 1: Read the model results DataFrame and extract the relevant columns
    results = load_sectoral_production(model_results=model_results)

    # Step 2: Read the data required for the IncFile
    distribution_keys = distribution_keys
    
    # 1) Ammonia
    Fertilizer = results["fertilizer"]
    Shipping_international = results["international shipping"]

    Fertilizer = Fertilizer.sum(axis=1) # MtNH3
    Fertilizer = Fertilizer * 18.6 / 3.6
    Shipping_ammonia = Shipping_international.iloc[:,1]

    Fertilizer = pd.DataFrame(Fertilizer.values[:, None] * distribution_keys["Fertilizer"].values[None, :],
                                       index=Fertilizer.index,
                                       columns=distribution_keys["Fertilizer"].index)

    Shipping_ammonia = pd.DataFrame(Shipping_ammonia.values[:, None] * distribution_keys["International shipping"].values[None, :],
                                       index=Shipping_ammonia.index,
                                       columns=distribution_keys["International shipping"].index)
    Total_ammonia = Fertilizer + Shipping_ammonia

    # 2) Methanol
    Shipping_international_biomeoh = Shipping_international.iloc[:,2]
    Shipping_domestic = results["domestic shipping"]
    Shipping_domestic_biomeoh = Shipping_domestic.iloc[:,2]

    Shipping_international_biomeoh = pd.DataFrame(Shipping_international_biomeoh.values[:, None] * distribution_keys["International shipping"].values[None, :],
                                       index=Shipping_international_biomeoh.index,
                                       columns=distribution_keys["International shipping"].index)
    Shipping_domestic_biomeoh = pd.DataFrame(Shipping_domestic_biomeoh.values[:, None] * distribution_keys["Domestic shipping"].values[None, :],
                                       index=Shipping_domestic_biomeoh.index,
                                       columns=distribution_keys["Domestic shipping"].index)
    Shipping_biomeoh = Shipping_international_biomeoh + Shipping_domestic_biomeoh
    #Methanol = results["MeOH"]
    Total_bioMeOH = Shipping_biomeoh

    # 3) Kerosene
    Aviation_international = results["international aviation"]
    Aviation_international_bio_kerosene = Aviation_international.iloc[:,2]
    Aviation_domestic = results["domestic aviation"]
    Aviation_domestic_bio_kerosene = Aviation_domestic.iloc[:,2]
    Aviation_international_bio_kerosene = pd.DataFrame(Aviation_international_bio_kerosene.values[:, None] * distribution_keys["International aviation"].values[None, :],
                                       index=Aviation_international_bio_kerosene.index,
                                       columns=distribution_keys["International aviation"].index)
    Aviation_domestic_bio_kerosene = pd.DataFrame(Aviation_domestic_bio_kerosene.values[:, None] * distribution_keys["Domestic aviation"].values[None, :],
                                       index=Aviation_domestic_bio_kerosene.index,
                                       columns=distribution_keys["Domestic aviation"].index)
    Aviation_international_e_kerosene = Aviation_international.iloc[:,1]
    Aviation_domestic_e_kerosene = Aviation_domestic.iloc[:,1]
    Aviation_international_e_kerosene = pd.DataFrame(Aviation_international_e_kerosene.values[:, None] * distribution_keys["International aviation"].values[None, :],
                                       index=Aviation_international_e_kerosene.index,
                                       columns=distribution_keys["International aviation"].index)
    Aviation_domestic_e_kerosene = pd.DataFrame(Aviation_domestic_e_kerosene.values[:, None] * distribution_keys["Domestic aviation"].values[None, :],
                                       index=Aviation_domestic_e_kerosene.index,
                                       columns=distribution_keys["Domestic aviation"].index)
    Aviation_international_fossil_kerosene = Aviation_international.iloc[:,0]
    Aviation_domestic_fossil_kerosene = Aviation_domestic.iloc[:,0]
    Aviation_international_fossil_kerosene = pd.DataFrame(Aviation_international_fossil_kerosene.values[:, None] * distribution_keys["International aviation"].values[None, :],
                                       index=Aviation_international_fossil_kerosene.index,
                                       columns=distribution_keys["International aviation"].index)
    Aviation_domestic_fossil_kerosene = pd.DataFrame(Aviation_domestic_fossil_kerosene.values[:, None] * distribution_keys["Domestic aviation"].values[None, :],
                                       index=Aviation_domestic_fossil_kerosene.index,
                                       columns=distribution_keys["Domestic aviation"].index)
    Total_bio_kerosene = Aviation_international_bio_kerosene + Aviation_domestic_bio_kerosene
    Total_e_kerosene = Aviation_international_e_kerosene + Aviation_domestic_e_kerosene
    Total_fossil_kerosene = Aviation_international_fossil_kerosene + Aviation_domestic_fossil_kerosene

    # 4) Heavy fuel oil
    Shipping_international_HFO = Shipping_international.iloc[:,0]
    Shipping_domestic_HFO = Shipping_domestic.iloc[:,0]
    Shipping_international_HFO = pd.DataFrame(Shipping_international_HFO.values[:, None] * distribution_keys["International shipping"].values[None, :],
                                       index=Shipping_international_HFO.index,
                                       columns=distribution_keys["International shipping"].index)
    Shipping_domestic_HFO = pd.DataFrame(Shipping_domestic_HFO.values[:, None] * distribution_keys["Domestic shipping"].values[None, :],
                                       index=Shipping_domestic_HFO.index,
                                       columns=distribution_keys["Domestic shipping"].index)
    Total_HFO = Shipping_international_HFO + Shipping_domestic_HFO
    
    
    # 5) Naphtha
    Chemicals = results["naphtha"]
    Chemicals = Chemicals * 13.44
    # print(Chemicals.iloc[-1,0])

    Total_synthetic_naphtha = Chemicals.iloc[:,1]
    Total_bio_naphtha = Chemicals.iloc[:,2]
    Total_fossil_naphtha = Chemicals.iloc[:,0]
    Total_synthetic_naphtha = pd.DataFrame(Total_synthetic_naphtha.values[:, None] * distribution_keys["High value chemicals"].values[None, :],
                                       index=Total_synthetic_naphtha.index,
                                       columns=distribution_keys["High value chemicals"].index)
    Total_bio_naphtha = pd.DataFrame(Total_bio_naphtha.values[:, None] * distribution_keys["High value chemicals"].values[None, :],
                                       index=Total_bio_naphtha.index,
                                       columns=distribution_keys["High value chemicals"].index)
    Total_fossil_naphtha = pd.DataFrame(Total_fossil_naphtha.values[:, None] * distribution_keys["High value chemicals"].values[None, :],
                                       index=Total_fossil_naphtha.index,
                                       columns=distribution_keys["High value chemicals"].index)
    

    # 6) Diesel
    diesel_light_duty = results["light duty"]
    diesel_heavy_duty = results["heavy duty"]
    diesel_light_duty = diesel_light_duty.iloc[:, 0]
    diesel_heavy_duty = diesel_heavy_duty.iloc[:, 0]
    diesel_light_duty = pd.DataFrame(diesel_light_duty.values[:, None] * distribution_keys["Road transport"].values[None, :],
                                       index=diesel_light_duty.index,
                                       columns=distribution_keys["Road transport"].index)
    diesel_heavy_duty = pd.DataFrame(diesel_heavy_duty.values[:, None] * distribution_keys["Road transport"].values[None, :],
                                       index=diesel_heavy_duty.index,
                                       columns=distribution_keys["Road transport"].index)
    Total_diesel = diesel_light_duty + diesel_heavy_duty

    # 7) Steel
    steel = results["steel"]
    Total_steel_BF = steel.iloc[:,0] * 1e6 # Convert to ton
    Total_steel_BFCCS = steel.iloc[:,1] * 1e6 # Convert to ton
    Total_steel_NGDRI = steel.iloc[:,2] * 1e6 # Convert to ton
    Total_steel_H2DRI = steel.iloc[:,3] * 1e6 # Convert to ton
    Total_steel_BF = pd.DataFrame(Total_steel_BF.values[:, None] * distribution_keys["Steel"].values[None, :],
                            index= Total_steel_BF.index,
                            columns=distribution_keys["Steel"].index)
    Total_steel_BFCCS = pd.DataFrame(Total_steel_BFCCS.values[:, None] * distribution_keys["Steel"].values[None, :],
                                index=Total_steel_BFCCS.index,
                                columns=distribution_keys["Steel"].index)
    Total_steel_NGDRI = pd.DataFrame(Total_steel_NGDRI.values[:, None] * distribution_keys["Steel"].values[None, :],
                                index=Total_steel_NGDRI.index,
                                columns=distribution_keys["Steel"].index)
    Total_steel_H2DRI = pd.DataFrame(Total_steel_H2DRI.values[:, None] * distribution_keys["Steel"].values[None, :],
                                index=Total_steel_H2DRI.index,
                                columns=distribution_keys["Steel"].index)

    # Step 4: Prepare the data for the IncFile
    Total_ammonia = Total_ammonia.loc[model_years]
    Total_bioMeOH = Total_bioMeOH.loc[model_years]
    Total_bio_kerosene = Total_bio_kerosene.loc[model_years]
    Total_e_kerosene = Total_e_kerosene.loc[model_years]
    Total_fossil_kerosene = Total_fossil_kerosene.loc[model_years]
    Total_HFO = Total_HFO.loc[model_years]
    Total_synthetic_naphtha = Total_synthetic_naphtha.loc[model_years]
    Total_bio_naphtha = Total_bio_naphtha.loc[model_years]
    Total_fossil_naphtha = Total_fossil_naphtha.loc[model_years]
    Total_diesel = Total_diesel.loc[model_years]
    Total_steel_BF = Total_steel_BF.loc[model_years]
    Total_steel_BFCCS = Total_steel_BFCCS.loc[model_years]
    Total_steel_NGDRI = Total_steel_NGDRI.loc[model_years]
    Total_steel_H2DRI = Total_steel_H2DRI.loc[model_years]

    Total_ammonia.index = Total_ammonia.index.astype(str)
    Total_bioMeOH.index = Total_bioMeOH.index.astype(str)
    Total_bio_kerosene.index = Total_bio_kerosene.index.astype(str)
    Total_e_kerosene.index = Total_e_kerosene.index.astype(str)
    Total_fossil_kerosene.index = Total_fossil_kerosene.index.astype(str)
    Total_HFO.index = Total_HFO.index.astype(str)
    Total_synthetic_naphtha.index = Total_synthetic_naphtha.index.astype(str)
    Total_bio_naphtha.index = Total_bio_naphtha.index.astype(str)
    Total_fossil_naphtha.index = Total_fossil_naphtha.index.astype(str)
    Total_diesel.index = Total_diesel.index.astype(str)
    Total_steel_BF.index = Total_steel_BF.index.astype(str)
    Total_steel_BFCCS.index = Total_steel_BFCCS.index.astype(str)
    Total_steel_NGDRI.index = Total_steel_NGDRI.index.astype(str)
    Total_steel_H2DRI.index = Total_steel_H2DRI.index.astype(str)

    Total_ammonia.index = [idx.replace('.0', '') for idx in Total_ammonia.index]
    Total_bioMeOH.index = [idx.replace('.0', '') for idx in Total_bioMeOH.index]
    Total_bio_kerosene.index = [idx.replace('.0', '') for idx in Total_bio_kerosene.index]
    Total_e_kerosene.index = [idx.replace('.0', '') for idx in Total_e_kerosene.index]
    Total_fossil_kerosene.index = [idx.replace('.0', '') for idx in Total_fossil_kerosene.index]
    Total_HFO.index = [idx.replace('.0', '') for idx in Total_HFO.index]
    Total_synthetic_naphtha.index = [idx.replace('.0', '') for idx in Total_synthetic_naphtha.index]
    Total_bio_naphtha.index = [idx.replace('.0', '') for idx in Total_bio_naphtha.index]
    Total_fossil_naphtha.index = [idx.replace('.0', '') for idx in Total_fossil_naphtha.index]
    Total_diesel.index = [idx.replace('.0', '') for idx in Total_diesel.index]
    Total_steel_BF.index = [idx.replace('.0', '') for idx in Total_steel_BF.index]
    Total_steel_BFCCS.index = [idx.replace('.0', '') for idx in Total_steel_BFCCS.index]
    Total_steel_NGDRI.index = [idx.replace('.0', '') for idx in Total_steel_NGDRI.index]
    Total_steel_H2DRI.index = [idx.replace('.0', '') for idx in Total_steel_H2DRI.index]

    if filename == "SOSIBUBOUND":
        filename = "OPTIFLOW_SOSIBUBOUND"

        ammonia_suffix =        " . AmmoniaBuffer       . AMMONIA_FLOW       . ILOUPFX_LO "
        biomeoh_suffix =        " . MethanolBuffer      . METHANOLFLOW       . ILOUPFX_LO "
        biokero_suffix =        " . BioJetBuffer        . BIOJETFLOW         . ILOUPFX_LO "
        ekero_suffix =          " . E_FT_JetBuffer      . E_FT_JET_FLOW      . ILOUPFX_LO "
        fosskero_suffix =       " . KeroseneBuffer      . KEROSENEFLOW       . ILOUPFX_LO "
        HFO_suffix =            " . HFOBuffer           . HFOFLOW            . ILOUPFX_LO "
        synnaphtha_suffix =     " . E_FT_NaphthaBuffer  . E_FT_NAPHTHA_FLOW  . ILOUPFX_LO "
        bionaphtha_suffix =     " . BioNaphthaBuffer    . BIONAPHTHAFLOW     . ILOUPFX_LO "
        fossnaphtha_suffix =    " . NaphthaBuffer       . NAPHTHAFLOW        . ILOUPFX_LO "
        diesel_suffix =         " . DieselBuffer        . DIESELFLOW         . ILOUPFX_LO "
        steel_BF_suffix =       " . Steel_BFBuffer      . STEEL_FLOW         . ILOUPFX_LO "
        steel_BFCCS_suffix =    " . Steel_BFCCSBuffer   . STEEL_FLOW         . ILOUPFX_LO "
        steel_NGDRI_suffix =    " . Steel_NGDRIBuffer   . STEEL_FLOW         . ILOUPFX_LO "
        steel_H2DRI_suffix =    " . Steel_H2DRIBuffer   . STEEL_FLOW         . ILOUPFX_LO "

        Total_ammonia.index = [f"{year}{ammonia_suffix}" for year in Total_ammonia.index]
        Total_bioMeOH.index = [f"{year}{biomeoh_suffix}" for year in Total_bioMeOH.index]
        Total_bio_kerosene.index = [f"{year}{biokero_suffix}" for year in Total_bio_kerosene.index]
        Total_e_kerosene.index = [f"{year}{ekero_suffix}" for year in Total_e_kerosene.index]
        Total_fossil_kerosene.index = [f"{year}{fosskero_suffix}" for year in Total_fossil_kerosene.index]
        Total_HFO.index = [f"{year}{HFO_suffix}" for year in Total_HFO.index]
        Total_synthetic_naphtha.index = [f"{year}{synnaphtha_suffix}" for year in Total_synthetic_naphtha.index]
        Total_bio_naphtha.index = [f"{year}{bionaphtha_suffix}" for year in Total_bio_naphtha.index]
        Total_fossil_naphtha.index = [f"{year}{fossnaphtha_suffix}" for year in Total_fossil_naphtha.index]
        Total_diesel.index = [f"{year}{diesel_suffix}" for year in Total_diesel.index]
        Total_steel_BF.index = [f"{year}{steel_BF_suffix}" for year in Total_steel_BF.index]
        Total_steel_BFCCS.index = [f"{year}{steel_BFCCS_suffix}" for year in Total_steel_BFCCS.index]
        Total_steel_NGDRI.index = [f"{year}{steel_NGDRI_suffix}" for year in Total_steel_NGDRI.index]
        Total_steel_H2DRI.index = [f"{year}{steel_H2DRI_suffix}" for year in Total_steel_H2DRI.index]

        Total_fuel_demand = pd.concat([Total_ammonia, Total_bioMeOH, Total_bio_kerosene, Total_e_kerosene, Total_fossil_kerosene, Total_HFO,
                                    Total_synthetic_naphtha, Total_bio_naphtha, Total_fossil_naphtha, Total_diesel])
        Total_fuel_demand = Total_fuel_demand * 1e6  # Convert MWh
        Total_steel = pd.concat([Total_steel_BF, Total_steel_BFCCS, Total_steel_NGDRI, Total_steel_H2DRI])
        Total_demand = pd.concat([Total_fuel_demand, Total_steel])

        # Step 4: Write the results to the IncFile

        filename = "OPTIFLOW_SOSIBUBOUND"
        incfile = IncFile(name = filename,
                        prefix="TABLE SOSIBUBOUND1(YYY,PROC,FLOW,iLOUPFXSET,AAA) 'Bounds on Source, Sink and Buffer Process Flows - for each year'\n",
                        suffix="\n;\nSOSIBUBOUND(YYY,AAA,PROC,FLOW,iLOUPFXSET)$(AAAOPTIFLOW(AAA)) = SOSIBUBOUND1(YYY,PROC,FLOW,iLOUPFXSET,AAA);",
                        path="incfiles" + sub_path)
        
        incfile.body = pd.DataFrame(index=Total_demand.index,
                                    columns=Total_demand.columns,
                                    data=Total_demand.values)

        incfile.save()

    elif filename == "MINFLOW":
        filename = "OPTIFLOW_MINFLOW"

        ammonia_suffix =        " . AmmoniaBuffer       . AMMONIA_FLOW       "
        biomeoh_suffix =        " . MethanolBuffer      . METHANOLFLOW       "
        biokero_suffix =        " . BioJetBuffer        . BIOJETFLOW         "
        ekero_suffix =          " . E_FT_JetBuffer      . E_FT_JET_FLOW      "
        fosskero_suffix =       " . KeroseneBuffer      . KEROSENEFLOW       "
        HFO_suffix =            " . HFOBuffer           . HFOFLOW            "
        synnaphtha_suffix =     " . E_FT_NaphthaBuffer  . E_FT_NAPHTHA_FLOW  "
        bionaphtha_suffix =     " . BioNaphthaBuffer    . BIONAPHTHAFLOW     "
        fossnaphtha_suffix =    " . NaphthaBuffer       . NAPHTHAFLOW        "
        diesel_suffix =         " . DieselBuffer        . DIESELFLOW         "

        Total_ammonia.index = [f"{year}{ammonia_suffix}" for year in Total_ammonia.index]
        Total_bioMeOH.index = [f"{year}{biomeoh_suffix}" for year in Total_bioMeOH.index]
        Total_bio_kerosene.index = [f"{year}{biokero_suffix}" for year in Total_bio_kerosene.index]
        Total_e_kerosene.index = [f"{year}{ekero_suffix}" for year in Total_e_kerosene.index]
        Total_fossil_kerosene.index = [f"{year}{fosskero_suffix}" for year in Total_fossil_kerosene.index]
        Total_HFO.index = [f"{year}{HFO_suffix}" for year in Total_HFO.index]
        Total_synthetic_naphtha.index = [f"{year}{synnaphtha_suffix}" for year in Total_synthetic_naphtha.index]
        Total_bio_naphtha.index = [f"{year}{bionaphtha_suffix}" for year in Total_bio_naphtha.index]
        Total_fossil_naphtha.index = [f"{year}{fossnaphtha_suffix}" for year in Total_fossil_naphtha.index]
        Total_diesel.index = [f"{year}{diesel_suffix}" for year in Total_diesel.index]

        Total_fuel_demand = pd.concat([Total_ammonia, Total_bioMeOH, Total_bio_kerosene, Total_e_kerosene, Total_fossil_kerosene, Total_HFO,
                                    Total_synthetic_naphtha, Total_bio_naphtha, Total_fossil_naphtha, Total_diesel])
        Total_fuel_demand = Total_fuel_demand * 1e6  # Convert MWh

        filename = "OPTIFLOW_MINFLOW"
        incfile = IncFile(name = filename,
                        prefix="TABLE MINFLOW1(YYY,PROC,FLOW,AAA) 'Constraint about fuel use limitations (U/year)'\n",
                        suffix="\n;\nMINFLOW(YYY,AAA,PROC,FLOW)$(AAAOPTIFLOW(AAA)) = MINFLOW1(YYY,PROC,FLOW,AAA);",
                        path="incfiles" + sub_path)
        
        incfile.body = pd.DataFrame(index=Total_fuel_demand.index,
                                    columns=Total_fuel_demand.columns,
                                    data=Total_fuel_demand.values)

        incfile.save()

    return Total_demand

def write_hydrogen_demand(model_results: pd.DataFrame,
                          distribution_keys: pd.DataFrame,
                            model_years: list = [2030, 2040, 2050],
                            sub_path: str = "",
                            ):
    """
    Write hydrogen demand results to an IncFile. This function takes the model results from a SD run and writes them to the HYDROGEN_DH2.inc file.
    Parameter dimensions:
    - Year
    - Area
    
    Returns:
    - IncFile with the hydrogen demand results for the chosen years.
    """

    # Step 1: Read the model results DataFrame and extract the relevant columns
    results = load_sectoral_production(model_results=model_results)

    # Step 2: Read the data required for the IncFile
    distribution_keys = distribution_keys
    
    # Hydrogen consumed from different sectors
    hydrogen_light_duty = results["light duty"]
    hydrogen_heavy_duty = results["heavy duty"]
    hydrogen_light_duty = hydrogen_light_duty.iloc[:, 2]
    hydrogen_heavy_duty = hydrogen_heavy_duty.iloc[:, 2]
    hydrogen_domestic_shipping = results["domestic shipping"]
    hydrogen_domestic_shipping = hydrogen_domestic_shipping.iloc[:, 3]
    hydrogen_refining = results["refinery"]
    hydrogen_refining = hydrogen_refining.sum(axis=1) #MTH2
    hydrogen_refining = hydrogen_refining * (33.33 / 1e6)  # Convert to TWh
    hydrogen_HT_heat = results["high temperature"]
    hydrogen_HT_heat = hydrogen_HT_heat.iloc[:, 3]
    hydrogen_light_duty = pd.DataFrame(hydrogen_light_duty.values[:, None] * distribution_keys["Road transport"].values[None, :],
                                       index=hydrogen_light_duty.index,
                                       columns=distribution_keys["Road transport"].index)

    hydrogen_heavy_duty = pd.DataFrame(hydrogen_heavy_duty.values[:, None] * distribution_keys["Road transport"].values[None, :],
                                       index=hydrogen_heavy_duty.index,
                                       columns=distribution_keys["Road transport"].index)

    hydrogen_domestic_shipping = pd.DataFrame(hydrogen_domestic_shipping.values[:, None] * distribution_keys["Domestic shipping"].values[None, :],
                                               index=hydrogen_domestic_shipping.index,
                                               columns=distribution_keys["Domestic shipping"].index)

    hydrogen_refining = pd.DataFrame(hydrogen_refining.values[:, None] * distribution_keys["Refining"].values[None, :],
                                      index=hydrogen_refining.index,
                                      columns=distribution_keys["Refining"].index)

    hydrogen_HT_heat = pd.DataFrame(hydrogen_HT_heat.values[:, None] * distribution_keys["High temperature heat"].values[None, :],
                                     index=hydrogen_HT_heat.index,
                                     columns=distribution_keys["High temperature heat"].index)
    
    Total_hydrogen_demand = hydrogen_light_duty + hydrogen_heavy_duty + hydrogen_domestic_shipping + hydrogen_refining + hydrogen_HT_heat
    Total_hydrogen_demand = Total_hydrogen_demand * 1e6  # Convert MWh
    # Step 4: Prepare the data for the IncFile
    Total_hydrogen_demand = Total_hydrogen_demand.loc[model_years]

    Total_hydrogen_demand.index = Total_hydrogen_demand.index.astype(str)
    Total_hydrogen_demand.index = [idx.replace('.0', '') for idx in Total_hydrogen_demand.index]
    Total_hydrogen_demand = Total_hydrogen_demand.rename(columns=lambda x: x.replace('_A', ''))

    # Step 4: Write the results to the IncFile
    #incfile

    filename = "HYDROGEN_DH2"

    incfile = IncFile(name=filename,
                      prefix="TABLE HYDROGEN_DH22(YYY,CCCRRRAAA) 'Hydrogen demand by region and year'\n",
                      suffix="\n;\nHYDROGEN_DH2(YYY,CCCRRRAAA) = HYDROGEN_DH22(YYY,CCCRRRAAA);",
                      path="incfiles" + sub_path)
    incfile.body = pd.DataFrame(index=Total_hydrogen_demand.index,
                                columns=Total_hydrogen_demand.columns,
                                data=Total_hydrogen_demand.values)
    
    incfile.save()

    return Total_hydrogen_demand

def write_heat_demand(model_results: pd.DataFrame,
                      distribution_keys: pd.DataFrame,
                        model_years: list = [2030, 2040, 2050],
                        sub_path: str = "",
                        ):
    """
    Write heat demand results to an IncFile. This function takes the model results from a SD run and writes them to the HEAT_DH2.inc file.
    Parameter dimensions:
    - Year
    - Area
    Returns:
    - IncFile with the heat demand results for the chosen years.
    """
    results = load_sectoral_production(model_results=model_results)
    
    heat_HT = results["high temperature"].iloc[:, :3]
    heat_HT = heat_HT[heat_HT.index.isin(model_years)]

    print(heat_HT)

    return heat_HT

def write_electricity_demand(model_results: pd.DataFrame,
                            distribution_keys: pd.DataFrame,
                            electricity_demand: pd.DataFrame,
                            model_years: list = [2030, 2040, 2050],
                            sub_path: str = "",
                            ):
    """
    Write electricity demand results to an IncFile. This function takes the model results from a SD run and writes them to the TRANSPORT_DE.inc file.
    Parameter dimensions:
    - Year
    - Area
    
    Returns:
    - IncFile with the transport electricity demand results for the chosen years.
    - IncFile with the general electricity demand results for the chosen years.
    """

    # Step 1: Read the model results DataFrame and extract the relevant columns
    results = load_sectoral_production(model_results=model_results)

    # Step 2: Read the data required for the IncFile
    distribution_keys = distribution_keys
    electricity_demand = electricity_demand
    
    # Electricity consumed from different sectors
    electricity_light_duty = results["light duty"]
    electricity_heavy_duty = results["heavy duty"]
    electricity_light_duty = electricity_light_duty.iloc[:, 1]
    electricity_heavy_duty = electricity_heavy_duty.iloc[:, 1]
    electricity_rail = electricity_demand["FC - TRANS,RAIL"]
    
    # Step 3: Prepare the data for the IncFile

    electricity_light_duty = pd.DataFrame(electricity_light_duty.values[:, None] * distribution_keys["Road transport"].values[None, :],
                                       index=electricity_light_duty.index,
                                       columns=distribution_keys["Road transport"].index)

    electricity_heavy_duty = pd.DataFrame(electricity_heavy_duty.values[:, None] * distribution_keys["Road transport"].values[None, :],
                                       index=electricity_heavy_duty.index,
                                       columns=distribution_keys["Road transport"].index)
    
    electricity_rail = pd.DataFrame(electricity_rail.values[:, None],
                                    index=electricity_rail.index,
                                    columns=["Rail"])

    electricity_light_duty = electricity_light_duty.loc[model_years]
    electricity_heavy_duty = electricity_heavy_duty.loc[model_years]
    electricity_light_duty.index = electricity_light_duty.index.astype(str)
    electricity_heavy_duty.index = electricity_heavy_duty.index.astype(str)
    electricity_light_duty.index = [idx.replace('.0', '') for idx in electricity_light_duty.index]
    electricity_heavy_duty.index = [idx.replace('.0', '') for idx in electricity_heavy_duty.index]
    electricity_light_duty = electricity_light_duty.rename(columns=lambda x: x.replace('_A', ''))
    electricity_heavy_duty = electricity_heavy_duty.rename(columns=lambda x: x.replace('_A', ''))
    electricity_rail = pd.concat([electricity_rail]*len(model_years), axis=1)
    electricity_rail.columns = model_years
    electricity_rail = electricity_rail.T

    light_duty_suffix = " . TRANS_EV     "
    heavy_duty_suffix = " . TRANS_BUS    "
    rail_suffix =       " . TRANS_TRAINS "

    electricity_light_duty.index = [f"{year}{light_duty_suffix}" for year in electricity_light_duty.index]
    electricity_heavy_duty.index = [f"{year}{heavy_duty_suffix}" for year in electricity_heavy_duty.index]
    electricity_rail.index = [f"{year}{rail_suffix}" for year in electricity_rail.index]

    transport_electricity_demand = pd.concat([electricity_light_duty, electricity_heavy_duty, electricity_rail])

    transport_electricity_demand = transport_electricity_demand * 1e6  # Convert MWh

    # Step 4: Write the results to the IncFile
    filename1 = "TRANSPORT_DE"

    incfile = IncFile(name=filename1,
                      prefix="TABLE   DE1_TRANS(YYY,DEUSER,RRR)   'Annual electricity consumption (MWh)'\n",
                      suffix="\n;\nDE(YYY,RRR,DEUSER)$(DE1_TRANS(YYY,DEUSER,RRR))   = DE1_TRANS(YYY,DEUSER,RRR);",
                      path="incfiles" + sub_path)
    incfile.body = pd.DataFrame(index=transport_electricity_demand.index,
                                columns=transport_electricity_demand.columns,
                                data=transport_electricity_demand.values)
    incfile.save()

    electricity_residential = electricity_demand["FC - RES"]
    electricity_commercial = electricity_demand["FC - OTHER"]
    electricity_industrial = electricity_demand["FC - IND"]

    electricity_residential = pd.DataFrame(electricity_residential.values[:, None],
                                             index=electricity_residential.index,
                                             )

    electricity_commercial = pd.DataFrame(electricity_commercial.values[:, None],
                                           index=electricity_commercial.index,
                                           )

    electricity_industrial = pd.DataFrame(electricity_industrial.values[:, None],
                                           index=electricity_industrial.index,
                                           )
    residential_suffix = " . RESE  "
    commercial_suffix =  " . OTHER "
    industrial_suffix =  " . PII   "
    electricity_residential.index = [f"{region}{residential_suffix}" for region in electricity_residential.index]
    electricity_commercial.index = [f"{region}{commercial_suffix}" for region in electricity_commercial.index]
    electricity_industrial.index = [f"{region}{industrial_suffix}" for region in electricity_industrial.index]

    electricity_total = pd.concat([electricity_residential, electricity_commercial, electricity_industrial], axis=0)

    electricity_total = electricity_total * 1e6  # Convert MWh
    electricity_total = pd.concat([electricity_total]*len(model_years), axis=1)
    electricity_total.columns = model_years

    filename2 = "DE"

    incfile = IncFile(name=filename2,
                      prefix="TABLE   DE1(RRR,DEUSER,YYY)   'Annual electricity consumption (MWh)'\n",
                      suffix="\n;\nDE(YYY,RRR,DEUSER)$(DE1(RRR,DEUSER,YYY))   = DE1(RRR,DEUSER,YYY);",
                      path="incfiles" + sub_path)
    incfile.body = pd.DataFrame(index=electricity_total.index,
                                columns=electricity_total.columns,
                                data=electricity_total.values)
    incfile.save()

    return transport_electricity_demand, electricity_total

def write_electrolyzer_capex(model_results: pd.DataFrame,
                                hydrogen_data: pd.DataFrame,
                                model_years: list = [2025, 2030, 2040, 2050],
                                sub_path: str = "",
                                ):
    """
    Write electrolyzer CAPEX results to the HYDROGEN_GDATA IncFile.
    Parameter dimensions:
    - Technology
    - Data category
    
    Returns:
    - IncFile with the electrolyzer CAPEX results for the chosen years.
    """

    # Step 1: Read the model results DataFrame and extract the relevant columns
    # Electrolyzer CAPEX from different sectors
    electrolyzer_CAPEX = model_results["AEC CAPEX"] / 1000 # M€/MW_el
    electrolyzer_CAPEX = pd.DataFrame(electrolyzer_CAPEX.values[:, None],
                                            index=electrolyzer_CAPEX.index,
                                            columns=["CAPEX"])
    electrolyzer_CAPEX = electrolyzer_CAPEX.loc[model_years]
    electrolyzer_CAPEX.index = electrolyzer_CAPEX.index.astype(str)
    electrolyzer_CAPEX.index = [idx.replace('.0', '') for idx in electrolyzer_CAPEX.index]
    electrolyzer_CAPEX = electrolyzer_CAPEX.rename(index={'2025': '2020'})

    # aec_technologies = ["GNR_ELYS_ELEC_AEC_Y-2020",
    #                     "GNR_ELYS_ELEC_AEC_Y-2030",
    #                     "GNR_ELYS_ELEC_AEC_Y-2040",
    #                     "GNR_ELYS_ELEC_AEC_Y-2050"]
    aec_technologies = ["GNR_ELYS_ELEC_AEC_Y-2030",
                        "GNR_ELYS_ELEC_AEC_Y-2040",
                        "GNR_ELYS_ELEC_AEC_Y-2050"]
    investment_cost_index = ["GDINVCOST0"]

    hydrogen_data.loc[aec_technologies, investment_cost_index] = electrolyzer_CAPEX.values

    hydrogen_data.fillna('', inplace=True)

    filename = "HYDROGEN_GDATA"

    incfile = IncFile(name=filename,
                    prefix="TABLE GDATA(GGG,GDATASET)  'Technologies characteristics'\n",
                    suffix="\n;",
                    path="incfiles" + sub_path
                    )

    incfile.body = pd.DataFrame(index=hydrogen_data.index,
                                columns=hydrogen_data.columns,
                                data=hydrogen_data.values)
    incfile.save()

    return electrolyzer_CAPEX

def write_hydrogen_production(model_results: pd.DataFrame,
                            distribution_keys: pd.DataFrame,
                            model_years: list = [2030, 2040, 2050],
                            sub_path: str = "",
                            ):
    """
    Write production from SMR technologies to an IncFile. This function takes the model results from a SD run and writes them to the HYDROGEN_MAXCH4TOH2.inc file.
    Parameter dimensions:
    - Year
    - Technology
    - Area
    
    Returns:
    - IncFile with the hydrogen production results for the chosen years.
    """

    # Step 1: Read the model results DataFrame and extract the relevant columns
    results = load_sectoral_production(model_results=model_results)

    df_blue_refinery = model_results[['refinery blue hydrogen demand']]
    df_grey_refinery = model_results[['refinery grey hydrogen demand']]
    df_blue_fertilizer = model_results[['fertilizer blue hydrogen demand']]
    df_grey_fertilizer = model_results[['fertilizer grey hydrogen demand']]

    # Step 2: Read the data required for the IncFile
    distribution_keys_refining = distribution_keys["Refining"]
    distribution_keys_fertilizer = distribution_keys["Fertilizer"]

    df_blue_refinery_A = pd.DataFrame(df_blue_refinery.values * distribution_keys_refining.values,
                                       index=df_blue_refinery.index,
                                       columns=distribution_keys["Refining"].index)
    df_grey_refinery_A = pd.DataFrame(df_grey_refinery.values * distribution_keys_refining.values,
                                       index=df_grey_refinery.index,
                                       columns=distribution_keys["Refining"].index)
    df_blue_fertilizer_A = pd.DataFrame(df_blue_fertilizer.values * distribution_keys_fertilizer.values,
                                       index=df_blue_fertilizer.index,
                                       columns=distribution_keys["Fertilizer"].index)
    df_grey_fertilizer_A = pd.DataFrame(df_grey_fertilizer.values * distribution_keys_fertilizer.values,
                                       index=df_grey_fertilizer.index,
                                       columns=distribution_keys["Fertilizer"].index)
    df_blue = (df_blue_refinery_A + df_blue_fertilizer_A) * 33.33 # Convert to MWh
    df_grey = (df_grey_refinery_A + df_grey_fertilizer_A) * 33.33 # Convert to MWh

    df_blue = df_blue.loc[model_years]
    df_grey = df_grey.loc[model_years]

    df_blue.index = df_blue.index.astype(str)
    df_grey.index = df_grey.index.astype(str)

    df_blue.index = [idx.replace('.0', '') for idx in df_blue.index]
    df_grey.index = [idx.replace('.0', '') for idx in df_grey.index]

    blue_suffix = " . GNR_STEAM-REFORMING-CCS_E-70_Y-2020   "
    grey_suffix = " . GNR_STEAM-REFORMING_E-70_Y-2020       "

    df_blue.index = [f"{year}{blue_suffix}" for year in df_blue.index]
    df_grey.index = [f"{year}{grey_suffix}" for year in df_grey.index]

    total_hydrogen_production = pd.concat([df_blue, df_grey])

    filename = "HYDROGEN_MINGCH4TOH2"

    incfile = IncFile(name=filename,
                      prefix="TABLE HYDROGEN_MINGCH4TOH2(Y,G,AAA) 'Minimum natural gas to hydrogen production by region and year'\n",
                      suffix="\n;",
                      path="incfiles" + sub_path)
    
    incfile.body = pd.DataFrame(index=total_hydrogen_production.index,
                                columns=total_hydrogen_production.columns,
                                data=total_hydrogen_production.values)
    incfile.save()


    return total_hydrogen_production


if __name__ == "__main__":
    baseline_results = pd.read_csv("vensim_results\\baseline_results.csv", index_col=0)
    subsidy_results = pd.read_csv("vensim_results\\subsidy_results.csv", index_col=0)
    hba_results = pd.read_csv("vensim_results\\hba_results.csv", index_col=0)
    mandate_results = pd.read_csv("vensim_results\\mandate_results.csv", index_col=0)
    distribution_keys = dl.load_distribution_keys()
    hydrogen_data = dl.load_hydrogen_data()
    model_years = [2030, 2040, 2050]
    out_path = ['\\loop4']

    output = write_electrolyzer_capex(model_results=baseline_results,
                                hydrogen_data=hydrogen_data,
                                model_years=model_years,
                                sub_path=out_path[0])