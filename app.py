from flask import Flask
from v1 import v1_bp
from pipelines.utils import load_pipeline


from os import path

app = Flask(__name__)
app.config['BUNDLE_ERRORS'] = True

pipeline_month = load_pipeline((path.join(app.root_path,
                                          'pipelines', 'month_pipeline.pkl.gz')))
pipeline_day_start = load_pipeline((path.join(app.root_path,
                                          'pipelines', 'day_start_pipeline.pkl.gz')))
pipeline_day_end = load_pipeline((path.join(app.root_path,
                                          'pipelines', 'day_end_pipeline.pkl.gz')))



app.register_blueprint(v1_bp, url_prefix='/v1')


if __name__ == '__main__':
    app.run()
