import sys
import os
import numpy as np
import pandas as pd
from itertools import combinations
import geopy.distance
from shapely.geometry import Polygon, MultiPolygon, Point, box
from shapely.strtree import STRtree
from utils import download_csv_dataset, download_veg_shapes, get_neighborhoods, get_city_limits

class Emissions:

    def __init__(self):
        self._bins = 3
        self._layers_emis = {'trees': TreesEmissions(), 'vehicles': VehiclesEmissions(), 'veg': VegEmissions()}
    
    def get_emissions(self, min_lat, min_lon, max_lat, max_lon):
        print('calculating emissions for grid')
        layers = {}
        bin_size = min((max_lat - min_lat) / self._bins, (max_lon - min_lon) / self._bins)
        lat_bins = int((max_lat - min_lat) // bin_size + 1)
        lon_bins = int((max_lon - min_lon) // bin_size + 1)
        
        for layer, emis in self._layers_emis.items():
            emis.prepare_grid(min_lat, min_lon, lat_bins, lon_bins, bin_size)
        
        for i in range(lat_bins):
            for j in range(lon_bins):
                lat = min_lat + bin_size * (i + 0.5)
                lon = min_lon + bin_size * (j + 0.5)
                layers_values = {}
                for layer, emis in self._layers_emis.items():
                    layers_values[layer] = emis.get_emission(i, j, lat, lon)
                for comb_len in range(1, len(self._layers_emis) + 1):
                    for comb in combinations(sorted(self._layers_emis.keys()), comb_len):
                        comb_layer = '_'.join(comb)
                        comb_value = sum([layers_values[l] for l in comb])
                        if not comb_layer in layers:
                            layers[comb_layer] = []
                        layers[comb_layer].append({ 'lat': lat, 'lon': lon, 'emi': comb_value})
        return layers


class EmissionsBase:
    
    def prepare_grid(self, min_lat, min_lon, lat_bins, lon_bins, bin_size):
        pass
    
    def get_emission(self, i, j, lat, lon):
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
    
    def get_emission(self, i, j, lat, lon):
        return self.trees_grid[i][j]

class VegEmissions(EmissionsBase):

    sq_degree_consumption = 85000.0 * 111000.0 * 120.0

    def __init__(self):
        geoms = download_veg_shapes()
        self.tree = STRtree([Polygon(g['coordinates'][0]) for g in geoms])
    
    def prepare_grid(self, min_lat, min_lon, lat_bins, lon_bins, bin_size):
        self.min_lat = min_lat
        self.min_lon = min_lon
        self.bin_size = bin_size
    
    def get_emission(self, i, j, lat, lon):
        cell = box(self.min_lon + j * self.bin_size, self.min_lat + i * self.bin_size,
                   self.min_lon + (j + 1) * self.bin_size, self.min_lat + (i + 1) * self.bin_size)
        area = sum([poly.intersection(cell).area for poly in self.tree.query(cell)])
        return -area * self.sq_degree_consumption;


class VehiclesEmissions(EmissionsBase):

    hp2num = {
       'Menys 8 cf': 3, '8 a 8,9': 8.5, '9 a 9,9': 9.5, '10 a 10,9': 10.5, '11 a 11,9': 11.5,
       '12 a 12,9': 12.5, '13 a 13,9': 13.5, '14 a 14,9': 14.5, '15 a 15,9': 15.5, '16 a 19,9': 18,
       '20 i més cf': 25, 'No consta': 5
    }
    
    total_emissions = 4930000000.0
    
    close_nbrs = 3

    def __init__(self):
        self.cars = download_csv_dataset('est-vehicles-potencia-fiscal-turismes')
        self.neighborhoods = get_neighborhoods()
        limits = get_city_limits()
        self.city_limits = MultiPolygon([Polygon(g[0]) for g in limits])
        self.nbr2emi = {}
        for index, car in self.cars.iterrows():
            nbr_id = car['Codi_Barri']
            if not nbr_id in self.nbr2emi:
                self.nbr2emi[nbr_id] = 0
            self.nbr2emi[nbr_id] += self.hp2num[car['Potencia_fiscal']] * car['Nombre_turismes']
    
    def prepare_grid(self, min_lat, min_lon, lat_bins, lon_bins, bin_size):
        self.emis_grid = np.zeros((lat_bins, lon_bins), dtype=float)
        for i in range(lat_bins):
            for j in range(lon_bins):
                lat = min_lat + bin_size * (i + 0.5)
                lon = min_lon + bin_size * (j + 0.5)
                if self.city_limits.intersects(Point(lon, lat)):
                    nbrs = []
                    for index, nbr in self.neighborhoods.iterrows():
                        dist = geopy.distance.vincenty((lat, lon), (nbr['lat'], nbr['lon'])).km
                        nbrs.append((index, 1.0 / dist))
                    nbrs.sort(key=lambda n: n[1], reverse=True)
                    nbrs = nbrs[:self.close_nbrs]
                    s = sum([n[1] for n in nbrs])
                    self.emis_grid[i][j] = np.sum([self.nbr2emi[n[0]] * n[1] / s for n in nbrs])
        s = np.sum(self.emis_grid)
        self.emis_grid = self.total_emissions * self.emis_grid / s
    
    def get_emission(self, i, j, lat, lon):
        return self.emis_grid[i][j]


if __name__ == '__main__':
    emi = Emissions()
    #print(emi.get_emissions(41.353755, 2.111845, 41.388346, 2.168766))
    layers = emi.get_emissions(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]))
    if not os.path.exists('static/csvs/'):
        os.mkdir('static/csvs/')
    for layer, data in layers.items():
        df = pd.DataFrame(data)
        df.to_csv('static/csvs/' + layer + '.csv')
