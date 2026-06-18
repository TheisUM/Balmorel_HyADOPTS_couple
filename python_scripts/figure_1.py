import pandas as pd
import matplotlib.pyplot as plt

def plot_figure_1(model_results_dictionary = dict) -> None:
    scenarios = list(model_results_dictionary.keys())
    hydrogen_demands = ['grey hydrogen TWH', 'blue hydrogen TWH', 'INDUSTRY TWH', 'TRANSPORTATION TWH']
    green_hydrogen_demands = ['INDUSTRY TWH', 'TRANSPORTATION TWH']
    sector_hydrogen_demands = ['refinery grey hydrogen demand', 'fertilizer grey hydrogen demand',
                                'refinery blue hydrogen demand','fertilizer blue hydrogen demand',
                                'naphtha hydrogen demand', 'refinery hydrogen demand','fertilizer hydrogen demand','steel hydrogen demand','high temperature hydrogen demand','MeOH hydrogen demand',
                                'light duty hydrogen demand','heavy duty hydrogen demand','domestic shipping hydrogen demand','international shipping hydrogen demand','domestic aviation hydrogen demand','international aviation hydrogen demand',]
    
    dict_sector_results = {}
    dict_results = {}
    for scenario in scenarios:
        df = model_results_dictionary[scenario][sector_hydrogen_demands] / 1e6 # Convert from TWh to MtH2
        dict_results[(scenario)] = df[df.index.get_level_values("time").isin([2022, 2025, 2030, 2035, 2040, 2045, 2050])].sum(axis=1)
        df.columns = [col.replace(" hydrogen demand", "") for col in df.columns]
        df["Scenario"] = scenario
        df = df.reset_index()
        df = df.set_index(["time","Scenario"])
        dict_sector_results[(scenario)] = df[df.index.get_level_values("time").isin([2030, 2040, 2050])]

    # df_green = model_results_dictionary[keys[3]][green_hydrogen_demands].sum(axis=1) / 33.33 # Convert from TWh to MtH2
    # print(df_green.iloc[-1])

    colors = ['grey', 'lightgrey',
            'darkblue', 'lightblue',
            'darkgreen','forestgreen','limegreen','seagreen','mediumseagreen', 'lightgreen',
            'maroon','firebrick','red','indianred','salmon','mistyrose']

    fig = plt.figure()
    fig.set_figheight(4)
    fig.set_figwidth(10)

    y_max = 70

    ax1 = plt.subplot2grid((1,2), (0,0), colspan=1)
    dict_results[scenarios[0]].plot(kind='line', color='black', linewidth=3, ax=ax1, legend=True)
    # print(dict_results[scenarios[0]].iloc[-1])
    dict_results[scenarios[1]].plot(kind='line', color='teal', linewidth=3, ax=ax1, legend=False)
    # print(dict_results[scenarios[1]].iloc[-1])
    dict_results[scenarios[2]].plot(kind='line', color='goldenrod', linewidth=3, ax=ax1, legend=False)
    # print(dict_results[scenarios[2]].iloc[-1])
    dict_results[scenarios[3]].plot(kind='line', color='crimson', linewidth=3, ax=ax1, legend=False)
    # print(dict_results[scenarios[3]].iloc[-1])
    ax1.set_title("a) Total demand projection", fontsize=10, loc='left')
    ax1.set_xlabel("")
    ax1.set_ylabel("Hydrogen demand (MtH$_2$/y)", fontsize=10)
    ax1.set_ylim(0, y_max)
    ax1.set_xlim(2025, 2050)
    ax1.grid(True)
    ax1.legend(labels=["Baseline (1)", "Premium (2)", "Auction (3)", "Mandate (4)"],loc='upper left', fontsize='small',frameon=True)

    ax2 = plt.subplot2grid((1,2), (0,1), colspan=1)
    
    # df_plotting = pd.concat([df_sector_base, df_sector_subsidy, df_sector_hba, df_sector_mandate])
    df_plotting = pd.concat(dict_sector_results.values())
    df_plotting.sort_index(level=["time", "Scenario"], ascending=[True, True], inplace=True,
                      key=lambda x: (pd.to_numeric(x) if x.name == "time" else pd.CategoricalIndex(x, categories=scenarios, ordered=True)))
    # df_plotting.sort_index(level='Scenario', ascending=True, inplace=True)
    # df_plotting.sort_index(level='Time', ascending=True, inplace=True)
    df_plotting.plot(kind='bar', stacked=True, color=colors, width=0.8, ax=ax2, legend=True,zorder=10)
    print(df_plotting.iloc[8,:])
    ax2.set_title("b) Sectoral hydrogen demand", fontsize=10, loc='left')
    ax2.set_xlabel("")
    ax2.set_ylabel("")
    ax2.tick_params(axis='x', bottom=False, labelbottom=False)  # Hide x-axis labels
    sec2 = ax2.secondary_xaxis(location=0)
    sec2.set_xticks([-0.5, 3.5, 7.5, 11.5, 15.5],labels=[])
    sec2.tick_params('x', length=10, width=1)
    # Add a scenario indicator for the first year only in all plots
    sec21 = ax2.secondary_xaxis(location=0)
    sec21.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],labels=['Bas','Pre','Auc','Man']*3, fontsize='small', rotation=90)
    sec22 = ax2.secondary_xaxis(location=0)
    sec22.set_xticks([1.5, 5.5, 9.5],labels=['2030', '2040', '2050'])
    sec22.tick_params('x', length=0, width=1, pad=25)
    ax2.set_ylim(0, y_max)
    ax2.grid(True, axis='y')
    handles, labels = ax2.get_legend_handles_labels()
    ax2.legend(handles[::-1], labels[::-1], loc='upper left', bbox_to_anchor=(1, 1), fontsize='small', ncols=1, frameon=False)
    
    fig.subplots_adjust(hspace=0.3, wspace=0.15, bottom=0.12, top=0.93, left=0.08, right=0.77)
    plt.show()

    # print(dict_sector_results[scenarios[3]].iloc[-1])
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

    plot_figure_1(result_dictionary)