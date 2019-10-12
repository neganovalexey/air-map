import requests
import dateutil.parser
import numpy as np
import os
import pandas as pd
from io import StringIO

'''
Useful ids:
'arbrat-zona' - trees
'est-vehicles-potencia-fiscal-turismes' - vehicles horsepowers by neighbourhood
'''

def download_csv_dataset(dataset_id, force_reload=False):
    if force_reload or not os.path.isfile('data/' + dataset_id + '.csv'):
        ds_info = requests.get('https://opendata-ajuntament.barcelona.cat/data/api/3/action/package_show?id=' + dataset_id)
        res = [r for r in ds_info.json()['result']['resources'] if r['format'] == 'CSV']
        last_res = max(res, key = lambda r: dateutil.parser.parse(r['qa']['updated']))
        ds = requests.get(last_res['url'])
        with open('data/' + dataset_id + '.csv', 'wb') as f:
            f.write(ds.content)
    return pd.read_csv('data/' + dataset_id + '.csv')
