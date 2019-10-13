from flask import Flask, render_template, request, jsonify

import json


app = Flask(__name__, static_folder='static')


GREEN = { 'range': ['rgba(255, 255, 255, 0.1)', 'rgba(34, 139, 34, 0.9)', 'yellow'], 'domain': [0, 0.3, 1] }
RED = { 'range': ['rgba(0, 0, 0, 0.1)', 'yellow', 'rgba(139, 34, 34, 0.9)'], 'domain': [0, 0.2, 1] }
RED_YELLOW_GREEN = { 'range': ['green', 'yellow', 'red'], 'domain': [0, 0.5, 1] }

COLOR_SCHEMES = {
    'empty.csv': (GREEN, 0),
    'trees.csv': (GREEN, 1000),
    'veg.csv': (GREEN, 1000),
    'vehicles.csv': (RED, 1000),
    'trees_veg.csv': (GREEN, 1000),
    'trees_vehicles.csv': (RED_YELLOW_GREEN, 1000),
    'veg_vehicles.csv': (RED_YELLOW_GREEN, 1000),
    'trees_veg_vehicles.csv': (RED_YELLOW_GREEN, 1000)
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
        'colorscale': color_range,
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
