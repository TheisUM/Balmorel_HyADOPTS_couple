import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from result_loading import result_loading_class

rl = result_loading_class()

def calculate_sector_effective_cost(model_results_dictionary = dict) -> dict:
    scenarios = list(model_results_dictionary.keys())
    commissions_of_hydrogen_technologies = {
        "Refining": ["Green Refinery Commissioning"],
        "HT heat": ["H2 NM Commissioning"],
        "Fertilizer": ["Green NH3 Commissioning"],
        "Steel": ["H2DRI EAF Commissioning"],
        "Naphtha": ["BioNaphtha Commissioning", "SynNaphtha Commissioning"], 
        "Methanol": ["BioMeOH Commissioning", "eMeOH Commissioning"],
        "International aviation": ["BioKero IA Commissioning", "SynKero IA Commissioning"],
        "Domestic aviation": ["BioKero DA Commissioning", "SynKero DA Commissioning"],
        "Light duty road": ["LD FCEV Commissioning"],
        "Heavy duty road": ["HD FCEV Commissioning"],
        "International shipping": ["MeOH IS Commissioning", "NH3 IS Commissioning"],
        "Domestic shipping": ["MeOH DS Commissioning", "H2FC DS Commissioning"],
    }
    sector_technology_shares = {
        "Refining": ["Grey refinery sector share", "Blue refinery sector share", "Green refinery sector share"],
        "HT heat": ["Grey NM sector share", "Blue NM sector share", "H2 NM sector share","Biogas NM sector share"],
        "Fertilizer": ["Grey NH3 sector share", "Blue NH3 sector share", "Green NH3 sector share"],
        "Steel": ["BF BOF sector share","BF BOF CCS sector share", "NGDRI EAF sector share", "H2DRI EAF sector share"],
        "Naphtha": ["Fossil naphtha sector share", "BioNaphtha sector share", "SynNaphtha sector share"], 
        "Methanol": ["Grey MeOH sector share", "Blue MeOH sector share", "BioMeOH sector share", "eMeOH sector share"],
        "International aviation": ["Jetfuel IA sector share", "SynKero IA sector share", "BioKero IA sector share"],
        "Domestic aviation": ["Jetfuel DA sector share", "SynKero DA sector share", "BioKero DA sector share"],
        "Light duty road": ["LD Fossil sector share","LD BEV sector share","LD FCEV sector share"],
        "Heavy duty road": ["HD Fossil sector share","HD BEV sector share","HD FCEV sector share"],
        "International shipping": ["HFO IS sector share", "NH3 IS sector share", "MeOH IS sector share"],
        "Domestic shipping": ["HFO DS sector share","Electric DS sector share","MeOH DS sector share","H2FC DS sector share"],
    }
    sector_technology_costs_w_learning = {
        "Refining": ["refinery H2 cost"],
        "HT heat": ["NM H2 GJ cost"],
        "Fertilizer": ["fertilizer NH3 cost"],
        "Steel": ["H2DRI cost"],
        "Naphtha": ["BioNaphtha cost", "SynNaphtha cost"], 
        "Methanol": ["Green bioMeOH cost","Green eMeOH cost"],
        "International aviation": ["SynKero cost","BioKero cost"],
        "Domestic aviation": ["SynKero cost","BioKero cost"],
        "Light duty road": ["LD FC LCO"],
        "Heavy duty road": ["HD FC LCO"],
        "International shipping": ["NH3 containership cost","MeOH containership cost"],
        "Domestic shipping": ["MeOH ship cost","FC ship cost"],
    }
    sector_technology_costs_standard = {
        "Refining": ["Grey H2 cost","Blue H2 cost"],
        "HT heat": ["Grey NG cost","Blue NG cost", "biogas cost"],
        "Fertilizer": ["Grey NH3 cost", "Blue NH3 cost"],
        "Steel": ["BF BOF cost", "BF BOF CCS cost", "NGDRI cost"],
        "Naphtha": ["Naphtha cost"], 
        "Methanol": ["convMeOH cost", "Blue MeOH cost"],
        "International aviation": ["Jetfuel cost"],
        "Domestic aviation": ["Jetfuel cost"],
        "Light duty road": ["LD ICE LCO","LD BE LCO"],
        "Heavy duty road": ["HD ICE LCO","HD BE LCO"],
        "International shipping": ["HFO containership cost"],
        "Domestic shipping": ["HFO ship cost","BE ship cost"],
    }

    sectors = list(commissions_of_hydrogen_technologies.keys())

    dict_effective_cost = {}
    dict_average_effective_cost = {}

    for scenario in scenarios:
        results = model_results_dictionary[scenario]
        for sector in sectors:
            df_commissions = results[commissions_of_hydrogen_technologies[sector]]
            df_learning_costs = results[sector_technology_costs_w_learning[sector]]
            df_sector_shares = results[sector_technology_shares[sector]]
            column_names = df_sector_shares.columns
            column_names = [name.replace(" sector share", "") for name in column_names]
            df_standard_costs = results[sector_technology_costs_standard[sector]]
            df_output = pd.DataFrame()
            df_output2 = pd.DataFrame()
            for i, column in enumerate(df_commissions.columns):
                technology = sector_technology_costs_w_learning[sector][i]
                total = df_commissions[column].sum()
                temp1 = df_commissions[column].copy() / total # New commissions
                temp2 = temp1.cumsum()
                df_running_share = temp1/temp2
                df_running_share.iloc[0] = 1
                df_running_share = pd.concat([df_running_share, df_learning_costs[technology]], axis=1)
                df_running_share[technology + " Shifted"] = df_running_share[technology].shift(1)
                df_running_share[technology + " Effective"] = df_running_share.apply(lambda row: row[technology] * row[column] + row[technology + " Shifted"] * (1-row[column]), axis=1)
                df_running_share.loc[2025, technology + " Effective"] = df_running_share.loc[2025, technology]
                df_running_share.drop(columns=[technology + " Shifted",column,technology], inplace=True)
                df_output = pd.concat([df_output, df_running_share], axis=1)
            df_output = pd.concat([df_standard_costs, df_output], axis=1)
            df_output.columns = column_names
            df_sector_shares.columns = column_names
            df_output2 = (df_sector_shares * df_output).sum(axis=1)
            df_output2.name = "Sector average"
            df_output = pd.concat([df_output, df_output2], axis=1)
            dict_effective_cost[(scenario,sector)] = df_output
    return dict_effective_cost

def calculate_actual_sector_cost(effective_cost_dictionary = dict,
                                 result_dictionary = dict) -> pd.DataFrame:
    scenarios = list(dict.fromkeys(key[0] for key in effective_cost_dictionary.keys()))
    sectors = list(dict.fromkeys(key[1] for key in effective_cost_dictionary.keys()))
    sector_activity_conversion = {
        "Refining": [1,"refinery current demand"],
        "HT heat": [3600 / 1e9,"high temperature current demand"],
        "Fertilizer": [18.6/1000,"fertilizer current demand"],
        "Steel": [1/1000,"steel current demand"],
        "Naphtha": [44.9/1000,"naphtha current demand"],
        "Methanol": [19.9/1000,"MeOH current demand"],
        "International aviation": [3600/1e9,"IA current demand"],
        "Domestic aviation": [3600/1e9,"DA current demand"],
        "Light duty road": [(1/0.5)/1000,"LD current demand"],
        "Heavy duty road": [(1/3.2)/1000,"HD current demand"],
        "International shipping": [(1/380)/1000,"IS current demand"],
        "Domestic shipping": [(1/20.8)/1000,"DS current demand"],
    }
    dict_actual_sector_cost = {}
    list_dfs = []
    for scenario in scenarios:
        results = result_dictionary[scenario]
        for sector in sectors:
            conversion = sector_activity_conversion[sector][0]
            df_effective_cost = effective_cost_dictionary[(scenario,sector)].iloc[:,-1]
            df_sector_activity = results[sector_activity_conversion[sector][1]] * conversion
            df_actual_cost = df_effective_cost * df_sector_activity
            dict_actual_sector_cost[(scenario,sector)] = df_actual_cost
            df_temp = df_actual_cost.copy()
            df_temp = df_temp.reset_index()
            df_temp.columns = ["Year", sector]
            df_temp.rename(columns={sector: "Actual cost"}, inplace=True)
            df_temp["Scenario"] = scenario
            df_temp["Sector"] = sector
            list_dfs.append(df_temp)
    
    # Pivot to get sectors as columns
    df_combined = pd.concat(list_dfs, ignore_index=True)
    df_combined = df_combined[df_combined["Year"].isin([2025, 2030, 2035, 2040, 2045, 2050])]
    # df_combined = df_combined[df_combined["Year"].isin([2030])]
    df_pivot = df_combined.pivot_table(index=["Scenario", "Year"], 
                                        columns="Sector", 
                                        values="Actual cost")
    df_pivot = df_pivot.reset_index()
    df_pivot.columns.name = None
    
    return df_pivot

if __name__ == "__main__":
    baseline_results = pd.read_csv("vensim_results\\baseline_results.csv", index_col=0)
    subsidy_results = pd.read_csv("vensim_results\\subsidy_results.csv", index_col=0)
    hba_results = pd.read_csv("vensim_results\\hba_results.csv", index_col=0)
    mandate_results = pd.read_csv("vensim_results\\mandate_results.csv", index_col=0)

    result_dictionary = {"baseline": baseline_results,
                        "subsidy": subsidy_results,
                        "hba": hba_results,
                        "mandate": mandate_results,
                        }
    dict_sector_effective_cost = calculate_sector_effective_cost(result_dictionary)
    df_actual_sector_cost = calculate_actual_sector_cost(dict_sector_effective_cost,
                                                           result_dictionary)
    
    # Calculate difference between baseline and other scenarios
    scenarios = df_actual_sector_cost["Scenario"].unique()
    baseline_df = df_actual_sector_cost[df_actual_sector_cost["Scenario"] == "baseline"].copy()
    
    list_diff_dfs = []
    for scenario in scenarios:
        if scenario == "baseline":
            continue
        scenario_df = df_actual_sector_cost[df_actual_sector_cost["Scenario"] == scenario].copy()
        sector_columns = [col for col in df_actual_sector_cost.columns if col not in ["Scenario", "Year"]]
        
        for sector in sector_columns:
            scenario_df[sector] = scenario_df[sector] - baseline_df[sector].values
        
        list_diff_dfs.append(scenario_df)
    
    df_difference = pd.concat(list_diff_dfs, ignore_index=True)
    df_difference["Total"] = df_difference[sector_columns].sum(axis=1)
    print(df_difference)
    df_actual_sector_cost_cumulative = df_actual_sector_cost.copy()
    df_actual_sector_cost_cumulative[sector_columns] = df_actual_sector_cost[sector_columns].cumsum() * 1/4 # Cumulative cost over 2025-2050, divided by 4 to account for time steps
    # df_actual_sector_cost.to_csv("vensim_results\\actual_sector_cost.csv", index=False)