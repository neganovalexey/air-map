import numpy as np
import pandas as pd
from utils import download_csv_dataset

class Emissions:

    def __init__(self):
        self._bins = 5
        self._layers_emis = {'trees': TreesEmissions(), 'vehicles': VehiclesEmissions()}
    
    def get_emissions(self, min_lat, min_lon, max_lat, max_lon):
        layers = {}
        bin_size = min((max_lat - min_lat) / self._bins, (max_lon - min_lon) / self._bins)
        lat_bins = int((max_lat - min_lat) // bin_size + 1)
        lon_bins = int((max_lon - min_lon) // bin_size + 1)
        
        for layer, emis in self._layers_emis.items():
            layers[layer] = []
            emis.prepare_grid(min_lat, min_lon, lat_bins, lon_bins, bin_size)
        
        for i in range(lat_bins):
            for j in range(lon_bins):
                for layer, emis in self._layers_emis.items():
                    layers[layer].append({ 'lat': min_lat + bin_size * (i + 0.5), 'lon': min_lon + bin_size * (j + 0.5),
                                           'emi': emis.get_emission(i, j)})
        return layers


class EmissionsBase:
    
    def prepare_grid(self, min_lat, min_lon, lat_bins, lon_bins, bin_size):
        pass
    
    def get_emission(self, i, j):
        pass


class TreesEmissions(EmissionsBase):

    def __init__(self):
        self.trees = download_csv_dataset('arbrat-zona')

    def prepare_grid(self, min_lat, min_lon, lat_bins, lon_bins, bin_size):
        self.trees_grid = np.zeros((lat_bins, lon_bins), dtype=float)
        for index, tree in self.trees.iterrows():
            em = 0
            if tree['ALCADA'] == 'PETITA':
                em = 16 # g / d
            elif tree['ALCADA'] == 'GRAN':
                em = 60
            else:
                em = 40
            i = int((tree['LATITUD_WGS84'] - min_lat) // bin_size)
            j = int((tree['LONGITUD_WGS84'] - min_lon) // bin_size)
            if i >= 0 and i < lat_bins and j >= 0 and j < lon_bins:
                self.trees_grid[i][j] -= em
    
    def get_emission(self, i, j):
        return self.trees_grid[i][j]

class VehiclesEmissions(EmissionsBase):

    def __init__(self):
        self.cars = download_csv_dataset('est-vehicles-potencia-fiscal-turismes')
    
    def get_emission(self, i, j):
        return 2

