from flask import Blueprint, send_file
v1_bp = Blueprint('v1', __name__)
from flask_restful import reqparse
import re
import csv
import nltk
from nltk.corpus import stopwords
from nltk.util import ngrams
from flask import current_app
from os import path
import datetime

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

DAYS = ['4', '30', '29', '31', '13-14', '21', '25', '7-8', '12-13',
        '18-19', '23-24', '29-30', '10', '28', '2-3', '17', '7', '26',
        '15-16', '9-10', '1', '19-20', '22-23', '26-27', '11-12', '3',
        '12', '18', '15', '8-9', '21-22', '27', '25-26', '6-7', '22',
        '4-5', '20', '11', '17-18', '20-21', '5', '16-17', '23', '5-6',
        '14', '24', '24-25', '10-11', '9', '30-31', '1-2', '2', '28-29',
        '14-15' , '27-28', '13', '6', '8', '19', '16', '3-4'
        ]

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
        with open(path.join(current_app.root_path, 'data', 'words_bag.csv'),
                  encoding='utf-8', newline='') as csvfile:
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
        for item in DAYS:
            days_dict[item] = 0
        for name, value in d.items():
            for k,v in days_dict.items():
                for mon in MONTHS_GEN.values():
                    pattern = k+mon
                    if pattern == name:
                        days_dict[k] += int(value)
        return list(days_dict.values())



def predict_date(month_bag, days_bag, text):
    """
    predict date start and date and by month_bag and days_bag
    :param month_bag:
    :param days_bag:
    :return: date_start, date_end
    """
    if sum(month_bag)+sum(days_bag) == 0:
        return None, None
    else:
        month = current_app.pipeline_month.predict([month_bag])
        day_start = current_app.pipeline_day_start.predict([days_bag])
        day_end = current_app.pipeline_day_end.predict([days_bag])
        year = datetime.date.today().year
        date_start = datetime.date(year, int(month), int(day_start))
        date_end = datetime.date(year, int(month), int(day_end))
        with open(path.join(current_app.root_path, 'data', 'test_data.csv'),
                  'a', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([text, int(month), int(day_start), int(day_end)])
        return date_start, date_end

v1_bp = Blueprint('v1', __name__)

@v1_bp.route('parse-date',  methods=['POST'])
def date_parser():
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument('text',
                        type=str,
                        required=True,
                        help='text is required'
                        )
    parser.parse_args()
    params = parser.parse_args()
    bag = BagOfWords(params['text'])
    month_bag = bag.months_bag
    days_bag = bag.days_bag
    date_start, date_end = predict_date(month_bag, days_bag, params['text'])
    response = {
        'start': date_start,
        'end': date_end
    }
    return response, 200

@v1_bp.route('trained-sample', methods=['GET'])
def trained_sample():
    filepath = path.join(current_app.root_path, 'data', 'test_data.csv')
    try:
        return send_file(filepath,as_attachment=True,
                         attachment_filename='trained_sample.csv',  mimetype='text/csv')
    except FileNotFoundError:
        response = {
            'Error': 'File not found'
        }
        return response, 404