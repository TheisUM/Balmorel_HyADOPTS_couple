import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from python_scripts.result_loading import result_loading_class
import pandas as pd
import seaborn as sns
import numpy as np
import pysd

sns.set_theme(style="whitegrid")
sns.set_palette("colorblind")
sns.set_context("paper", font_scale=1.5)

# set the default font size for all plots to 14
#plt.rcParams['font.size'] = 14
# set all other font sizes to 12
plt.rcParams['font.size'] = 12
# set legend fontsize to 14
plt.rcParams['legend.fontsize'] = 12
# set the font weight of the legend to bold
plt.rcParams['legend.title_fontsize'] = 14
# set the font size of the x and y labels to 14
plt.rcParams['axes.labelsize'] = 12
# set the font weight of the x and y labels to bold
plt.rcParams['axes.labelweight'] = 'bold'
# set the font size of the x and y ticks to 12
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
# set the font size of the title to 16
plt.rcParams['axes.titlesize'] = 14
# set the font weight of the title to bold
plt.rcParams['axes.titleweight'] = 'bold'

rl = result_loading_class()

def save_figure(fig:plt.Figure,
                filename:str = "",
                dpi:int = 300,
                ):
    """ Save the figure with high resolution and tight layout.
    If no filename is provided, the figure will be shown instead. """
    # Save the figure with high resolution and tight layout
    if len(filename) > 0:
        filepath = "results/" + filename + ".png"
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
        print(f"Figure saved at {filepath}")
        plt.close(fig)  # Close the figure to free up memory
    else:
        plt.show()  # Show the figure if no filename is provided

def plot_carbon_taxes(dl, # data_loading_class
                      filename:str = "",
                      dpi:int = 300
                      ):
    fig, ax = plt.subplots(figsize=(8,4))
    ax.plot(dl.load_carbon_taxes(), color = 'black', label="Carbon tax (WEO Forecast)", lw=3, linestyle='dashed',)
    ax.plot(dl.load_carbon_taxes(**{"discount_rate":0.08}), color = 'black', label="Carbon tax (Present Cost)", lw=3)
    ax.set_ylabel(r"€/t$\,$CO$_\mathbf{2}$")
    ax.set_xlabel("Year")
    ax.legend(loc='center', bbox_to_anchor=(0.5, -0.25), ncol=2, handlelength=2.3)
    ax.set_xlim(2022, 2050)
    ax.set_ylim(50, 250)

    save_figure(fig, filename=filename, dpi=dpi)

def plot_electrolyzer_capex(model_results:pd.DataFrame,
                            filename:str = "",
                            dpi:int = 300
                            ):
    fig, ax = plt.subplots(figsize=(7,4))
    ax.plot(model_results["AEC CAPEX"], label="Electrolyzer CAPEX", color='black', lw=2)
    ax.set_ylabel(r"€$_{\mathbf{2020}}$/kW$_\mathbf{e}$", fontsize=12)
    ax.set_xlabel("Year", fontsize=12)
    ax.set_xlim(2022, 2051)
    ax.set_ylim(0, 2000)
    for yr in [2025,2030,2050]:
        ax.scatter(yr, model_results["AEC CAPEX"].loc[yr], facecolors='none', edgecolors='r', s=150, linewidths=2)
        print(yr, " electrolyzer capital cost: ", model_results["AEC CAPEX"].loc[yr], "€/kW")
    
    save_figure(fig, filename=filename, dpi=dpi)

def plot_sector_production(model_results:pd.DataFrame,
                           filename = "",
                           dpi:int = 300,
                           ):
    # Visualize the energy consumption in the different sectors using stacked area plots.
    # Do this in two separate grid plots. One for industry and one for transport. Use the dictionary sector_dict to get the sectors for each category.
    for main_sector in rl.sector_dict.keys():
        fig, axs = plt.subplots(2, 3, figsize=(12, 6))
        #fig.suptitle(main_sector + " activity projections")
        fig.tight_layout(h_pad=2.0, w_pad=1.0)  # Add padding between subplots
        for i, (sub_sector, sub_dict) in enumerate(rl.sector_dict[main_sector].items()):
            if sub_dict["unit"] == "GWh":
                unit = "TWh"
                df = model_results[sub_dict["stocks"]] / 1000
            else:
                unit = sub_dict["unit"]
                df = model_results[sub_dict["stocks"]]
            df.index = model_results.index
            df.columns = list(map(lambda x: rl.pretty_names_technologies[x], df.columns ))
            ax = axs[i%2, i//2]
            df.plot.area(ax=ax, color=["gray", "blue", "green", "lightblue"])
            ax.title.set_text(rl.pretty_names[sub_sector])
            ax.title.set_fontsize(12)
            ax.title.set_fontweight('bold')
            ax.set_xlabel("")
            ax.set_ylabel(unit)
            # Reduce the font size of the axis labels
            ax.xaxis.label.set_fontsize(10)
            ax.xaxis.label.set_fontweight('bold')
            ax.yaxis.label.set_fontsize(10)
            # Reduce the size of the tick labels
            ax.tick_params(axis='both', which='major', labelsize=10)
            # Reduce the size of the legend
            ax.legend(loc='lower left', fontsize=10)
            ax.grid(False)
            
            ax.autoscale(enable=True, axis='both', tight=True)  # Adjust the axis limits to fit the data        
        # fig.suptitle(filename + f"_{main_sector}")
        save_figure(fig, filename + f"_{main_sector}" if len(filename) > 0 else "", dpi=dpi)

def plot_system_emissions(model_results:pd.DataFrame,
                            filename:str = "",
                            dpi:int = 300,
                            write_df:bool = False,
                            cumulative_emissions:bool = False,
                            ):
    # Prepare the emission sources for industry and transportation
    df_yearly = model_results[["naphtha emissions", "refinery emissions", "fertilizer emissions", "steel emissions", "high temperature emissions", "MeOH emissions",
                        "international shipping emissions", "heavy duty emissions", "international aviation emissions", "domestic shipping emissions", "domestic aviation emissions"]]
    time = model_results["TIME STEP"].iloc[0] # Convert time step size to years (currently 1/20th of a year)
    
    df_yearly = (df_yearly / 1e6) # Convert to Mt CO2/year
    df_cumulative = df_yearly.cumsum() * time / 1e3  # Convert to Gt CO2 and account for time step size

    if cumulative_emissions:
        df = df_cumulative
    else:
        df = df_yearly

    df.index = model_results.index
    df = df.sort_index()
    
    # Create a stacked area plot for the emissions
    fig, ax = plt.subplots(figsize=(6, 4))
    df.index = model_results.index
    df.columns = [r"Naphtha", r"Refinery", r"Fertilizer", r"Steel", r"High Temp.", r"MeOH",
                                r"International Shipping", r"Heavy Duty", r"International Aviation", r"Domestic Shipping", r"Domestic Aviation"]
    df.plot.area(ax=ax, color=["gray", "blue", "green", "orange", "red", "purple", "brown", "pink", "cyan", "magenta", "yellow", "lightgray"], alpha=0.8)

    ax.set_xlabel("Year")
    if cumulative_emissions:
        ax.set_ylabel("Gt CO$_2$ cumulative")
    else:
        ax.set_ylabel("Mt CO$_2$/year")

    ax.set_xlim(df.index[0], df.index[-1])
    ax.set_ylim(0)
    # Reduce the font size of the axis labels
    ax.set_xticks([2022, 2030, 2040, 2050])
    # Reduce the size of the legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles[::-1], labels=labels[::-1], loc='upper left')

    fig.suptitle(filename)
    save_figure(fig, filename, dpi=dpi)
    if write_df == True:
        return df_yearly, df_cumulative

def plot_sector_costs(model_results:pd.DataFrame,
                      model:pysd.py_backend.model.Model,
                      filename:str = "",
                      dpi:int = 300,
                      ):
    # Visualize the energy consumption in the different sectors using stacked area plots.
    # Do this in two separate grid plots. One for industry and one for transport. Use the dictionary sector_dict to get the sectors for each category.
    for main_sector in rl.sector_dict.keys():
        fig, axs = plt.subplots(3, 2, figsize=(8, 10))
        #fig.suptitle(main_sector + " cost projections")
        # Pad less on the x-axis
        fig.tight_layout(h_pad=2, w_pad=1.0)  # Add padding between subplots
        for i, (sub_sector, sub_dict) in enumerate(rl.sector_dict[main_sector].items()):
            placeholder = sub_dict["costs"][0].lower().replace(" ", "_")
            cost_unit = model.components.__getattribute__(placeholder).units
            df = model_results[sub_dict["costs"]]
            df.index = model_results.index
            df.columns = list(map(lambda x: rl.pretty_names_costs[x], df.columns ))
            ax = axs[i//2, i%2]
            df.plot(ax=ax, color=["gray", "blue", "green", "orange"], linewidth=2)
            ax.title.set_text(rl.pretty_names[sub_sector])
            ax.title.set_fontsize(12)
            # Set bold font for the title
            ax.title.set_fontweight('bold')
            ax.set_xlabel("")
            ax.set_ylabel(cost_unit)
            # Reduce the font size of the axis labels
            ax.xaxis.label.set_fontsize(10)
            ax.xaxis.label.set_fontweight('bold')
            ax.yaxis.label.set_fontsize(10)
            # Reduce the size of the tick labels
            ax.tick_params(axis='both', which='major', labelsize=10)
            # Reduce the size of the legend
            ax.legend(loc='best', fontsize=10)
            
            ax.autoscale(enable=True, axis='both', tight=True)  # Adjust the axis limits to fit the data
            ax.set_ylim(0)  # Adjust the axis limits to fit the data
        
        # fig.suptitle(filename + f"_{main_sector}")
        save_figure(fig, filename + f"_{main_sector}" if len(filename) > 0 else "", dpi=dpi)

def plot_hydrogen_projection(model_results:pd.DataFrame,
                             filename:str = "",
                             dpi:int = 300,
                             final_year:int = 2050,
                             step_horizontal_lines:int = 100,
                             ):
    df = model_results[['grey hydrogen TWH', 'blue hydrogen TWH', 'INDUSTRY TWH', 'TRANSPORTATION TWH',]]
    df_sub = model_results[['refinery grey hydrogen demand', 'fertilizer grey hydrogen demand',
                                'refinery blue hydrogen demand','fertilizer blue hydrogen demand',
                                'naphtha hydrogen demand', 'refinery hydrogen demand','fertilizer hydrogen demand','steel hydrogen demand','high temperature hydrogen demand','MeOH hydrogen demand',
                                'light duty hydrogen demand','heavy duty hydrogen demand','domestic shipping hydrogen demand','international shipping hydrogen demand','domestic aviation hydrogen demand','international aviation hydrogen demand',]]
    df_relative = df_sub.div(df_sub.sum(axis=1), axis=0)
    total_h2_demand = df.sum(axis=1)
    total_h2_demand_2050 = total_h2_demand.loc[final_year]
    n_horizontal_lines = (total_h2_demand_2050 - total_h2_demand_2050 % step_horizontal_lines) / step_horizontal_lines
    horizontal_lines_TWh = np.arange(step_horizontal_lines, n_horizontal_lines*step_horizontal_lines + 1, step_horizontal_lines)
    horizontal_lines_TWh = np.append(horizontal_lines_TWh,total_h2_demand_2050)
    horizontal_lines_TWh = np.append(0,horizontal_lines_TWh)
    fig, (ax1, ax3) = plt.subplots(1,2,figsize=(8, 4), gridspec_kw={'width_ratios': [5, 1]})
    df.index = model_results.index
    df.columns = [r"Grey H$_2$", r"Blue H$_2$", r"Green H$_2$ (industry)", r"Green H$_2$ (transport)",]
    df.plot.area(ax=ax1, color=["gray", "blue", "darkgreen", "limegreen"], alpha = 0.8)
    ax1.set_xlabel("Year")
    ax1.set_ylabel("TWh a$^{-1}$")
    ax1.grid(False)
    ax1.hlines(xmin=2022,xmax=2050,y=horizontal_lines_TWh, color='black', linestyle='--', linewidth=0.8,zorder=0, alpha=0.3)
    ax1.set_xlim(df.index[0], df.index[-1])
    ax1.set_ylim(0, total_h2_demand_2050)
    ax1.set_xticks([2022, 2030, 2040, 2050])
    ax1.set_yticks(np.append(0,horizontal_lines_TWh))
    ax1.tick_params(left=False)
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles=handles[::-1], labels=labels[::-1], loc='upper left', fontsize='small', frameon=False)
    df_relative.index = model_results.index
    df_relative.columns = [r"Refinery grey H$_2$", r"Fertilizer grey H$_2$",
                            r"Refinery blue H$_2$", r"Fertilizer blue H$_2$",
                            r"Naphtha green H$_2$", r"Refinery green H$_2$", r"Fertilizer green H$_2$", r"Steel green H$_2$", r"High Temp. green H$_2$", r"MeOH green H$_2$",
                            r"Light Duty green H$_2$", r"Heavy Duty green H$_2$", r"Domestic Shipping green H$_2$", r"International Shipping green H$_2$", r"Domestic Aviation green H$_2$", r"International Aviation green H$_2$",]
    colors = ['grey', 'lightgrey',
            'darkblue', 'lightblue',
            'darkgreen','forestgreen','limegreen','seagreen','mediumseagreen', 'lightgreen',
            'maroon','firebrick','red','indianred','salmon','mistyrose']
    df_relative.reset_index(inplace=True)
    df_relative = df_relative.loc[df_relative['time'] == final_year]
    df_relative.plot(x='time',ax=ax3, kind='bar', stacked=True, alpha = 1, color=colors)
    ax3.set_xlabel("")
    ax3.set_xticks([])
    ax3.set_ylabel(f"Relative share in {final_year}")
    ax3.set_ylim(0,1)
    ax3.set_yticks([])
    ax3.yaxis.set_label_position("right")
    ax3.grid(False)
    handles3, labels3 = ax3.get_legend_handles_labels()
    ax3.legend(handles=handles3[::-1],labels=labels3[::-1],loc='lower left', bbox_to_anchor=(-6.8, -0.55), fontsize='small',ncols=4, frameon=False)
    save_figure(fig, filename, dpi=dpi)

def plot_demand_curve(years_of_interest:list,
                      price_offers:pd.DataFrame,
                      quantity_offers:pd.DataFrame,
                      model_results:pd.DataFrame,
                      type_:str = "H2",
                      filename:str = "",
                      dpi:int = 300):
    # Create a staircase plot for the hydrogen price offers with the hydrogen quantity offers as the steps
    fig, axs = plt.subplots(1, len(years_of_interest), figsize=(5*len(years_of_interest),6), sharey=True)
    plt.locator_params(axis='x', nbins=5)
    fig.tight_layout(h_pad=2.0, w_pad=2.0)  # Add padding between subplots
    
    for ix, year in enumerate(years_of_interest):
        df_price = price_offers.loc[year].sort_values(ascending=False)
        
        df_quantity = quantity_offers.loc[year, df_price.index]
        df_cum_quant = df_quantity.copy()
        for i in range(1, len(df_cum_quant)):
            df_cum_quant.iloc[i] += df_cum_quant.iloc[i-1]
        df_cum_quant = pd.concat([pd.Series([0]), df_cum_quant])
        df_price = pd.concat([pd.Series([df_price.iloc[0]]), df_price])
        axs[ix].step(np.array(df_cum_quant), np.array(df_price), color='black')
        # Fill the area under the curve for every step
        for i in range(1, len(df_price)):
            sector = df_price.index[i]
            axs[ix].fill_between([df_cum_quant.iloc[i-1], df_cum_quant.iloc[i]], df_price.iloc[i], color=rl.sector_colors[sector], label=sector)
        if type_ == "H2":
            axs[ix].axhline(model_results["Green H2 cost"].loc[year], linestyle="dashed", color="black",label=r"Green H$_2$ cost")
            axs[ix].set_xlabel(r"Demand [TWh/year]")
            axs[ix].set_ylim(0,np.ceil(max(df_price))+1)
        elif type_ == "CO2":
            axs[ix].axhline(model_results["CARBON TAX"].loc[year], linestyle="dashed", color="black",label="Carbon tax")
            axs[ix].set_ylabel(r"CO$_2$ WTP [€/tCO$_2$]")
            axs[ix].set_xlabel(r"Emissions [Mt CO$_2$/year]")
        axs[ix].set_title(str(year))
        axs[ix].grid(axis='y', alpha=0.5)
        axs[ix].set_xlim(0)
    
    if type_ == "H2":
        axs[0].set_ylabel(r"H$_2$ WTP [€/kg]")
        l_ix = len(years_of_interest) - 1
        ax2 = axs[l_ix].twinx()
        ax2.set_yticks((axs[l_ix].get_yticks()*120/3.6).round())
        ax2.set_ylabel(r"H$_2$ WTP [€/MWh]")
        ax2.grid(False)
        axs[l_ix].tick_params(left = False, right = False)
        ax2.tick_params(left = False, right = False)
    fig.tight_layout(h_pad=2.0, w_pad=0.8) 

    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, [rl.pretty_names[s] if s in rl.pretty_names.keys() else s for s in labels], loc='upper center', bbox_to_anchor=(0.5, 0.03), ncol=5)
    
    save_figure(fig, filename, dpi=dpi)

def plot_study_comparison(mc_results_melt:pd.DataFrame,
                          study_results:pd.DataFrame,
                          filename:str = "",
                          dpi:int = 300,
                          ):
    fig, ax = plt.subplots(figsize=(6,4))

    base = sns.lineplot(data = mc_results_melt, x='Year', y='TWh', palette=sns.color_palette(['red']), hue='Subsidy', alpha=0.7, errorbar='sd', legend=True, ax=ax)

    box  = sns.boxplot( data = study_results, y="Scope", x="Year", color="blue", positions=[2030, 2040, 2050], width=1, label = "Study results", showfliers=False, ax=ax, fill=False)
    handles, labels = ax.get_legend_handles_labels()

    ax.legend(handles, ["Model projection spread", "Other study projections",
                        "Other studies (Power)", "Other studies (Industry)",
                        "Other studies (Transport)"], loc='upper left')

    #ax.set_title("Monte Carlo analysis of hydrogen demand")
    ax.set_xlabel("Year")
    ax.set_ylabel("TWh/year")
    ax.set_xlim(2022, 2051)
    ax.set_ylim(0, 1750)
    ax.set_xticks([2022, 2030, 2040, 2050])
    ax.set_xticklabels([2022, 2030, 2040, 2050])
    ax.set_yticks(ax.get_yticks())
    ax.set_yticklabels(ax.get_yticklabels())
    # Create twinx to have two y-axes with different scales
    ax2 = ax.twinx()
    ax2.set_yticks(ax.get_yticks()/120*3.6)
    ax2.set_ylabel("MT/year")
    ax2.grid(False)
    ax.tick_params(left = False)
    ax2.tick_params(right = False)

    save_figure(fig, filename, dpi=dpi)

def plot_subsidized_demand_comparison(results:dict,
                                      study_results:pd.DataFrame,
                                      filename:str = "",
                                      dpi:int = 300,
                                      ):
    # Plot the hydrogen demand for different subsidy sizes and compare it to the study results
    fig, ax = plt.subplots(figsize=(8,4))

    for ix, i in enumerate(results):
        if i == "base":
            label = "No subsidy"
            color = "red"
        else:
            label = str(float(i.split(" = ")[1])) + " €/kg subsidy"
            color = sns.color_palette("colorblind")[ix]

        ax.plot(results[i]["SCOPE TWH"], label = label, color=color)

    box_alpha = 0.4
    box=sns.boxplot(data = study_results,
                    y="Scope", 
                    x="Year", 
                    color="blue", 
                    positions=[2030, 2040, 2050], 
                    width=1, 
                    label = "Study results", 
                    showfliers=False, 
                    ax=ax, 
                    fill=False, 
                    **{'boxprops': {'alpha': box_alpha},
                       'flierprops': {'alpha': box_alpha},
                       'medianprops': {'alpha': box_alpha},
                       'meanprops': {'alpha': box_alpha},
                       'capprops': {'alpha': box_alpha},
                       'whiskerprops': {'alpha': box_alpha},
                       })

    handles, labels = ax.get_legend_handles_labels()
    labels[-1] = "Other study projections"
    ax.legend(handles, labels, loc='center', fontsize=12, bbox_to_anchor=(0.5, -0.25), ncols=3)

    plt.axvline(x=2025, color='black', linestyle='--', alpha=0.2)
    plt.axvline(x=2035, color='black', linestyle='--', alpha=0.2)
    plt.fill_between([2025, 2035], 0, 2500, color='grey', alpha=0.1)

    ax.set_xlabel("Year")
    ax.set_ylabel("TWh/year")
    ax.set_xlim(2022, 2051)
    ax.set_ylim(0, 2000)
    ax.set_xticks([2022, 2030, 2040, 2050])
    ax.set_xticklabels([2022, 2030, 2040, 2050])
    ax.set_yticks(ax.get_yticks())
    ax.set_yticklabels(ax.get_yticklabels())
    ax2 = ax.twinx()
    ax2.set_yticks((ax.get_yticks()/120*3.6).round())
    ax2.set_ylabel("MT/year")
    ax2.grid(False)
    ax.tick_params(left = False)
    ax2.tick_params(right = False)
    ax.annotate('Subsidy period', xy=(2027, 1800), xytext=(2027, 1800), fontsize=12, fontstyle='italic')

    save_figure(fig, filename, dpi=dpi)

def plot_subsidized_demand_curves(results:dict,
                                  h2_price_offers:dict[pd.DataFrame],
                                  h2_quantity_offers:dict[pd.DataFrame],
                                  filename:str = "",
                                  dpi:int = 300,
                                  ):
    """ Create a staircase plot for the hydrogen price offers with the hydrogen quantity offers as the steps.
    This function also plots the green hydrogen cost range as a filled area between the two dashed lines. """
    # Create a staircase plot for the hydrogen price offers with the hydrogen quantity offers as the steps
    fig, ax = plt.subplots(figsize=(8,4))
    year = 2025.05
    last = len(list(results.keys())) - 1
    h2_cost_bounds = [0, 0]
    max_demand = 0
    max_wtp = -1000
    for ix, ct in enumerate(results.keys()):
        df_price = h2_price_offers[ct].loc[year].sort_values(ascending=False)
        
        df_quantity = h2_quantity_offers[ct].loc[year, df_price.index]
        df_cum_quant = df_quantity.copy()
        for i in range(1, len(df_cum_quant)):
            df_cum_quant.iloc[i] += df_cum_quant.iloc[i-1]
        df_cum_quant = pd.concat([pd.Series([0]), df_cum_quant])
        df_price = pd.concat([pd.Series([df_price.iloc[0]]), df_price])
        if ct == "base":
            label = "No subsidy"
            color = "red"
        else:
            label = str(float(ct.split(" = ")[1])) + " €/kg subsidy"
            color = sns.color_palette("colorblind")[ix]
        ax.step(np.array(df_cum_quant), np.array(df_price), label=label, color=color)
        if ix == 0:
            h2_cost_bounds[0] = results[ct]["Green H2 cost"].loc[year]
        elif ix == last:
            h2_cost_bounds[1] = results[ct]["Green H2 cost"].loc[year]
        if max(df_cum_quant) > max_demand: max_demand = max(df_cum_quant)
        if max(df_price) > max_wtp: max_wtp = max(df_price)

    ax.axhline(y=h2_cost_bounds[0], color='black', linestyle='--', alpha=0.2)
    ax.axhline(y=h2_cost_bounds[1], color='black', linestyle='--', alpha=0.2)
    ax.fill_between([0, 2000], h2_cost_bounds[0], h2_cost_bounds[1], color='grey', alpha=0.1)

    ax.set_ylabel(r"€/kg")
    ax.set_xlabel(r"TWh/year")
    ax.set_ylim(0, np.ceil(max_wtp)+1)
    #ax.set_title(str(int(year)) + " hydrogen demand curves")
    ax.grid(axis='y', alpha=0.5)
    ax.set_xlim(0, 2000)

    ax.legend(loc='center', bbox_to_anchor=(0.5, -0.25), ncols=3)

    ax2 = ax.twinx()
    ax2.set_yticks((ax.get_yticks()*120/3.6).round())
    ax2.grid(False)
    ax2.set_ylabel(r"€/MWh")
    ax.tick_params(left = False)
    ax2.tick_params(right = False)

    ax.annotate("Green hydrogen cost range", xy=(1100, np.mean(h2_cost_bounds)), xytext=(900, np.mean(h2_cost_bounds)*0.97), fontsize=12, fontstyle='italic')

    print("2035 levelized H2 production cost without subsidies: \t", round(h2_cost_bounds[0],3), "€/kg")
    print("2035 levelized H2 production cost with 3€/kg subsidies:\t", round(h2_cost_bounds[1],3), "€/kg")

    save_figure(fig, filename, dpi=dpi)

def plot_hydrogen_subsidy_costs(results:dict,
                                filename:str = "",
                                dpi:int = 300,
                                ):
    fig, ax = plt.subplots(figsize=(8,4))

    for ix, i in enumerate(results):
        if i == "base":
            continue
        else:
            label = str(float(i.split(" = ")[1])) + " €/kg subsidy"
            color = sns.color_palette("colorblind")[ix]
        print("Total subsidy cost for " + label + " in 2050: \tB€", round(results[i]["total subsidy cost"].loc[2050], 2))
        ax.plot(results[i]["subsidy payout"], label = label, color=color)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='center', bbox_to_anchor=(0.5, -0.25), ncols=2)

    plt.axvline(x=2025, color='black', linestyle='--', alpha=0.2)
    plt.axvline(x=2045, color='black', linestyle='--', alpha=0.2)
    plt.fill_between([2025, 2045], 0, 200, color='grey', alpha=0.1)

    ax.set_xlabel("Year")
    ax.set_ylabel("B€/year")
    ax.set_xlim(2022, 2050)
    ax.set_ylim(0,200)
    ax.set_xticks([2022, 2025, 2035, 2045, 2050])
    ax.set_xticklabels([2022, 2025, 2035, 2045, 2050])
    ax.set_yticks(ax.get_yticks())
    ax.set_yticklabels(ax.get_yticklabels())
    ax.tick_params(left = False)
    ax.grid(False)
    ax.grid(axis='y', alpha=0.5)
    ax.annotate('Period with\nactively subsidized\nelectrolysis units', xy=(2026, 110), xytext=(2026, 110), fontsize=12, fontstyle='italic')

    save_figure(fig, filename, dpi=dpi)

def plot_mc_parameter_distributions(mc_vars:dict,
                                    basemodel:pysd.py_backend.model.Model,
                                    filename:str = "",
                                    dpi:int = 300,
                                    ):
    fig, axs = plt.subplots(2, 4, figsize=(14, 8), sharey=True)
    fig.tight_layout(w_pad=1.0, h_pad=3)  # Add padding between subplots
    #fig.suptitle("Parameter distributions for Monte Carlo analysis")
    for ix, (param, values) in enumerate(mc_vars.items()):
        ax = axs[ix//4, ix%4]
        scaler = 1
        if values[2] == '%':
            scaler = 100
        if values[2] == '€/MWh':
            scaler = 40
        ax.axvline(basemodel[param]*scaler, lw= 3, color='r', linestyle='--', label='Base case')
        ax.plot(values[0]*scaler, values[1], lw=5, alpha=0.6)
        ax.set_title(values[3], fontsize=14, fontweight='bold')
        ax.set_yticks(ax.get_yticks())
        ax.set_yticklabels("", fontsize=14)
        ax.set_xlabel(values[2], fontsize=14, fontweight='normal')
        ax.set_xlim(np.min(values[0])*scaler, np.max(values[0])*scaler)
        ax.set_ylim(0)
        ax.grid(False)
        
    axs[0,0].set_ylabel("Density", fontsize=14,fontweight='normal')
    axs[1,0].set_ylabel("Density", fontsize=14,fontweight='normal')
    axs[1,0].legend([Line2D([],[],color='r',lw=3,linestyle='--')],['Base case values'], loc='center', fontsize=14, bbox_to_anchor=(2.25, -0.2))

    save_figure(fig, filename=filename, dpi=dpi)

if __name__ == "__main__":
    pass