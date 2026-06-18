import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from result_loading import result_loading_class

rl = result_loading_class()

def plot_figure_4(model_results_dictionary = dict) -> None:
    scenarios = list(model_results_dictionary.keys())
    dict_scenario_results = {}
    dict_sector_units = {}
    for main_sector in rl.sector_dict.keys():
        for sub_sector, sub_dict in rl.sector_dict[main_sector].items():
            df = pd.DataFrame()
            for scenario in scenarios:
                if sub_dict["unit"] == "GWh":
                    unit = "TWh"
                    temp = model_results_dictionary[scenario][sub_dict["stocks"]] / 1000
                else:
                    unit = sub_dict["unit"]
                    temp = model_results_dictionary[scenario][sub_dict["stocks"]]
                temp.index = model_results_dictionary[scenario].index
                temp.columns = list(map(lambda x: rl.pretty_names_technologies[x], temp.columns ))
                temp["Scenario"] = scenario
                temp = temp.reset_index()
                temp = temp[temp["time"].isin([2025,2030,2040,2050])]
                temp["time"] = temp["time"].astype(int)
                df = pd.concat([df, temp])
                dict_sector_units[(sub_sector)] = unit
            dict_scenario_results[(sub_sector)] = df

    sub_sectors = list(dict_scenario_results.keys())

    pretty_name_to_color = {
            "Grey Ammonia": "gray",
            "Blue Ammonia": "blue",
            "Green Ammonia": "forestgreen",
            "Grey Hydrogen": "gray",
            "Blue Hydrogen": "blue",
            "Green Hydrogen": "forestgreen",
            "Grey Natural Gas": "gray",
            "Blue Natural Gas": "blue",
            "Biogas": "darkgreen",
            "Hydrogen": "lightblue",
            "Grey Methanol": "gray",
            "Blue Methanol": "blue",
            "Biogenic Methanol": "darkgreen",
            "eMethanol": "orange",
            "Coal BF BOF": "gray",
            "Coal BF BOF CCS": "blue",
            "NG DRI-EAF": "lightgray",
            "H$_2$ DRI-EAF": "lightblue",
            "Fossil Naphtha": "gray",
            "Biogenic Naphtha": "darkgreen",
            "Synthetic Naphtha": "orange",
            "Fossil Kerosene": "gray",
            "Synthetic Kerosene": "orange",
            "Biogenic Kerosene": "darkgreen",
            "HFO": "gray",
            "NH$_3$": "firebrick",
            "Bio-MeOH": "darkgreen",
            "Battery-Electric": "gold",
            "H$_2$ FC": "lightblue",
            "Diesel ICE": "gray",
            "Battery EV": "gold",
            "H$_2$ FC EV": "lightblue",
                                }

    fig = plt.figure()
    fig.set_figheight(8)
    fig.set_figwidth(12)

    for i, sub_sector in enumerate(sub_sectors):
        ax = fig.add_subplot(4, 3, i+1)
        df = dict_scenario_results[sub_sector]
        if sub_sector in ["domestic shipping", "heavy duty"]:
            print(sub_sector)
            print(df[df["time"] == 2050])

        df.set_index(["time","Scenario"], inplace=True)
        df.sort_index(level=["time", "Scenario"], ascending=[True, True], inplace=True,
                      key=lambda x: (pd.to_numeric(x) if x.name == "time" else pd.CategoricalIndex(x, categories=scenarios, ordered=True)))
        techs = df.columns
        colors = [pretty_name_to_color[tech] for tech in techs]
        df.plot(kind='bar',stacked=True,ax=ax, color=colors, width=0.9)
        ax.set_xlabel("")
        unit = dict_sector_units[sub_sector]
        ax.set_ylabel(unit)
        ax.tick_params(axis='x', bottom=False, labelbottom=False)  # Hide x-axis labels
        sec10 = ax.secondary_xaxis(location=0)
        sec10.set_xticks([-0.5, 3.5, 7.5, 11.5, 15.5],labels=[])
        sec10.tick_params('x', length=10, width=1)
        if i >= 9: # Only adjust the x-axis labels for the first 9 subplots
            sec12 = ax.secondary_xaxis(location=0)
            sec12.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],labels=['Bas','Pre','Auc','Man',
                                                                                            'Bas','Pre','Auc','Man',
                                                                                            'Bas','Pre','Auc','Man',
                                                                                            'Bas','Pre','Auc','Man'], fontsize='small', rotation=-45)
            sec20 = ax.secondary_xaxis(location=0)
            sec20.set_xticks([1.5, 5.5, 9.5, 13.5],labels=['2025', '2030', '2040', '2050'])
            sec20.tick_params('x', length=0, width=1, pad=25)
        else:
            sec12 = ax.secondary_xaxis(location=0)
            sec12.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],labels=['','','','','','','','','','','','','','','',''], fontsize='small')
        # Reduce the size of the legend
        ax.legend(loc='lower left', fontsize='small', title=rl.pretty_names[sub_sector], title_fontproperties={'weight': 'bold', 'size': 'small'})
        ax.grid(False)      
    fig.subplots_adjust(hspace=0.08, wspace=0.21, bottom=0.07, top=0.99, left=0.07, right=0.99)
    plt.show()

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
    plot_figure_4(result_dictionary)