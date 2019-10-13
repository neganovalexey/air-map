import os
from io import StringIO
import requests
import json
import dateutil.parser
import numpy as np
import pandas as pd

'''
Useful ids:
'arbrat-zona' - trees
'est-vehicles-potencia-fiscal-turismes' - vehicles horsepowers by neighbourhood
'''

def download_csv_dataset(dataset_id, force_reload=False):
    if force_reload or not os.path.isfile('data/' + dataset_id + '.csv'):
        ds_info = requests.get('https://opendata-ajuntament.barcelona.cat/data/api/3/action/package_show?id=' + dataset_id)
        res = [r for r in ds_info.json()['result']['resources'] if r['format'].lower() == 'csv']
        last_res = max(res, key = lambda r: dateutil.parser.parse(r['qa']['updated']))
        ds = requests.get(last_res['url'])
        with open('data/' + dataset_id + '.csv', 'wb') as f:
            f.write(ds.content)
    return pd.read_csv('data/' + dataset_id + '.csv')

def download_veg_shapes(force_reload=False):
    if force_reload or not os.path.isfile('data/cobertura-vegetal-ndvi.json'):
        ds_info = requests.get('https://opendata-ajuntament.barcelona.cat/data/api/3/action/package_show?id=cobertura-vegetal-ndvi')
        res = [r for r in ds_info.json()['result']['resources'] if r['format'].lower() == 'shp']
        last_res = max(res, key = lambda r: dateutil.parser.parse(r['qa']['updated']))
        ds = requests.get(last_res['url'])
        with open('data/cobertura-vegetal-ndvi.shp', 'wb') as f:
            f.write(ds.content)
            
        #TODO: convert automatically to geojson
    
    with open('data/cobertura-vegetal-ndvi.json') as f:
        shapes = json.load(f)
    print('loaded vegetal shapes')
    return shapes['geometries']

def get_neighborhoods():
    return pd.read_csv('data/neightborhoods.csv', index_col=0, header=None, names=['id', 'name', 'lat', 'lon'])

def get_city_limits():
    with open('data/terme-municipal.json') as f:
        shapes = json.load(f)
    return shapes['features'][0]['geometry']['coordinates']
