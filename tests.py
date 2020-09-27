import unittest
from app import app
import csv
from os import path
import datetime
import json
import dateutil.parser

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_only_post_page(self):
        response = self.app.get('v1/parse-date', content_type='json')
        self.assertEqual(response.status_code, 405)
        response = self.app.put('v1/parse-date', content_type='json')
        self.assertEqual(response.status_code, 405)
        response = self.app.delete('v1/parse-date', content_type='json')
        self.assertEqual(response.status_code, 405)

    def test_data(self):
        with open((path.join(app.root_path, '', 'data/test_data.csv')), encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                text = row['text']
                month = row['month']
                day_start = row['day_start']
                day_end = row['day_end']
                year = datetime.date.today().year
                date_start_manual = datetime.date(year, int(month), int(day_start))
                date_end_manual = datetime.date(year, int(month), int(day_end))
                response = self.app.post('v1/parse-date',  data=json.dumps({'text':text}),
                                            content_type='application/json'
                                         )

                def datetime_parser(json_dict):
                    for (key, value) in json_dict.items():
                        try:
                            json_dict[key] = dateutil.parser.parse(value)
                        except (ValueError, AttributeError):
                            pass
                    return json_dict

                dict = json.loads(response.data, object_hook=datetime_parser)
                date_start = datetime.date(dict['start'].year, dict['start'].month, dict['start'].day)
                date_end = datetime.date(dict['end'].year, dict['end'].month, dict['end'].day)
                self.assertEqual(date_start_manual, date_start)
                self.assertEqual(date_end_manual, date_end)

if __name__ == '__main__':
    unittest.main()