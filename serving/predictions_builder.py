import os

import requests
from datetime import datetime, timedelta
from tensorflow import keras
import pickle
import json

API_KEY = 'PXAMV42AU6LKXV828GP3UCWGH'

regions = ["Kyiv", "Vinnytsia", "Lutsk", "Dnipro", "Donetsk", "Zhytomyr", "Uzhhorod", 
           "Zaporizhzhia", "Ivano-Frankivsk", "Kropyvnytskyi", "Luhansk", "Lviv", "Mykolaiv", 
           "Odesa", "Poltava", "Rivne", "Simferopol", "Sumy", "Ternopil", "Kharkiv", "Kherson", 
           "Khmelnytskyi", "Cherkasy", "Chernivtsi", "Chernihiv"];

def get_forecast(city, date_from, date_to):
    response = requests.get(f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
                        f"{city}/{date_from}/{date_to}?unitGroup=metric&key={API_KEY}")
    if response.status_code == 200:
        return response.json()

def get_last_model(directory) :
    # Get a list of all files in the directory
    files = os.listdir(directory)

    # Sort the list of files by creation time in descending order
    files.sort(key=lambda x: os.path.getctime(os.path.join(directory, x)), reverse=True)

    # Get the name of the most recently created file
    #return files[0]
    return "/home/vampir/lolitech/api/api_project/data/models/model1-2.h5"

def build_predictions():
    with open(get_last_model("/home/vampir/lolitech/api/api_project/data/models"), 'rb') as file:
        model = keras.models.load_model('/home/vampir/lolitech/api/api_project/data/models/model1-2.h5')
        #model = pickle.load(file)
    
    prediction_date = datetime.today()

    for region in regions:
        build_region_prediction(region, model, prediction_date)

def build_region_prediction(region, model, prediction_date):
    dates = get_dates(prediction_date)
    weather = get_forecast(region, dates[0].strftime('%Y-%m-%d'), dates[1].strftime('%Y-%m-%d'))

    curr_date = dates[0]
    curr_hour = curr_date.hour

    prediction = { str(region): {} , "last_prediction_time": prediction_date, }
    for i in range(12):
        day = 0 if curr_hour < 24 else 1
        hour = curr_date.hour

        curr_weather = weather['days'][day]['hours'][hour]
        hour_temp = curr_weather['temp']
        hour_humidity = curr_weather['humidity']
        hour_windspeed = curr_weather['windspeed']
        hour_pressure = curr_weather['pressure']

        input_data = [[hour_temp, hour_humidity, hour_windspeed, hour_pressure]]
        # i need model params on this step
        prediction = model.predict(input_data)
        curr_date = curr_date + timedelta(hours=1)
        curr_hour = curr_hour + 1

        prediction_time = curr_date.strftime('%H:%M')
        prediction[str(region)][str(prediction_time)] = prediction
    
    save_prediction(prediction, region)

def save_prediction(prediction, region):
    with open(f"/home/vampir/lolitech/api/api_project/data/predictions/{str(region)}.json", "w") as f:
        json.dump(prediction,f)

def get_dates(date):
    date = date + timedelta(hours=1)
    date_from = date.replace(minute=0, second=0, microsecond=0)
    date_to = date_from + timedelta(hours=12)
    return [date_from, date_to]

if __name__ == "__main__":
    build_predictions()