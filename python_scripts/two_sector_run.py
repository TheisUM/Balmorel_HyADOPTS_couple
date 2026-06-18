
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import data_loading

import pysd
### ------- Load model from Vensim mdl file ------- ###
cwd = os.getcwd()

# Specify the file path of the Vensim model
model_file = os.path.join(cwd,"vensim_models/test with two sectors.mdl")

# Load the model using the `load` function from `pysd`
model = pysd.read_vensim(model_file, split_views = False)

base_run = model.run()

base_run.plot()
plt.title("Base run")
plt.show()


