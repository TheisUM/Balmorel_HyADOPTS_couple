import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
    # df_combined = df_combined[df_combined["Year"].isin([2025, 2030, 2035, 2040, 2045, 2050])]
    # df_combined = df_combined[df_combined["Year"].isin([2030])]
    df_pivot = df_combined.pivot_table(index=["Scenario", "Year"], 
                                        columns="Sector", 
                                        values="Actual cost")
    df_pivot = df_pivot.reset_index()
    df_pivot.columns.name = None
    
    return df_pivot

def plot_figure_2(model_results_dictionary = dict) -> None:
    keys = list(model_results_dictionary.keys())
    emission_sources = ["naphtha emissions", "refinery emissions", "fertilizer emissions", "steel emissions", "high temperature emissions", "MeOH emissions",
                        "international shipping emissions", "heavy duty emissions", "international aviation emissions", "domestic shipping emissions", "domestic aviation emissions"]
    h2_tech_to_sector_dict = {'Green Refinery': 'refinery', 'H2 NM': 'high temperature', 'Green NH3': 'fertilizer', 'H2DRI EAF': 'steel', 'BioNaphtha': 'naphtha',
                                                     'SynNaphtha': 'naphtha', 'BioMeOH': 'MeOH', 'eMeOH': 'MeOH', 'SynKero IA': 'international aviation', 
                                                     'BioKero IA': 'international aviation', 'SynKero DA': 'domestic aviation', 'BioKero DA': 'domestic aviation', 'LD FCEV': 'light duty',
                                                     'HD FCEV': 'heavy duty', 'NH3 IS': 'international shipping', 'MeOH IS': 'international shipping',
                                                     'MeOH DS': 'domestic shipping', 'H2FC DS': 'domestic shipping'}
    subsidy_costs = [tech + " subsidy cost" for tech in h2_tech_to_sector_dict.keys()]

    grouping_of_sectors1 = {"BioNaphtha subsidy cost": "Naphtha",
                            "SynNaphtha subsidy cost": "Naphtha",
                       "Green Refinery subsidy cost": "Refining",
                       "Green NH3 subsidy cost": "Fertilizer",
                          "H2DRI EAF subsidy cost": "Steel",
                            "H2 NM subsidy cost": "HT heat",
                            "BioMeOH subsidy cost": "Methanol",
                            "eMeOH subsidy cost": "Methanol",
                            "LD FCEV subsidy cost": "Light duty road",
                            "HD FCEV subsidy cost": "Heavy duty road",
                            "NH3 IS subsidy cost": "International shipping",
                            "MeOH IS subsidy cost": "International shipping",
                            "MeOH DS subsidy cost": "Domestic shipping",
                            "H2FC DS subsidy cost": "Domestic shipping",
                            "BioKero IA subsidy cost": "International aviation",
                            "SynKero IA subsidy cost": "International aviation",
                            "BioKero DA subsidy cost": "Domestic aviation",
                            "SynKero DA subsidy cost": "Domestic aviation",}

    time_step = mandate_results.index[1] - mandate_results.index[0]

    dict_sector_effective_cost = calculate_sector_effective_cost(result_dictionary)
    df_actual_sector_cost = calculate_actual_sector_cost(dict_sector_effective_cost,result_dictionary)
    
    # Calculate difference between baseline and other scenarios
    scenarios = keys
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

    list_cumm_dfs = []
    for scenario in scenarios:
        if scenario == "baseline":
            continue
        scenario_df = df_difference[df_difference["Scenario"] == scenario].copy()
        sector_columns = [col for col in df_difference.columns if col not in ["Scenario", "Year"]]
        scenario_df[sector_columns] = scenario_df[sector_columns].cumsum() * time_step
        list_cumm_dfs.append(scenario_df)
    df_difference_cummulative = pd.concat(list_cumm_dfs, ignore_index=True)
    df_difference_cummulative = df_difference_cummulative[df_difference_cummulative["Year"].isin([2025, 2030, 2035, 2040, 2045, 2050])]
    df_difference_cummulative.drop(columns=["Light duty road"], inplace=True)
    # df_difference_cummulative.to_csv("vensim_results\\difference_cummulative.csv", index=False)
    # print(df_difference_cummulative)

    df_emissions_base = model_results_dictionary[keys[0]][emission_sources].sum(axis=1) / 1e6 # Convert to MtCO2/y
    df_emissions_base_cumulative = df_emissions_base.cumsum().iloc[-1] * time_step / 1e3 # GtCO2 cumulative
    df_emissions_base = df_emissions_base[df_emissions_base.index.isin([2022, 2025, 2030, 2035, 2040, 2045, 2050])] # Focus on years
    df_emissions_premium = model_results_dictionary[keys[1]][emission_sources].sum(axis=1) / 1e6 # Convert to MtCO2/y
    df_emissions_premium_cumulative = df_emissions_premium.cumsum().iloc[-1] * time_step / 1e3 # GtCO2 cumulative
    df_emissions_premium = df_emissions_premium[df_emissions_premium.index.isin([2022, 2025, 2030, 2035, 2040, 2045, 2050])] # Focus on years
    df_emissions_hba = model_results_dictionary[keys[2]][emission_sources].sum(axis=1) / 1e6 # Convert to MtCO2/y
    df_emissions_hba_cumulative = df_emissions_hba.cumsum().iloc[-1] * time_step / 1e3 # GtCO2 cumulative
    df_emissions_hba = df_emissions_hba[df_emissions_hba.index.isin([2022, 2025, 2030, 2035, 2040, 2045, 2050])] # Focus on years
    df_emissions_mandates = model_results_dictionary[keys[3]][emission_sources].sum(axis=1) / 1e6 # Convert to MtCO2/y
    df_emissions_mandates_cumulative = df_emissions_mandates.cumsum().iloc[-1] * time_step / 1e3 # GtCO2 cumulative
    df_emissions_mandates = df_emissions_mandates[df_emissions_mandates.index.isin([2022, 2025, 2030, 2035, 2040, 2045, 2050])] # Focus on years

    df_subsidy_premium = model_results_dictionary[keys[1]][subsidy_costs].sum(axis=1).cumsum() * time_step # B€ cumulative
    df_subsidy_premium = df_subsidy_premium[df_subsidy_premium.index.isin([2022, 2025, 2030, 2035, 2040, 2045, 2050])] # Focus on years
    df_subsidy_hba = model_results_dictionary[keys[2]][subsidy_costs].sum(axis=1).cumsum() * time_step # B€ cumulative
    df_subsidy_hba = df_subsidy_hba[df_subsidy_hba.index.isin([2022, 2025, 2030, 2035, 2040, 2045, 2050])] # Focus on years

    df_premium_abatement_cost = df_subsidy_premium.iloc[-1] / (df_emissions_base_cumulative - df_emissions_premium_cumulative) # €/tCO2
    df_hba_abatement_cost = df_subsidy_hba.iloc[-1] / (df_emissions_base_cumulative - df_emissions_hba_cumulative) # €/tCO2
    print(f"Premium subsidy abatement cost in 2050: {df_premium_abatement_cost:.2f} tCO2/€. --- {df_subsidy_premium.iloc[-1]} B€ over {df_emissions_base_cumulative - df_emissions_premium_cumulative:.2f} GtCO2 cumulative abated.")
    print(f"HBA style subsidy abatement cost in 2050: {df_hba_abatement_cost:.2f} tCO2/€. --- {df_subsidy_hba.iloc[-1]} B€ over {df_emissions_base_cumulative - df_emissions_hba_cumulative:.2f} GtCO2 cumulative abated.")    

    df_subsidy_premium_sector = model_results_dictionary[keys[1]][subsidy_costs].cumsum().iloc[-1] * time_step # B€ cumulative
    df_subsidy_premium_sector = df_subsidy_premium_sector.rename(index=grouping_of_sectors1)
    df_subsidy_premium_sector = df_subsidy_premium_sector.groupby(df_subsidy_premium_sector.index).sum()
    df_subsidy_premium_sector.drop(columns="Light duty road", inplace=True)
    df_subsidy_hba_sector = model_results_dictionary[keys[2]][subsidy_costs].cumsum().iloc[-1] * time_step # B€ cumulative
    df_subsidy_hba_sector = df_subsidy_hba_sector.rename(index=grouping_of_sectors1)
    df_subsidy_hba_sector = df_subsidy_hba_sector.groupby(df_subsidy_hba_sector.index).sum()
    df_subsidy_hba_sector.drop(columns="Light duty road", inplace=True)

    df_subsidy_sector = pd.DataFrame({"subsidy": df_subsidy_premium_sector,
                                        "hba": df_subsidy_hba_sector})
    
    sector_order = ["Naphtha", "Refining", "Fertilizer", "Steel", "HT heat", "Methanol", "Heavy duty road", "International shipping", "Domestic shipping", "International aviation", "Domestic aviation"]

    df_subsidy_sector = df_subsidy_sector.reindex(sector_order)
    
    df_policy_cost = df_difference_cummulative.copy()
    df_policy_cost = df_policy_cost[df_policy_cost["Year"] == 2050]
    df_policy_cost.drop(columns=["Year"], inplace=True)
    df_policy_cost = df_policy_cost.set_index("Scenario")
    df_policy_cost = df_policy_cost.T
    df_policy_cost = df_policy_cost.reindex(sector_order)
    # print(df_subsidy_sector)
    print(df_policy_cost)
    df_policy_cost["subsidy"] = df_policy_cost["subsidy"] + df_subsidy_sector["subsidy"]
    df_policy_cost["hba"] = df_policy_cost["hba"] + df_subsidy_sector["hba"]
    # print(df_policy_cost)

    fig = plt.figure()
    fig.set_figheight(5)
    fig.set_figwidth(10)

    ax1 = plt.subplot2grid((2,2), (0,0), colspan=1)
    df_subsidy_premium.plot(kind='line', color='teal', linewidth=3, ax=ax1, legend=False,zorder=10)
    df_subsidy_hba.plot(kind='line', color='goldenrod', linewidth=3, ax=ax1, legend=False,zorder=10)
    # print(df_subsidy_premium.iloc[-1], df_subsidy_hba.iloc[-1])
    ax1.set_xlabel("")
    ax1.set_ylabel("Subsidy payout (B€)", fontsize=10)
    ax1.set_title("a) Cumulative subsidy payout", fontsize=10, loc='left')
    ax1.set_ylim(0, 1200)
    ax1.set_yticks(range(0,1200+1,200))
    ax1.set_xlim(2025, 2050)
    ax1.set_xticklabels([])
    ax1.legend(labels=["Premium", "Auction"],loc='upper left', fontsize='small',frameon=True)
    ax1.grid(True)
    ax2 = plt.subplot2grid((2,2), (1,0), colspan=1)
    df_emissions_base.plot(kind='line', color='black', linewidth=3, ax=ax2, legend=True,zorder=10)
    df_emissions_premium.plot(kind='line', color='teal', linewidth=3, ax=ax2, legend=False,zorder=10)
    df_emissions_hba.plot(kind='line', color='goldenrod', linewidth=3, ax=ax2, legend=False,zorder=10)
    df_emissions_mandates.plot(kind='line', color='crimson', linewidth=3, ax=ax2, legend=False,zorder=10)
    # print(df_emissions_base.iloc[-1], df_emissions_premium.iloc[-1], df_emissions_hba.iloc[-1], df_emissions_mandates.iloc[-1])
    ax2.set_xlabel("")
    ax2.set_ylabel("Emissions (MtCO$_2$/y)", fontsize=10)
    ax2.set_title("b) Emissions projection", fontsize=10, loc='left')
    ax2.set_ylim(0, 1200)
    ax2.set_yticks(range(0, 1200+1, 200))
    ax2.set_xlim(2025, 2050)
    ax2.grid(True)
    ax2.legend(labels=["Baseline", "Premium", "Auction","Budget"],loc='lower left', fontsize='small',frameon=True)
    ax3 = plt.subplot2grid((2,2), (0,1), colspan=1, rowspan=2)
    x1 = np.arange(len(df_subsidy_sector.index))
    x2 = x1 + 0.3
    x3 = x1 + 0.6
    bar1 = plt.bar(x1, df_policy_cost["subsidy"], color='teal', label='Premium',width=0.3,zorder=10)
    bar2 = plt.bar(x2, df_policy_cost["hba"], color='goldenrod', label='Auction',width=0.3,zorder=10)
    bar3 = plt.bar(x3, df_policy_cost["mandate"], color='crimson', label='Mandate',width=0.3,zorder=10)
    # for bar in bar1:
    #     height = bar.get_height()
    #     ax3.annotate(f'{height:.0f}',
    #                 xy=(bar.get_x() + bar.get_width() / 3, height),
    #                 xytext=(-3, 3),  # 3 points offset
    #                 textcoords="offset points",
    #                 ha='center', va='bottom', fontsize=8)
    # for bar in bar2:
    #     height = bar.get_height()
    #     ax3.annotate(f'{height:.0f}',
    #                 xy=(bar.get_x() + bar.get_width() / 3, height),
    #                 xytext=(3, 3),  # 3 points offset
    #                 textcoords="offset points",
    #                 ha='center', va='bottom', fontsize=8)
    # for bar in bar3:
    #     height = bar.get_height()
    #     ax3.annotate(f'{height:.0f}',
    #                 xy=(bar.get_x() + bar.get_width() / 3, height),
    #                 xytext=(3, 3),  # 3 points offset
    #                 textcoords="offset points",
    #                 ha='center', va='bottom', fontsize=8)
    ax3.set_xlabel("")
    ax3.set_ylabel("Policy cost (B€)", fontsize=10)
    ax3.set_title("c) Cumulative 'policy cost' per sector in 2050", fontsize=10, loc='left')
    ax3.set_xticks(x1 + 0.3)
    ax3.set_xticklabels(df_subsidy_sector.index, rotation=45, ha='right', fontsize=8)
    ax3.legend(loc='upper left', fontsize='small', frameon=True)
    ax3.grid(True)
    ax3.set_ylim(-100, 600)
    ax3.set_xlim(-0.4,11)

    fig.subplots_adjust(hspace=0.2, wspace=0.2, bottom=0.21, top=0.95, left=0.08, right=0.97)
    plt.show()
    return None

if __name__ == "__main__":
    baseline_results = pd.read_csv("vensim_results_main\\baseline_results.csv", index_col=0)
    subsidy_results = pd.read_csv("vensim_results_main\\subsidy_results.csv", index_col=0)
    hba_results = pd.read_csv("vensim_results_main\\hba_results.csv", index_col=0)
    mandate_results = pd.read_csv("vensim_results_main\\mandate_results.csv", index_col=0)

    result_dictionary = {"baseline": baseline_results,
                        "subsidy": subsidy_results,
                        "hba": hba_results,
                        "mandate": mandate_results,
                        }

    # baseline_Ctax_revenue = baseline_results["CUMULATED CARBON TAX REVENUE"] / 1e3 # B€ 
    # premium_Ctax_revenue = subsidy_results["CUMULATED CARBON TAX REVENUE"] / 1e3 # B€
    # hba_Ctax_revenue = hba_results["CUMULATED CARBON TAX REVENUE"] / 1e3 # B€
    # mandate_Ctax_revenue = mandate_results["CUMULATED CARBON TAX REVENUE"] / 1e3 # B€
    # total_Ctax_revenue = pd.DataFrame({"Baseline": baseline_Ctax_revenue,
    #                                     "Premium": premium_Ctax_revenue,
    #                                     "HBA style": hba_Ctax_revenue,
    #                                     "Budget": mandate_Ctax_revenue})
    # total_Ctax_revenue = total_Ctax_revenue[total_Ctax_revenue.index.isin([2025, 2030, 2035, 2040, 2045, 2050])]
    # print(total_Ctax_revenue)
    # total_Ctax_revenue.to_csv("vensim_results\\total_Ctax_revenue.csv")

    # h2_tech_to_sector_dict = {'Green Refinery': 'refinery', 'H2 NM': 'high temperature', 'Green NH3': 'fertilizer', 'H2DRI EAF': 'steel', 'BioNaphtha': 'naphtha',
    #                                                  'SynNaphtha': 'naphtha', 'BioMeOH': 'MeOH', 'eMeOH': 'MeOH', 'SynKero IA': 'international aviation', 
    #                                                  'BioKero IA': 'international aviation', 'SynKero DA': 'domestic aviation', 'BioKero DA': 'domestic aviation', 'LD FCEV': 'light duty',
    #                                                  'HD FCEV': 'heavy duty', 'NH3 IS': 'international shipping', 'MeOH IS': 'international shipping',
    #                                                  'MeOH DS': 'domestic shipping', 'H2FC DS': 'domestic shipping'}
    # subsidy_costs = [tech + " subsidy cost" for tech in h2_tech_to_sector_dict.keys()]

    # payout_premium = subsidy_results[subsidy_costs].cumsum() * (1/4) # B€ cumulative
    # payout_premium["Scenario"] = "Premium"
    # payout_hba = hba_results[subsidy_costs].cumsum() * (1/4) # B€ cumulative
    # payout_hba["Scenario"] = "Auction"
    # total_payout = pd.concat([payout_premium, payout_hba], axis=0)
    # total_payout = total_payout[total_payout.index.isin([2025, 2030, 2035, 2040, 2045, 2050])]
    # total_payout.to_csv("vensim_results\\total_payout.csv")
    # print(total_payout)

    plot_figure_2(result_dictionary)

    # dict_sector_effective_cost = calculate_sector_effective_cost(result_dictionary)
    # df_actual_sector_cost = calculate_actual_sector_cost(dict_sector_effective_cost,result_dictionary)
    # df_actual_sector_cost = df_actual_sector_cost[df_actual_sector_cost["Year"].isin([2025, 2030, 2035, 2040, 2045, 2050])]
    # df_actual_sector_cost.to_csv("vensim_results\\actual_sector_cost_2.csv", index=False)
