from flask import Blueprint
from  flask_restful import reqparse
v1_bp = Blueprint('v1', __name__)
from utils import BagOfWords
from utils import predict_date

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
    date_start, date_end = predict_date(month_bag, days_bag)
    response = {
        'start': date_start,
        'end': date_end
    }
    return response, 200