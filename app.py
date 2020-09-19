from flask import Flask
from flask_restful import Api
from api import Date

app = Flask(__name__)

api = Api(app)

api.add_resource(Date, '/parse-date/')

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
