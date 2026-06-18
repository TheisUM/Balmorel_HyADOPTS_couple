import pysd
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import data_loading

# Function to plot the results of the model which expects two dict runs as input
def plot_shipping_results(run1, run2):
    run1_name = list(run1.keys())[0]
    run2_name = list(run2.keys())[0]
    run1 = run1[run1_name]
    run2 = run2[run2_name]

    fig, axs = plt.subplots(2, 2, figsize=(10, 10))
    ax1 = axs[0, 0]
    ax2 = axs[0, 1]
    ax3 = axs[1, 0]
    ax4 = axs[1, 1]

    # PLot run 1's consumption
    ax1.plot(run1.index, run1["check"], label="Total consumption modelled", linestyle='-', color='grey')
    ax1.plot(run1.index, run1["int shipping consumption"], label="Total consumption", linestyle='--', color='grey')
    ax1.plot(run1.index, run1["HFO shipping consumption"], label="HFO", linestyle='-', color='black')
    ax1.plot(run1.index, run1["NH3 shipping consumption"], label="NH3", linestyle='-', color='blue')
    ax1.plot(run1.index, run1["MeOH shipping consumption"], label="MeOH", linestyle='-', color='green')
    ax1.title.set_text(f"{run1_name} - Consumption")

    # Plot run 2's consumption
    ax2.plot(run2.index, run2["check"], label="Total consumption modelled", linestyle='-', color='grey')
    ax2.plot(run2.index, run2["int shipping consumption"], label="Total consumption", linestyle='--', color='grey')
    ax2.plot(run2.index, run2["HFO shipping consumption"], label="HFO", linestyle='-', color='black')
    ax2.plot(run2.index, run2["NH3 shipping consumption"], label="NH3", linestyle='-', color='blue')
    ax2.plot(run2.index, run2["MeOH shipping consumption"], label="MeOH", linestyle='-', color='green')
    ax2.title.set_text(f"{run2_name} - Consumption")
    
    # PLot run 1's costs
    ax3.plot(run1.index, run1["HFO cost"]*1000, label="HFO", linestyle='-', color='black')
    ax3.plot(run1.index, run1["NH3 cost"]*1000, label="NH3", linestyle='-', color='blue')
    ax3.plot(run1.index, run1["MeOH cost"]*1000, label="MeOH", linestyle='-', color='green')
    ax3.title.set_text(f"{run1_name} - Costs")

    # Plot run 2's costs
    ax4.plot(run2.index, run2["HFO cost"]*1000, label="HFO", linestyle='-', color='black')
    ax4.plot(run2.index, run2["NH3 cost"]*1000, label="NH3", linestyle='-', color='blue')
    ax4.plot(run2.index, run2["MeOH cost"]*1000, label="MeOH", linestyle='-', color='green')
    ax4.title.set_text(f"{run2_name} - Costs")

    # Set labels
    ax1.set_xlabel("Year")
    ax2.set_xlabel("Year")
    ax3.set_xlabel("Year")
    ax4.set_xlabel("Year")

    ax1.set_ylabel("Shipping consumption [GWh]")
    ax2.set_ylabel("Shipping consumption [GWh]")
    ax3.set_ylabel("Price [€/GJ]")
    ax4.set_ylabel("Price [€/GJ]")

    # Plot legend in each subplot
    ax1.legend(loc='best')
    ax2.legend(loc='best')
    ax3.legend(loc='best')
    ax4.legend(loc='best')

    for ax in axs.flatten():
        ax.grid(alpha=0.5)

    plt.show()

# Function to plot the costs of the model which expects two dict runs as input
def plot_shipping_costs(run1, run2):
    run1_name = list(run1.keys())[0]
    run2_name = list(run2.keys())[0]
    run1 = run1[run1_name]
    run2 = run2[run2_name]

    fig, axs = plt.subplots(2, 2, figsize=(10, 10))
    ax1 = axs[0, 0]
    ax2 = axs[0, 1]
    ax3 = axs[1, 0]
    ax4 = axs[1, 1]

    # Plot run 1's investments
    ax1.plot(run1.index, run1["HFO investment level"], label="HFO", linestyle='-', color='black')
    ax1.plot(run1.index, run1["NH3 investment level"], label="NH3", linestyle='-', color='blue')
    ax1.plot(run1.index, run1["MeOH investment level"], label="MeOH", linestyle='-', color='green')
    ax1.title.set_text(f"{run1_name} - Investments")

    # Plot run 2's investments
    ax2.plot(run2.index, run2["HFO investment level"], label="HFO", linestyle='-', color='black')
    ax2.plot(run2.index, run2["NH3 investment level"], label="NH3", linestyle='-', color='blue')
    ax2.plot(run2.index, run2["MeOH investment level"], label="MeOH", linestyle='-', color='green')
    ax2.title.set_text(f"{run2_name} - Investments")

    # Plot run 1's prices
    ax3_2 = ax3.twinx()
    ax3_2.plot(run1.index, run1["carbon_tax"], label="CO2 tax", linestyle='-', color='grey')
    ax3.plot(run1.index, run1["oil_price"], label="Oil price", linestyle='-', color='black')
    ax3.plot(run1.index, run1["biomass_price"], label="Biomass price", linestyle='-', color='green')
    ax3.plot(run1.index, run1["hydrogen_price"]/0.12, label="H2 price", linestyle='-', color='blue')
    ax3.title.set_text(f"{run1_name} - Prices")

    # Plot run 2's prices
    ax4_2 = ax4.twinx()
    ax4_2.plot(run2.index, run2["carbon_tax"], label="CO2 tax", linestyle='-', color='grey')
    ax4.plot(run2.index, run2["oil_price"], label="Oil price", linestyle='-', color='black')
    ax4.plot(run2.index, run2["biomass_price"], label="Biomass price", linestyle='-', color='green')
    ax4.plot(run2.index, run2["hydrogen_price"]/0.12, label="H2 price", linestyle='-', color='blue')
    ax4.title.set_text(f"{run2_name} - Prices")

    # Set labels
    ax1.set_xlabel("Year")
    ax2.set_xlabel("Year")
    ax3.set_xlabel("Year")
    ax4.set_xlabel("Year")

    ax1.set_ylabel("Investment level [fraction]")
    ax2.set_ylabel("Investment level [fraction]")
    ax3.set_ylabel("Price [€/GJ]")
    ax3_2.set_ylabel("Price [€/tCO2]", color='grey')
    ax4.set_ylabel("Price [€/GJ]")
    ax4_2.set_ylabel("Price [€/tCO2]", color='grey')
    
    # Collect legend handles and labels in each subplot
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    h3, l3 = ax3.get_legend_handles_labels()
    h4, l4 = ax4.get_legend_handles_labels()
    h3_2, l3_2 = ax3_2.get_legend_handles_labels()
    h4_2, l4_2 = ax4_2.get_legend_handles_labels()

    # Plot legend in each subplot
    ax1.legend(h1, l1, loc='best')
    ax2.legend(h2, l2, loc='best')
    ax3.legend(h3+h3_2, l3+l3_2, loc='best')
    ax4.legend(h4+h4_2, l4+l4_2, loc='best')

    for ax in axs.flatten():
        ax.grid(alpha=0.5)

    plt.show()

def plot_fertilizer_results(run1, run2):
    run1_name = list(run1.keys())[0]
    run2_name = list(run2.keys())[0]
    run1 = run1[run1_name]
    run2 = run2[run2_name]

    fig, axs = plt.subplots(2, 2, figsize=(10, 10))
    ax1 = axs[0, 0]
    ax2 = axs[0, 1]
    ax3 = axs[1, 0]
    ax4 = axs[1, 1]

    # PLot run 1's consumption
    ax1.plot(run1.index, run1["check0"], label="Total consumption modelled", linestyle='-', color='black')
    ax1.plot(run1.index, run1["NH3 fertilizer consumption"], label="Total consumption", linestyle='--', color='black')
    ax1.plot(run1.index, run1["Grey NH3"], label="Grey", linestyle='-', color='grey')
    ax1.plot(run1.index, run1["Blue NH3"], label="Blue", linestyle='-', color='blue')
    ax1.plot(run1.index, run1["Green NH3"], label="Green", linestyle='-', color='green')
    ax1.title.set_text(f"{run1_name} - Production")

    # Plot run 2's consumption
    ax2.plot(run2.index, run2["check0"], label="Total consumption modelled", linestyle='-', color='black')
    ax2.plot(run2.index, run2["NH3 fertilizer consumption"], label="Total consumption", linestyle='--', color='black')
    ax2.plot(run2.index, run2["Grey NH3"], label="Grey NH3", linestyle='-', color='grey')
    ax2.plot(run2.index, run2["Blue NH3"], label="Blue NH3", linestyle='-', color='blue')
    ax2.plot(run2.index, run2["Green NH3"], label="Green NH3", linestyle='-', color='green')
    ax2.title.set_text(f"{run2_name} - Production")
    
    # PLot run 1's costs
    ax3.plot(run1.index, run1["Grey H2 cost"]/1000, label="Grey H2", linestyle='-', color='black')
    ax3.plot(run1.index, run1["Blue H2 cost"]/1000, label="Blue H2", linestyle='-', color='blue')
    ax3.plot(run1.index, run1["Green H2 cost"]/1000, label="Green H2", linestyle='-', color='green')
    ax3.title.set_text(f"{run1_name} - Hydrogen Costs")

    # Plot run 2's
    ax4.plot(run2.index, run2["Grey H2 cost"]/1000, label="Grey H2", linestyle='-', color='black')
    ax4.plot(run2.index, run2["Blue H2 cost"]/1000, label="Blue H2", linestyle='-', color='blue')
    ax4.plot(run2.index, run2["Green H2 cost"]/1000, label="Green H2", linestyle='-', color='green')
    ax4.title.set_text(f"{run2_name} - Hydrogen Costs")

    # Set labels
    ax1.set_xlabel("Year")
    ax2.set_xlabel("Year")
    ax3.set_xlabel("Year")
    ax4.set_xlabel("Year")

    ax1.set_ylabel("Fertilizer production [MT]")
    ax2.set_ylabel("Fertilizer production [MT]")
    ax3.set_ylabel("Price [€/kg]")
    ax4.set_ylabel("Price [€/kg]")

    # Plot legend in each subplot
    ax1.legend(loc='best')
    ax2.legend(loc='best')
    ax3.legend(loc='best')
    ax4.legend(loc='best')

    for ax in axs.flatten():
        ax.grid(alpha=0.5)
    
    plt.show()

def plot_fertilizer_costs(run1, run2):
    run1_name = list(run1.keys())[0]
    run2_name = list(run2.keys())[0]
    run1 = run1[run1_name]
    run2 = run2[run2_name]

    fig, axs = plt.subplots(2, 2, figsize=(10, 10))
    ax1 = axs[0, 0]
    ax2 = axs[0, 1]
    ax3 = axs[1, 0]
    ax4 = axs[1, 1]

    # Plot run 1's investments
    ax1.plot(run1.index, run1["Grey investment"], label="Grey NH3", linestyle='-', color='grey')
    ax1.plot(run1.index, run1["Blue investment"], label="Blue NH3", linestyle='-', color='blue')
    ax1.plot(run1.index, run1["Green investment"], label="Green NH3", linestyle='-', color='green')
    ax1.title.set_text(f"{run1_name} - Investments")

    # Plot run 2's investments
    ax2.plot(run2.index, run2["Grey investment"], label="Grey NH3", linestyle='-', color='grey')
    ax2.plot(run2.index, run2["Blue investment"], label="Blue NH3", linestyle='-', color='blue')
    ax2.plot(run2.index, run2["Green investment"], label="Green NH3", linestyle='-', color='green')
    ax2.title.set_text(f"{run2_name} - Investments")

    # Plot run 1's prices
    ax3_2 = ax3.twinx()
    ax3_2.plot(run1.index, run1["carbon_tax"], label="CO2 tax", linestyle='-', color='grey')
    ax3.plot(run1.index, run1["gas_price"], label="Gas price", linestyle='-', color='black')
    ax3.plot(run1.index, run1["hydrogen_price"]/0.12, label="H2 price", linestyle='-', color='blue')
    ax3.title.set_text(f"{run1_name} - Prices")

    # Plot run 2's prices
    ax4_2 = ax4.twinx()
    ax4_2.plot(run2.index, run2["carbon_tax"], label="CO2 tax", linestyle='-', color='grey')
    ax4.plot(run2.index, run2["gas_price"], label="Gas price", linestyle='-', color='black')
    ax4.plot(run2.index, run2["hydrogen_price"]/0.12, label="H2 price", linestyle='-', color='blue')
    ax4.title.set_text(f"{run2_name} - Prices")

    # Set labels
    ax1.set_xlabel("Year")
    ax2.set_xlabel("Year")
    ax3.set_xlabel("Year")
    ax4.set_xlabel("Year")

    ax1.set_ylabel("Capacity Investment [MT/yr]")
    ax2.set_ylabel("Capacity Investment [MT/yr]")
    ax3.set_ylabel("Price [€/GJ]")
    ax3_2.set_ylabel("Price [€/tCO2]", color='grey')
    ax4.set_ylabel("Price [€/GJ]")
    ax4_2.set_ylabel("Price [€/tCO2]", color='grey')

    # Collect legend handles and labels in each subplot
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    h3, l3 = ax3.get_legend_handles_labels()
    h4, l4 = ax4.get_legend_handles_labels()
    h3_2, l3_2 = ax3_2.get_legend_handles_labels()
    h4_2, l4_2 = ax4_2.get_legend_handles_labels()

    # Plot legend in each subplot
    ax1.legend(h1, l1, loc='best')
    ax2.legend(h2, l2, loc='best')
    ax3.legend(h3+h3_2, l3+l3_2, loc='best')
    ax4.legend(h4+h4_2, l4+l4_2, loc='best')

    for ax in axs.flatten():
        ax.grid(alpha=0.5)
    
    plt.show()

### ------- Load model from Vensim mdl file ------- ###
cwd = os.getcwd()

# Specify the file path of the Vensim model
model_file = os.path.join(cwd,"vensim_models/Actualizado_new_switch.mdl")

# Load the model using the `load` function from `pysd`
model = pysd.read_vensim(model_file, split_views = True)

# Now you can use the `model` object to interact with the Vensim model
stocks_of_interest = ["hydrogen_price","oil_price", "carbon_tax", "gas_price", "biomass_price",
                                "int shipping consumption", "HFO shipping consumption",
                                "NH3 shipping consumption", "MeOH shipping consumption",
                                "shipping hydrogen demand",
                                "fleet reinvestment",
                                "HFO investment level", "NH3 investment level", "MeOH investment level",
                                "HFO cost", "NH3 cost", "MeOH cost",
                                "check",
                                "Grey investment level", "Grey investment", "Grey H2 cost", "Grey NH3",
                                "Green investment level", "Green investment", "Green H2 cost", "Green NH3",
                                "Blue investment level", "Blue investment", "Blue H2 cost", "Blue NH3",
                                "fertilizer hydrogen demand",
                                "NH3 reinvestment",
                                "check0", "NH3 fertilizer consumption"]

# For example, you can access model variables, run simulations, etc.
run1 = model.run(return_columns=stocks_of_interest)
run1_save = { "Vensim params" : run1 }

### ------- Load new data at run time ------- ###
dl = data_loading.data_loading_class()
carbon_taxes = dl.load_carbon_taxes()
gas_prices = dl.load_gas_prices()
oil_prices = dl.load_oil_prices()
woodchip_prices = dl.load_woodchip_prices(sensitivity=1)

### ------- Run model with new data ------- ###
model.set_components({"carbon_tax": carbon_taxes})
model.set_components({"gas_price": gas_prices, "oil_price": oil_prices})
model.set_components({"biomass_price": woodchip_prices})


run2 = model.run(return_columns=stocks_of_interest)
run2_save = { "Base" : run2 }

stocks_of_interest.append("electricity_price")
model.set_components({"electricity_price": 0.0})
run7 = model.run(return_columns=stocks_of_interest)
run7_save = { "No Electricity cost" : run7 }

plot_shipping_results(run2_save, run7_save)
plot_shipping_costs(run2_save, run7_save)

plot_shipping_results(run2_save, run1_save)
plot_shipping_costs(run2_save, run1_save)

plot_fertilizer_results(run2_save, run1_save)
plot_fertilizer_costs(run2_save, run1_save)

# PLot fertilizer hydrogen demand and shipping hydrogen demand in the same plot
fig, ax = plt.subplots(figsize=(12, 9))
ax.plot(run2.index, run2["shipping hydrogen demand"], label="Shipping hydrogen demand", linestyle='-', color='blue')
ax.plot(run2.index, run2["fertilizer hydrogen demand"], label="Fertilizer hydrogen demand", linestyle='-', color='green')
ax.plot(run2.index, run2["shipping hydrogen demand"]+run2["fertilizer hydrogen demand"], label="Total hydrogen demand", linestyle='-', color='black')
ax.title.set_text("Hydrogen demand - Base scenario")
ax.set_xlabel("Year")
ax.set_ylabel("Hydrogen demand [tH2]")
ax.legend(loc='best')
ax.grid(alpha=0.5)
plt.show()

carbon_taxes_seamaps = dl.load_carbon_taxes("seamaps")
run3 = model.run(return_columns=stocks_of_interest, params={"carbon_tax": carbon_taxes_seamaps})
run3_save = { "Seamaps CO2-Tax" : run3 }

plot_shipping_results(run2_save, run3_save)
plot_shipping_costs(run2_save, run3_save)

oil_prices_150 = dl.load_oil_prices(sensitivity=1.5)
run4 = model.run(return_columns=stocks_of_interest, params={"oil_price": oil_prices_150, "carbon_tax": carbon_taxes_seamaps})
run4_save = { "Oil 150%, Seamaps CO2-Tax" : run4 }

plot_shipping_results(run2_save, run4_save)
plot_shipping_costs(run2_save, run4_save)

woodchip_prices = dl.load_woodchip_prices(sensitivity=1.5)
run5 = model.run(return_columns=stocks_of_interest, params={"biomass_price": woodchip_prices, "oil_price" : oil_prices})
run5_save = { "Woodchip 150%" : run5 }

plot_shipping_results(run2_save, run5_save)
plot_shipping_costs(run2_save, run5_save)

electricity_prices = dl.load_electricity_prices()
run6 = model.run(return_columns=stocks_of_interest, params={"electricity_price": electricity_prices})
run6_save = { "Electricity prices updated" : run6 }

plot_shipping_results(run2_save, run6_save)
plot_shipping_costs(run2_save, run6_save)