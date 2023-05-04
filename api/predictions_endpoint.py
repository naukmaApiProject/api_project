import sys
sys.path.append('.')

import datetime as dt
import json
import requests
import os
import json
from serving.predictions_builder import build_predictions
from flask import Flask, jsonify, request

API_TOKEN = "authtoken"
LAST_MODEL_TRAINED = dt.datetime(2023, 4, 24, 16, 20, 0)
PREDICTIONS_PATH = "/app/data/predictions/"


app = Flask(__name__)

def create_query_parameter(key: str, value: str):
    return f"&{key}={value}"

def get_prediction(region):
    response = {
        "last_model_train_time": LAST_MODEL_TRAINED.strftime("%Y-%m-%d %H:%M:%S"),
        "regions_forecast": {}
    }

    last_updated = None

    if region == "all" or region == "":
        for filename in os.listdir(PREDICTIONS_PATH):
            if filename.endswith(".json"):
                with open(os.path.join(PREDICTIONS_PATH, filename), "r") as f:
                    json_data = json.load(f)
                    if last_updated == None:
                        last_updated = json_data["last_prediction_time"]
                    region_name = os.path.splitext(filename)[0]
                    response["regions_forecast"][region_name] = json_data[region_name]

    else:
        with open(os.path.join(PREDICTIONS_PATH, f"{region}.json"), "r") as f:
            json_data = json.load(f)
            last_updated = json_data["last_prediction_time"]
            response["regions_forecast"][region] = json_data[region]

    response["last_prediction_time"] = last_updated
    return response

def authenticate(json_data):
    if json_data is None or json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)
    
class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/api/update", methods=["POST"])
def update():
    json_data = request.get_json()
    authenticate(json_data)
    build_predictions()
    return jsonify({"status" : "success"})

@app.route("/",methods=["GET"])
def home_page():
    return "<p><h1>Alarms API</h1></p>"

@app.route("/api/predict", methods=["POST"])
def predictions_endpoint():
    json_data = request.get_json()

    authenticate(json_data)

    if json_data.get("region") is None:
        raise InvalidUsage("You should specify the region or leave it blank to get prediction for all regions", status_code=400)

    region = json_data.get("region")

    response = get_prediction(region)

    return response

if __name__ == '__main__':
    app.run()