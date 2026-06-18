import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

def plot_figure_3(model_results_dictionary = dict) -> None:
    # Define the sectors of the model
    steel_sector = ["BF BOF", "BF BOF CCS", "NGDRI EAF", "H2DRI EAF"]
    temp_sector = ["Grey NG NM", "Blue NG NM", "Biogas NM", "H2 NM"]
    dict_heavy_industry = {"BF BOF": "Fossil", "BF BOF CCS": "Blue", "NGDRI EAF": "Fossil", "H2DRI EAF": "Renewable",
                            "Grey NG NM": "Fossil", "Blue NG NM": "Blue", "Biogas NM": "Renewable", "H2 NM": "Renewable"}
    hvc_sector = ["Fossil naphtha", "SynNaphtha", "BioNaphtha"]
    meoh_sector = ["Grey MeOH", "Blue MeOH", "BioMeOH", "eMeOH"]
    fertilizer_sector = ["Grey NH3", "Blue NH3", "Green NH3"]
    dict_chemical_industry = {"Fossil naphtha": "Fossil", "SynNaphtha": "Renewable", "BioNaphtha": "Renewable",
                            "Grey MeOH": "Fossil", "Blue MeOH": "Blue", "BioMeOH": "Renewable", "eMeOH": "Renewable",
                            "Grey NH3": "Fossil", "Blue NH3": "Blue", "Green NH3": "Renewable"}
    refining_sector = ["Grey Refinery", "Blue Refinery", "Green Refinery"]
    dict_refining = {"Grey Refinery": "Fossil", "Blue Refinery": "Blue", "Green Refinery": "Renewable"}
    industry_sectors = steel_sector + hvc_sector + fertilizer_sector + temp_sector + refining_sector + meoh_sector

    int_aviation_sector = ["Jetfuel IA", "SynKero IA", "BioKero IA"]
    dom_aviation_sector = ["Jetfuel DA", "SynKero DA", "BioKero DA"]
    dict_aviation_industry = {"Jetfuel IA": "Fossil", "SynKero IA": "Hydrogen", "BioKero IA": "Biological",
                            "Jetfuel DA": "Fossil", "SynKero DA": "Hydrogen", "BioKero DA": "Biological"}
    int_shipping_sector = ["HFO IS", "NH3 IS", "MeOH IS"]
    dom_shipping_sector = ["HFO DS", "Electric DS", "MeOH DS", "H2FC DS"]
    dict_shipping_industry = {"HFO IS": "Fossil", "NH3 IS": "Hydrogen", "MeOH IS": "Hydrogen",
                            "HFO DS": "Fossil", "Electric DS": "Electric", "MeOH DS": "Hydrogen", "H2FC DS": "Hydrogen"}
    ld_road_transport_sector = ["LD Fossil", "LD BEV", "LD FCEV"]
    hd_road_transport_sector = ["HD Fossil", "HD BEV", "HD FCEV"]
    dict_road_transport_industry = {"LD Fossil": "Fossil", "LD BEV": "Electric", "LD FCEV": "Hydrogen",
                            "HD Fossil": "Fossil", "HD BEV": "Electric", "HD FCEV": "Hydrogen"}
    transport_sectors = int_aviation_sector + dom_aviation_sector + int_shipping_sector + dom_shipping_sector + ld_road_transport_sector + hd_road_transport_sector

    technologies = industry_sectors + transport_sectors
    
    dict_tech_to_sector = {"steel": steel_sector,
                            "hvc": hvc_sector,
                            "meoh": meoh_sector,
                            "fertilizer": fertilizer_sector,
                            "high temperature": temp_sector,
                            "refining": refining_sector,
                            "international aviation": int_aviation_sector,
                            "domestic aviation": dom_aviation_sector,
                            "international shipping": int_shipping_sector,
                            "domestic shipping": dom_shipping_sector,
                            "light duty road transport": ld_road_transport_sector,
                            "heavy duty road transport": hd_road_transport_sector}
    
    dict_sector_grouping = {"heavy industry": steel_sector + temp_sector,
                            "chemical industry": hvc_sector + meoh_sector + fertilizer_sector,
                            "refining industry": refining_sector,
                            "aviation": int_aviation_sector + dom_aviation_sector,
                            "shipping": int_shipping_sector + dom_shipping_sector,
                            "road transport": ld_road_transport_sector + hd_road_transport_sector}
    dict_tech_simplification = {"heavy industry": dict_heavy_industry,
                                    "chemical industry": dict_chemical_industry,
                                    "refining industry": dict_refining,
                                    "aviation": dict_aviation_industry,
                                    "shipping": dict_shipping_industry,
                                    "road transport": dict_road_transport_industry}
    
    dict_results = {}

    sectors = list(dict_sector_grouping.keys())
    scenarios = list(model_results_dictionary.keys())
    baseline_results    = model_results_dictionary[scenarios[0]][technologies]
    subsidy_results     = model_results_dictionary[scenarios[1]][technologies]
    hba_results         = model_results_dictionary[scenarios[2]][technologies]
    mandate_results     = model_results_dictionary[scenarios[3]][technologies]

    for scenario in scenarios:
        for sector in sectors:
            dict_simplification = dict_tech_simplification[sector]
            temp = model_results_dictionary[scenario][dict_sector_grouping[sector]]
            # Rename columns in temp using dict_simplification
            temp = temp.rename(columns=dict_simplification)
            temp = temp.T.groupby(level=0).sum().T
            temp = temp.reset_index()
            temp["Scenario"] = scenario
            dict_results[(scenario, sector)] = temp

    df_road_transport = pd.DataFrame()
    df_aviation = pd.DataFrame()
    df_shipping = pd.DataFrame()

    df_heavy_industry = pd.DataFrame()
    df_chemical_industry = pd.DataFrame()
    df_refining = pd.DataFrame()

    for scenario in scenarios:
        df_road_transport = pd.concat([df_road_transport, dict_results[(scenario, "road transport")]])
        df_aviation = pd.concat([df_aviation, dict_results[(scenario, "aviation")]])
        df_shipping = pd.concat([df_shipping, dict_results[(scenario, "shipping")]])

        df_heavy_industry = pd.concat([df_heavy_industry, dict_results[(scenario, "heavy industry")]])
        df_chemical_industry = pd.concat([df_chemical_industry, dict_results[(scenario, "chemical industry")]])
        df_refining = pd.concat([df_refining, dict_results[(scenario, "refining industry")]])

    df_road_transport.set_index(["time"], inplace=True)
    df_aviation.set_index(["time","Scenario"], inplace=True)
    df_shipping.set_index(["time","Scenario"], inplace=True)
    df_heavy_industry.set_index(["time","Scenario"], inplace=True)
    df_chemical_industry.set_index(["time","Scenario"], inplace=True)
    df_refining.set_index(["time","Scenario"], inplace=True)

    fig = go.Figure(go.Scatterternary({
        "mode": "markers",
        "a": df_road_transport["Fossil"],
        "b": df_road_transport["Electric"],
        "c": df_road_transport["Hydrogen"],
        "marker": {
            "color": df_road_transport["Scenario"].map({"baseline": "black", "subsidy": "teal", "hba": "goldenrod", "mandate": "crimson"}),
            "size": 10,
        }
        
    }))

    fig.update_layout({
        "ternary": {
            "sum": 100,
            "aaxis": {"title": "Fossil", "tickangle": 0, "ticks":"outside","tickmode":"array", "tickvals":[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]},
            "baxis": {"title": "Electric", "tickangle": 45, "ticks":"outside","tickmode":"array", "tickvals":[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]},
            "caxis": {"title": "Hydrogen", "tickangle": -45, "ticks":"outside","tickmode":"array", "tickvals":[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]}
        },
    })


    fig.show()

    return None

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

    plot_figure_3(result_dictionary)

