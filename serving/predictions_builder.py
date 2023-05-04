import sys
sys.path.append('.')

import os
import requests

import pickle
import json
import numpy as np
import random
import time
from tensorflow import keras
from datetime import datetime, timedelta
from utils.regions import get_region_id

API_KEY = 'PXAMV42AU6LKXV828GP3UCWGH'

MODEL_FILE = 'model/model2.h5'
THRESHOLD = 0.5
MODEL_FILE = 'model/model2.h5'
THRESHOLD = 0.5
regions = ["Kyiv", "Vinnytsia", "Lutsk", "Dnipro", "Donetsk", "Zhytomyr", "Uzhhorod", 
           "Zaporizhzhia", "Ivano-Frankivsk", "Kropyvnytskyi", "Luhansk", "Lviv", "Mykolaiv",
           "Odesa", "Poltava", "Rivne", "Simferopol", "Sumy", "Ternopil", "Kharkiv", "Kherson", 
           "Khmelnytskyi", "Cherkasy", "Chernivtsi", "Chernihiv"];

def get_forecast(city, date_from, date_to):
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city},Ukraine/{date_from}/{date_to}?unitGroup=metric&key={API_KEY}";
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

def get_last_model(directory) :
    # Get a list of all files in the directory
    files = os.listdir(directory)

    # Sort the list of files by creation time in descending order
    files.sort(key=lambda x: os.path.getctime(os.path.join(directory, x)), reverse=True)

    # Get the name of the most recently created file
    return directory + "/" + files[0]

def build_predictions():
    
    model = keras.models.load_model(get_last_model("/app/data/models"), compile=False)
    prediction_date = datetime.today()
    for region in regions:
        build_region_prediction(region, model, prediction_date)

def build_region_prediction(region, model, prediction_date):
    #get next 12 hours date range
    dates = get_dates(prediction_date)
    weather = get_forecast(region, dates[0].strftime('%Y-%m-%d'), dates[1].strftime('%Y-%m-%d'))
    curr_date = dates[0]
    curr_hour = curr_date.hour

    prediction = { "last_prediction_time": prediction_date.strftime('%Y-%m-%d %H:%M:%S') }
    prediction[region] = {}

    input_data = [0] * 12
    
    #get data for 12 hours for particular region
    for i in range(12):
        day = 0 if curr_hour < 24 else 1
        hour = curr_date.hour

        date = curr_date.strftime('%Y-%m-%d')
        date = datetime.strptime(date, '%Y-%m-%d')

        daily_weather = weather['days'][day]

        curr_weather = daily_weather['hours'][hour]

        #model input variables
        date = date.timestamp()
        day_temp_max = daily_weather['tempmax']
        day_temp_min = daily_weather['tempmin']
        day_temp = daily_weather['temp']
        day_temp2 = float(time.time())
        day_humidity = daily_weather['humidity']  
        day_hour = float(hour)
        hour_temp = curr_weather['temp']
        hour_dew = curr_weather['dew']
        hour_humidity = curr_weather['humidity']
        m_region = get_region_id(region)


        input_data[i] = [date,m_region,day_temp_max,day_temp_min,day_temp,day_temp2,day_humidity,day_hour,hour_temp,hour_humidity,hour_dew]
        curr_date = curr_date + timedelta(hours=1)
        curr_hour = curr_hour + 1

    #normalize data    
    mean = np.mean(input_data, axis=0)
    std = np.std(input_data, axis=0)
    std[std == 0] = 1e-6  #
    #add a small value to prevent division by 0
    eps = 1e-10
    normalized_data = (input_data - mean) / (std + eps)
    #predict
    res = model.predict(normalized_data)

    #write predictions to object
    curr_date = dates[0]
    curr_hour = curr_date.hour

    for i in range(12):
        day = 0 if curr_hour < 24 else 1
        hour = curr_date.hour

        prediction_time = curr_date.strftime('%H:%M')
        alarm = True if res[i] >= THRESHOLD else False
        print(alarm)
        prediction[region][prediction_time] = alarm

        curr_date = curr_date + timedelta(hours=1)
        curr_hour = curr_hour + 1
    
    save_prediction(prediction,region)

def save_prediction(prediction, region):
    with open(f"/app/data/predictions/{str(region)}.json", "w") as f:
        json.dump(prediction,f)

def get_dates(date):
    date = date + timedelta(hours=1)
    date_from = date.replace(minute=0, second=0, microsecond=0)
    date_to = date_from + timedelta(hours=12)
    return [date_from, date_to]

if __name__ == "__main__":
    build_predictions()