import joblib

#read pipeline from file
def load_pipeline(filepath):
    return joblib.load(filepath)
