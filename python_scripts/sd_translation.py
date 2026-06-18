import pysd
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_stocks(stocks):
    fig, axs = plt.subplots(int(len(stocks)/2), 2, figsize=(10, 5*len(stocks)))

    for i, stock in enumerate(stocks):
        ax = axs[int(np.round(i/4+0.1)), np.round(i%2) ]
        ax.plot(stock.index, stock["SMR Users"], label="SMR Users (LT={})".format(1/stock["Green Hydrogen Demand"].iloc[0]))
        ax.plot(stock.index, stock["Adopters"], label="Adopters (LT={})".format(1/stock["Green Hydrogen Demand"].iloc[0]))
        ax.plot(stock.index, stock["EC Users"], label="EC Users (LT={})".format(1/stock["Green Hydrogen Demand"].iloc[0]))
        ax2 = ax.twinx()
        ax2.plot(stock.index, stock["EC price"], label="EC price (LT={})".format(1/stock["Green Hydrogen Demand"].iloc[0]), color='black')
        
        h, l = ax.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax.legend(h+h2, l+l2, loc='best')
        
        
    plt.show()

cwd = os.getcwd()

# Specify the file path of the Vensim model
model_file = os.path.join(cwd,"vensim_models/example model.mdl")

# Load the model using the `load` function from `pysd`
model = pysd.read_vensim(model_file)

# Now you can use the `model` object to interact with the Vensim model
# For example, you can access model variables, run simulations, etc.
stocks = [model.run(params = {"Renovation Rate": 1/LT},  return_columns=["SMR Users", "Adopters", "EC Users", "Acceptability", "Renovation Rate"]) for LT in range(5, 25, 5)]

"""
fig, axs = plt.subplots(len(stocks), 1, figsize=(10, 5*len(stocks)))

for i, stock in enumerate(stocks):
    ax = axs[i]
    ax.plot(stock.index, stock["SMR Users"], label="SMR Users (LT={})".format(1/stock["Renovation Rate"].iloc[0]))
    ax.plot(stock.index, stock["Adopters"], label="Adopters (LT={})".format(1/stock["Renovation Rate"].iloc[0]))
    ax.plot(stock.index, stock["EC Users"], label="EC Users (LT={})".format(1/stock["Renovation Rate"].iloc[0]))
    ax2 = ax.twinx()
    ax2.plot(stock.index, stock["Acceptability"], label="Acceptability (LT={})".format(1/stock["Renovation Rate"].iloc[0]), color='r')
    ax.legend(loc='best')
    ax2.legend(loc='upper right')

plt.show()
"""

fig, ax = plt.subplots(figsize=(10, 5))

line_styles = ['-', '--', ':', '-.']
colors = ['blue', 'red', 'green', 'orange']

for i, stock in enumerate(stocks):
    ax.plot(stock.index, stock["SMR Users"], label="SMR Users (LT={})".format(1/stock["Renovation Rate"].iloc[0]), linestyle=line_styles[0], color=colors[i])
    ax.plot(stock.index, stock["Adopters"], label="Adopters (LT={})".format(1/stock["Renovation Rate"].iloc[0]), linestyle=line_styles[1], color=colors[i])
    ax.plot(stock.index, stock["EC Users"], label="EC Users (LT={})".format(1/stock["Renovation Rate"].iloc[0]), linestyle=line_styles[2], color=colors[i])

ax.legend(loc='best')
plt.show()

fig, ax = plt.subplots(figsize=(10, 5))

for i, stock in enumerate(stocks):
    ax.plot(stock.index, stock["Acceptability"], label="Acceptability (LT={})".format(1/stock["Renovation Rate"].iloc[0]), linestyle=line_styles[0], color=colors[i])

ax.legend(loc='best')
plt.show()


stocks = [model.run(
                    params={"Green Hydrogen Demand": lambda : model.components.ec_users()*demand_pr_user}, 
                    return_columns=["SMR Users", "Adopters", "EC Users", "Acceptability", "Renovation Rate", "Green Hydrogen Demand", "EC price"])
                    for demand_pr_user in [0.01, 0.1, 0.2]]

stocks.insert(0, model.run( params={"Green Hydrogen Demand": 20},
    return_columns=["SMR Users", "Adopters", "EC Users", "Acceptability", "Renovation Rate", "Green Hydrogen Demand", "EC price"]))

plot_stocks(stocks)


gas_prices = pd.Series(index=stocks[0].index, data=np.linspace(10, 20, len(stocks[0].index)))
#model.set_components()
gas_price_run = model.run(params={"SMR price": gas_prices}, return_columns=["SMR Users", "Adopters", "EC Users", "Acceptability", "Renovation Rate"])

fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(gas_price_run.index, gas_price_run["SMR Users"], label="SMR Users")
ax.plot(gas_price_run.index, gas_price_run["Adopters"], label="Adopters")
ax.plot(gas_price_run.index, gas_price_run["EC Users"], label="EC Users")
ax2 = ax.twinx()
ax2.plot(gas_price_run.index, gas_price_run["Acceptability"], label="Acceptability", color='r')

ax.legend(loc='upper left')
ax2.legend(loc='upper right')

plt.show()

# Function to plot the results
def plot_results(run1, run2):
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()
    ax1.plot(run1.index, run1["int shipping consumption"], label="Total consumption", linestyle='-', color='grey')
    ax1.plot(run1.index, run1["int shipping fossil energy consumption"], label="MDO 1", linestyle='--', color='blue')
    ax1.plot(run1.index, run1["ammonia shipping consumption"], label="NH3 1", linestyle=':', color='blue')
    ax1.plot(run1.index, run1["methanol shipping consumption"], label="MeOH 1", linestyle='-.', color='blue')

    ax1.plot(run2.index, run2["int shipping fossil energy consumption"], label="MDO 2", linestyle='--', color='red')
    ax1.plot(run2.index, run2["ammonia shipping consumption"], label="NH3 2", linestyle=':', color='red')
    ax1.plot(run2.index, run2["methanol shipping consumption"], label="MeOH 2", linestyle='-.', color='red')

    ax2.plot(run1.index, run1["shipping hydrogen demand"], label="Shipping Hydrogen Demand 1", linestyle='-', color='black')
    ax2.plot(run2.index, run2["shipping hydrogen demand"], label="Shipping Hydrogen Demand 2", linestyle='--', color='black')

    ax1.legend(loc='best')
    ax2.legend(loc='best')

    plt.show()