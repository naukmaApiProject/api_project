import os
import re

import numpy as np
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from num2words import num2words
import nltk

import csv

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

ISW_REPORTS_CSV = "isw_reports.csv"

def remove_date(data):
    data = data.read().splitlines(True)
    return data[1:]

def remove_one_letter_word(data):
    words = word_tokenize(str(data))
    new_text = ""
    for w in words:
        if(len(w) > 1):
            new_text = new_text + " " + w
    return new_text

def convert_lowercase(data):
    return np.char.lower(data)

def remove_stop_words(data):
    stop_words = set(stopwords.words('english'))
    stop_stop_words = {"no", "not"}
    stop_words = stop_words - stop_stop_words

    words = word_tokenize(str(data))
    new_text = ""
    for w in words:
        if w not in stop_words and len(w) > 1:
            new_text = new_text + " " + w
    return new_text

def remove_punctuation(data):
    symbols = "!\"#$%&()*+-./:;<=>?@[\]^_`{|}~\n"

    for i in range(len(symbols)):
        data = np.char.replace(data, symbols[i], ' ')
        data = np.char.replace(data, "  ", " ")
    data = np.char.replace(data, ",", "")
    return data

def remove_apostrophe(data):
    return np.char.replace(data, "`", "")

def stemming(data):
    stemmer = PorterStemmer()

    tokens = word_tokenize(str(data))
    new_text = ""
    for w in tokens:
        new_text = new_text + " " + stemmer.stem(w)
    return new_text

def lemmatiazing(data):
    lemmatizer = WordNetLemmatizer()

    tokens = word_tokenize(str(data))
    new_text = ""
    for w in tokens:
        new_text = new_text + " " + lemmatizer.lemmatize(w)
    return new_text

def convert_numbers(data):
    tokens = word_tokenize(str(data))
    new_text = ""
    for w in tokens:
        if w.isdigit():
            if int(w) < 10000000:
                w = num2words(w)
            else:
                w = ''
        new_text = new_text + " " + w
    new_text = np.char.replace(new_text, "-", " ")
    return new_text

def remove_url_from_string(data):
    words = word_tokenize(str(data))

    new_text = ""
    for w in words:
        w = re.sub(r'^http?:\/\/.*[\r\n]*', '', str(w), flags=re.MULTILINE)
        w = re.sub(r'^https?:\/\/.*[\r\n]*', '', str(w), flags=re.MULTILINE)
        new_text = new_text + " " + w
    return new_text



def preprocess(data, word_root_algo ="lemm"):
    data = remove_one_letter_word(data)
    data = remove_url_from_string(data)
    data = convert_lowercase(data)
    data = remove_punctuation(data)
    data = remove_apostrophe(data)
    data = remove_stop_words(data)
    data = convert_numbers(data)
    data = stemming(data)
    data = remove_punctuation(data)
    data = convert_numbers(data)

    if word_root_algo == "lemm":
        data = lemmatiazing(data)
    else:
        data = stemming(data)
    data = remove_punctuation(data)
    data = remove_stop_words(data)

    return data

def write_vectors_to_file(text):
    if(not os.path.exists("vectors")):
        os.makedirs("vectors")
    header = ['report_date','vector']
    with open(f'data_sources/{ISW_REPORTS_CSV}', 'w', encoding = "utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(text)

csv_data = []

for i in os.listdir("isw_reports"):
    if i.startswith("ISW"):
        print(i)
        with open(f'isw_reports/{i}', "r",encoding = "utf-8") as f:
            data = remove_date(f)
            vector = preprocess(data)
            date = i[4:14]
            row = [date, vector]
            csv_data.append(row)

write_vectors_to_file(csv_data)





