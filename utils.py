import requests
import dateutil.parser
import numpy as np
from io import StringIO

'''
Useful ids:
'arbrat-zona' - trees
'est-vehicles-potencia-fiscal-turismes' - vehicles horsepowers by neighbourhood
'''

def csv_obtainer(dataset_id):
    ds_info = requests.get('https://opendata-ajuntament.barcelona.cat/data/api/3/action/package_show?id=' + dataset_id)
    res = [r for r in ds_info.json()['result']['resources'] if r['format'] == 'CSV']
    last_res = max(res, key = lambda r: dateutil.parser.parse(r['qa']['updated']))
    ds = requests.get(last_res['url'])
    ds_lines = ds.text.split('\n')
    columns = len(ds_lines[0].split(','))
    regexes = [r'([^,"]*|"[^,"]*")'] * columns
    ds_np = np.fromregex(StringIO(ds.text), ','.join(regexes), dtype=str)
    return (ds_np[0], ds_np[1:])
