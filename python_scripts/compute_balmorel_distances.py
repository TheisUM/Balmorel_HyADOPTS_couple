import os
import pandas as pd
import numpy as np
from geopy.distance import geodesic

def compute_balmorel_distances(path_to_coordinates='\\data\\coordinates_RRR.csv',
                               path_to_regions='\\data\\RRR.xlsx',
                               path_to_connections='\\data\\RRR_connections.xlsx'):
    """
    Computes distances for Balmorel model based on input data.

    Parameters:
    data (list of tuples): Each tuple contains coordinates (x, y) of a point.

    Returns:
    list of list: A matrix representing distances between each pair of points.
    """
    
    # get current working directory
    cwd = os.getcwd()

    # load regions and coordinates for regions
    coordinates = pd.read_csv(cwd + path_to_coordinates)
    regions = pd.read_excel(cwd + path_to_regions)
    land_connections = pd.read_excel(cwd + path_to_connections, sheet_name='land connections')
    sea_connections = pd.read_excel(cwd + path_to_connections, sheet_name='subsea connections')

    # make sure RRR columns are strings and strip any whitespace
    regions['RRR'] = regions['RRR'].astype(str).str.strip()
    coordinates['RRR'] = coordinates['RRR'].astype(str).str.strip()
    # merge regions with coordinates on RRR column
    regions = regions.merge(coordinates, on="RRR")
    labels = regions['RRR'].tolist()
    # Prepare a list of tuples with (latitude, longitude) for each region
    region_coords = [(row['Lat'], row['Lon']) for _, row in regions.iterrows()]

    # Calculate distances between regions using coordinates
    rerouting_factor = 1.3 # factor to account for rerouting of lines due to terrain, urban areas, etc.
    s = len(regions)
    distances = np.zeros((s, s))
    for i in range(s):
        for j in range(s):
            distances[i, j] = geodesic(region_coords[i], region_coords[j]).km * rerouting_factor
    df_dist = pd.DataFrame(distances, index=labels, columns=labels)

    land_connections.set_index(land_connections.columns[0], inplace=True)
    land_connections.index.name = None

    sea_connections.set_index(sea_connections.columns[0], inplace=True)
    sea_connections.index.name = None

    all_connections = land_connections.add(sea_connections, fill_value=0)
    all_connections.fillna(0, inplace=True) # fill NaN values with 0 for connections that do not exist
    all_connections

    distance_matrix = df_dist * all_connections

    return distance_matrix

if __name__ == "__main__":
    distances = compute_balmorel_distances()
    print(distances)