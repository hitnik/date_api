from flask_restful import Resource, reqparse


class Date(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text')
        parser.parse_args()
        params = parser.parse_args()
        print(params)
        response = {
            'ok': True
        }

        return response, 200

