import re
import csv
import nltk
from nltk.corpus import stopwords
from nltk.util import ngrams
import joblib
import pandas as pd
from os import path


MONTHS_GEN = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря"
}

def clear_words(words):
    stop_words = stopwords.words('russian')
    stop_words.extend(['что', 'это', 'так', 'вот', 'быть', 'как', 'в', 'к', 'на','см',
                       '...', '..', ',', '.', 'м/с', 'В', '(', ')', ':', '-', '–', ';', '!'])
    cleared = []
    for word in words:
        if word.lower() not in stop_words:
            if not re.search('°', word)\
                    and not re.match(r'^[-\+]\d+', word):
                    cleared.append(word.lower())

    return cleared

def count_words_in_list(word, list):
    count = 0
    for i in list:
        if word == i:
            count += 1
    return count

def filter_months_in_bag(d):
    result = {}
    month_list = list(MONTHS_GEN.values())
    for month in month_list:
        for k, v in d.items():
            if k == month:
                result[month] = v
    return result

class BagOfWords():

    def __init__(self, sentence):
        self._sentence = sentence
        self._bag_dict = self._sentence_to_bagofwords()

    def _primary_clearing(self):
        pattern = re.compile('\d+((\s-\s)|(\s-)|(-\s))\d+')
        if re.search(pattern, self._sentence):
            match = re.search(pattern, self._sentence).group()
            new = match.replace(' ', '')
            self._sentence = self._sentence.replace(match, new)
        pattern_and = re.compile('\d+\sи\s\d+')
        if re.search(pattern_and, self._sentence):
            match = re.search(pattern_and, self._sentence).group()
            new = match.replace(' и ', '-')
            self._sentence = self._sentence.replace(match, new)

    def _sentence_to_bagofwords(self):
        bag = []
        d = {}
        with open('words_bag.csv', encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                item = row['bag']
                bag.append(str(item))

        self._primary_clearing()

        words = nltk.word_tokenize(self._sentence)
        cleared_words = clear_words(words)
        bigrams = ngrams(cleared_words, 2)
        uniom_grams = set()
        for item in bigrams:
            sum = ''
            for i in item:
                sum+=i
                uniom_grams.add(sum)
        for item in bag:
            d[item] = count_words_in_list(item, uniom_grams)
        return d

    @property
    def months_bag(self):
        d = self._bag_dict
        month_dict = {}
        for month in MONTHS_GEN.values():
            month_dict[month] = 0
        for key, value in d.items():
            for k, v in month_dict.items():
                pattern = re.compile(k + '$')
                if re.search(pattern, key):
                    month_dict[k] += int(value)
        return list(month_dict.values())

    @property
    def days_bag(self):
        d = self._bag_dict
        days_dict = {}
        with open('./data/weather_data_days.csv', encoding='utf-8', newline='') as csvfile:
            reader = csv.reader(csvfile)
            row_names = next(reader)
            row_names.remove('day_start')
            row_names.remove('day_end')
            row_names.remove('text')
        for item in row_names:
            days_dict[item] = 0
        for name, value in d.items():
            for k,v in days_dict.items():
                for mon in MONTHS_GEN.values():
                    pattern = k+mon
                    if pattern == name:
                        days_dict[k] += int(value)
        return list(days_dict.values())


#Save the pipeline
def save_pipeline(filepath, pipeline_to_persist) -> None:
    joblib.dump(pipeline_to_persist, filepath)

#read pipeline from file
def load_pipeline(filepath):
    return joblib.load(filepath)

def read_data(filepath):
    return pd.read_csv(filepath)

def split_data(data, exlude_columns, predict_column):

    X = data.drop(exlude_columns, axis=1)
    y = data[predict_column].astype('int64')

    return X, y