"""
This script loads all Excel files from the technology_data folder into pandas DataFrames.
"""

import os
import pandas as pd

def load_technology_data():
    """
    Load all Excel files from the technology_data folder into pandas DataFrames.

    Returns:
        dict: A dictionary where keys are file names and values are DataFrames.
    """

    # Define the path to the technology_data folder
    folder_path = os.path.join(os.path.dirname(__file__), '..', 'technology_data')

    # List all Excel files in the folder
    excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx') or f.endswith('.xls')]

    # Load each Excel file into a dictionary of DataFrames
    data = {}
    for file in excel_files:
        file_path = os.path.join(folder_path, file)
        data[file] = pd.read_excel(file_path, sheet_name='alldata_flat')  # Load sheet with all data

    # Example: print the names of loaded files
    print("Loaded files:", list(data.keys()))
    return data