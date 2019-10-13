from flask import Flask, render_template, request, jsonify

import json


app = Flask(__name__, static_folder='static')


GREEN = ['rgba(255, 255, 255, 0)', 'yellow', 'rgba(34, 139, 34, 0.9)']
RED = ['rgba(255, 255, 255, 0)', 'yellow', 'rgba(139, 34, 34, 0.9)']
RED_YELLOW_GREEN = ['red', 'yellow', 'green']

COLOR_SCHEMES = {
    'empty.csv': (GREEN, 0),
    'trees.csv': (GREEN, 100000),
    'veg.csv': (GREEN, 100000000),
    'vehicles.csv': (RED, 2000000000),
    'trees_veg.csv': (GREEN, 100000000),
    'trees_vehicles.csv': (RED_YELLOW_GREEN, 2000000000),
    'veg_vehicles.csv': (RED_YELLOW_GREEN, 2000000000),
    'trees_veg_vehicles.csv': (RED_YELLOW_GREEN, 2000000000)
}


@app.route('/', methods=['GET'])
def draw_map():
    return render_template('index.html',
                           app_id=app.app_id,
                           app_code=app.app_code)


@app.route('/filter', methods=['POST'])
def make_info():
    data = request.form
    keys = set(data)
    print(keys)
    if not keys:
        filename = 'empty.csv'
    else:
        filename = '_'.join(sorted(keys)) + '.csv'
    color_range, base_count = COLOR_SCHEMES[filename]
    return jsonify({
        'filename': filename,
        'colorscale': {
            'range': color_range,
            'domain': [0, 0.5, 1],
        },
        'base_count': base_count,
    })


try:
    with open('credentials.json') as fin:
        credentials = json.loads(fin.read())
        app.app_id, app.app_code = credentials['app_id'], credentials['app_code']
except (KeyError, FileNotFoundError, json.decoder.JSONDecodeError) as e:
    print("Error while reading HERE API credentials, proceed on your own risk!")
    print(e)


if __name__ == '__main__':
    app.run()
