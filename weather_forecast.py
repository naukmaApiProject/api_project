import os

import requests
import datetime
import matplotlib.pyplot as plt

API_KEY = 'PXAMV42AU6LKXV828GP3UCWGH'
CITY = "KYIV"
UNIT_GROUP = "metric"
COUNTRY= "UKRAINE"
FROM_DATE = datetime.datetime.now().date()
TO_DATE = None
FORECAST_HOURS = 12

def get_forecast():
    return requests.get(f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
                        f"{CITY},{COUNTRY}/{FROM_DATE}/{TO_DATE}?unitGroup={UNIT_GROUP}&key={API_KEY}")

def parse_json_response(response_json, current_hour):
    data = []
    hours_count = 0
    for day in response_json["days"]:
        for hour in day["hours"]:
            iso_hour = datetime.time(current_hour, 0, 0)
            if(str(iso_hour) == "00:00:00") :
                data.append(hour)
                if(hours_count < FORECAST_HOURS):
                    current_hour += 1
                    hours_count+=1
            elif(str(iso_hour) == hour["datetime"]):
                data.append(hour)
                if(hours_count < FORECAST_HOURS):
                    current_hour += 1
                    if(current_hour==24): current_hour = 0
                    hours_count+=1
    write_report_to_file(data)
    return dict(map(lambda dataObject: (str(dataObject['datetime']).split(":")[0], dataObject['temp']), data))

def write_report_to_file(data):
    if(not os.path.exists("weather_forecasts")):
        os.makedirs("weather_forecasts")
    with open(f'weather_forecasts/{str(datetime.datetime.now())}', 'w', encoding = "utf-8") as file:
        for i in data:
            file.write(str(i))

def visualize(data):
    values = list(data.values())
    colors = list(map(lambda temp: "red" if temp > 0 else "blue", values))
    plt.bar(range(len(data)), values, color = colors)
    plt.xticks(range(len(data)), list(data.keys()))
    plt.title('Time to Temperature plot')
    plt.xlabel('hours')
    plt.ylabel('temperature')
    plt.show()


current_hour = datetime.datetime.now().time().hour
if(current_hour < FORECAST_HOURS):
    TO_DATE = datetime.datetime.now().date()
    response = get_forecast()
else:
    TO_DATE = datetime.date.today() + datetime.timedelta(days=1)
    response = get_forecast()

data = parse_json_response(response.json(), current_hour)
visualize(data)
