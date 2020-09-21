from flask import Blueprint
from  flask_restful import reqparse
v1_bp = Blueprint('v1', __name__)
from utils import BagOfWords

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
    print(params)
    response = {
        'ok': True
    }

    return response, 200