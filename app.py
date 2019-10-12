from flask import Flask, render_template, request, jsonify

import json

from emissions import Emissions


app = Flask(__name__, static_folder='static')
emissions = Emissions()


@app.route('/', methods=['GET'])
def draw_map():
    return render_template('index.html',
                           app_id=app.app_id,
                           app_code=app.app_code)

@app.route('/filter',  methods=['POST'])
def make_info():
    data = request.form
    print(data)
    #TODO: return data depending on filter categories

    response = emissions.get_emissions(data['min_lat'], data['min_lon'], data['max_lat'], data['max_lon'])
    return jsonify(response)


try:
    with open('credentials.json') as fin:
        credentials = json.loads(fin.read())
        app.app_id, app.app_code = credentials['app_id'], credentials['app_code']
except (KeyError, FileNotFoundError, json.decoder.JSONDecodeError) as e:
    print("Error while reading HERE API credentials, proceed on your own risk!")
    print(e)


if __name__ == '__main__':
    app.run()
