from flask import Flask
from v1 import v1_bp

app = Flask(__name__)
app.config['BUNDLE_ERRORS'] = True
app.register_blueprint(v1_bp, url_prefix='/v1')


if __name__ == '__main__':
    app.run()
