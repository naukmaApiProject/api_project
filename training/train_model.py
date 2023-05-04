import random
import uuid

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.models import load_model
from tensorflow.keras import Input
from typing import List
from sklearn import preprocessing
import pandas as pd
import numpy as np
import math



class DataObject:
    date: float
    alarm: float
    region: int
    hour_temp: float
    day_temp_max: float
    day_temp_min: float
    day_temp: float
    day_temp2: float
    day_humidity: float
    hour: float
    hour_humidity: float
    hour_dew: float
    alarm: float

    def __str__(self):
        return f"DataObject(date={self.date}, alarm={self.alarm}, region={self.region}, day_temp_max={self.day_temp_max}, day_temp_min={self.day_temp_min}, day_temp={self.day_temp}, day_humidity={self.day_humidity}, hour={self.hour}, hour_temp={self.hour_temp}, hour_humidity={self.hour_humidity}, hour_dew={self.hour_dew}"


vectorizer = TfidfVectorizer()
data_list = [  ]  # here we store all out data objects

skip_first = True
count =  0  # remove it later
with open(f'/app/data/merged/all_data.csv', 'r', encoding="utf-8") as input_file:  # input file is all_data.csv
    with open(f'/app/data/merged/new_all_data.csv', 'w') as output_file:
        # for now the data after processing is not written to file
        for i in input_file:
            count += 1  #
            if skip_first:  # this is used to skip first line with column names
                skip_first = False
                continue
            # if count % 2 > 0:
            # continue
            # print(count)
            data_string = i.split(";")  # split line on items
            data_object = DataObject()
            data_object.date = float(data_string[2])
            data_object.day_temp_max = float(data_string[3])
            data_object.day_temp_min = float(data_string[4])
            data_object.day_temp = float(data_string[5])
            data_object.day_humidity = float(data_string[7])
            data_object.hour = float(data_string[18].split(":")[0])
            data_object.day_temp2 = float(data_string[19])
            data_object.hour_humidity = float(data_string[20])
            data_object.hour_dew = float(data_string[21])
            data_object.hour_temp = float(data_string[20])
            data_object.region = int(data_string[44])
            data_object.alarm = 1 if data_string[-4] == 'True' else 0
            data_list.append(data_object)

df = pd.DataFrame([d.__dict__ for d in data_list])
normalized_df = (df - df.mean()) / df.std(ddof=0)  # example normalization
# print(normalized_df[3])
# Prepare the data
X = []
y = []
# for ind in df.index:
#   if df["region"][ind] != 3:
#    print(df["region"][ind])

for ind in normalized_df.index:
    X.append([normalized_df["date"][ind], normalized_df["region"][ind], normalized_df["day_temp_max"][ind],
              normalized_df["day_temp_min"][ind], normalized_df["day_temp"][ind], normalized_df["day_temp2"][ind],
              normalized_df["day_humidity"][ind], normalized_df["hour"][ind], normalized_df["hour_temp"][ind],
              normalized_df["hour_humidity"][ind], normalized_df["hour_dew"][ind]])
    y.append(1 if normalized_df["alarm"][ind] > 0 else 0)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = Sequential()
model.add(Input(shape=(11,)))
model.add(Dense(88, activation='relu'))
model.add(Dropout(rate=0.01))
model.add(Dense(44, activation='relu'))
# model.add(Dropout(rate=0.01))
model.add(Dense(22, activation='relu'))
# model.add(Dropout(rate=0.01))
model.add(Dense(11, activation='elu'))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=80, batch_size=10, verbose=1)
scores = model.evaluate(X_test, y_test, verbose=0)
print("%s: %.2f%%" % (model.metrics_names[1], scores[1] * 100))
scores = model.evaluate(X_train, y_train, verbose=0)
print("%s: %.2f%%" % (model.metrics_names[1], scores[1] * 100))

model_uuid = uuid.uuid4()
model.save(f'/app/models/model{model_uuid}.h5')
print('Model Saved!')

# load model
savedModel = load_model(f'/app/models/model{model_uuid}.h5')
savedModel.summary()

predictions = (savedModel.predict(X_test) > 0.5).astype(int)
# summarize the first 5 cases
for i in range(100):
    print('%s (expected %d)' % (predictions[i], y_test[i]))