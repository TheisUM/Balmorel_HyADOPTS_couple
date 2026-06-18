### This script runs the hydrogen model under different scenarios ###
import pysd
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import data_loading
#from IPython.parallel import Client
from time import time

## ----------------- Load the model ----------------- ##
cwd = os.getcwd()
model_name = "hydrogen_model"
model_short_path = "vensim_models/" + model_name

model_loaded = True # Set to True if the model is loaded from a Python file

start = time()
if model_loaded: # Load the model from the Python file
    model_file = os.path.join(cwd, model_short_path + ".py")
    model = pysd.load(model_file)
else: # Read the model from the Vensim mdl file
    model_file = os.path.join(cwd, model_short_path + ".mdl")
    model = pysd.read_vensim(model_file, split_views = True)

print("Model loaded in {} seconds".format(time()-start))

## ----------------- Setup/modify model ----------------- ##
stocks_of_interest = ["TOTAL GREEN HYDROGEN DEMAND", "Green H2 cost", "TOTAL SUBSIDIES"]

model.set_components({"SEED": 12, "pulse size": 0.3, "SYSTEM NOISE": 0.1})

def new_subsidy_pulse():
    t = model.components.time()
    p = 0
    if t >= 2025 and t < 2025 + 10:
        p = 1
    return p

model.components.pulse_h2_subsidy = new_subsidy_pulse

## ----------------- Run the model ----------------- ##
runs_demand = []
runs_price = []
runs_subsidy = []

subsidies = [0, 0.5, 1, 1.5, 2, 2.5, 3]

for subsidy in subsidies:
    model.set_components({"Green H2 subsidy size": subsidy})
    run = model.run(return_columns=stocks_of_interest)
    runs_demand.append(run[stocks_of_interest[0]])
    runs_price.append(run[stocks_of_interest[1]])
    runs_subsidy.append(run[stocks_of_interest[2]].iloc[-1])

## ----------------- Plot the results ----------------- ##
# Plot the total subsidy values in a bar plot
fig, ax = plt.subplots()
plt.bar(subsidies, runs_subsidy, width=0.4)
plt.xticks(subsidies)
plt.title("Total subsidies for different subsidies")
plt.xlabel("€/kg subsidy")
plt.ylabel("M€")
plt.show()

fig, ax = plt.subplots()
df = pd.DataFrame(runs_price).T
df.columns = subsidies
df.index = run.index
df.plot(ax=ax, title="GREEN H2 price evolution for different subsidies")
ax.set_xlabel("Year")
ax.set_ylabel("€/kg")
ax.legend(title="€/kg subsidy")
plt.show()

# Plot the results
fig, ax = plt.subplots()
df = pd.DataFrame(runs_demand).T
df.columns = subsidies
df.index = run.index
df.plot(ax=ax, title="TOTAL GREEN HYDROGEN DEMAND for different subsidies")
ax.set_xlabel("Year")
ax.set_ylabel("t H2")
ax.legend(title="€/kg subsidy")
plt.show()



# Run the model
# Now you can use the `model` object to interact with the Vensim model
stocks_of_interest = ["naphtha hydrogen demand", "naphtha production"]
model.set_components({"Green H2 subsidy size": 0})

# For example, you can access model variables, run simulations, etc.
runs = []

for seed in range(1, 11):
    model.set_components({"SEED": seed})
    run = model.run(return_columns=stocks_of_interest)
    runs.append(run[stocks_of_interest[0]])
    if seed == 1:
        naphtha_production_pulse = run["naphtha production"]

model.set_components({"SEED": 11, "pulse size": 0})

run = model.run(return_columns=stocks_of_interest)
runs.append(run[stocks_of_interest[0]])
naphtha_production_norm = run["naphtha production"]

# Plot the results
fig, ax = plt.subplots()
df = pd.DataFrame(runs).T
df.columns = range(1, 12)
df.index = run.index
df.plot(ax=ax, title="Naphtha hydrogen demand for different seeds")
ax2 = ax.twinx()
ax2.plot(naphtha_production_pulse, label="Naphtha production", color="black", linestyle="--")
ax2.plot(naphtha_production_norm, label="Naphtha production", color="black", linestyle="--")
ax2.set_ylabel("Naphtha production")
ax.set_xlabel("Year")
ax.set_ylabel("Naphtha hydrogen demand")
ax.legend(title="Seed")
plt.show()

