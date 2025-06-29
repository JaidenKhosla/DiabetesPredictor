import pickle
import shutil
import os

import pandas as pd
import numpy

from Model import *
from sklearn.preprocessing import LabelEncoder

from flask import Flask
from flask import request
from flask_cors import CORS

parentDirectory = "./Server/models/"
encoderDirectory = "./Server/encoders/"

models : dict[str : dict[str: ]] = {
}

encoders: dict[str: dict[str: LabelEncoder]] = {

}

for directory in list(os.walk(parentDirectory))[1:]:
    directoryName = directory[0]
    parsedDirectory = directoryName.replace(parentDirectory, "")
    
    models[parsedDirectory] = {}
    pklFiles = directory[2]

    for pklFile in pklFiles:
        pklFilePath = f"{directoryName}/{pklFile}"

        pklFileName = pklFile.replace(".pkl", "")

        models[parsedDirectory][pklFileName] = pickle.load(open(pklFilePath, "rb"))

for directory in list(os.walk(encoderDirectory))[1:]:
    directoryName = directory[0]
    parsedDirectory = directoryName.replace(encoderDirectory, "")
    
    encoders[parsedDirectory] = {}
    pklFiles = directory[2]

    for pklFile in pklFiles:
        pklFilePath = f"{directoryName}/{pklFile}"

        pklFileName = pklFile.replace(".pkl", "")

        encoders[parsedDirectory][pklFileName] = pickle.load(open(pklFilePath, "rb"))  

class Predictor:

    dataframe: pd.DataFrame

    def __init__(self, dataframe: pd.DataFrame, category: str=None, model_key: str=None):
        self.dataframe = dataframe
        if category != None and model_key != None: self.model = models[category][model_key]
        self.category = category
        self.model_key = model_key

    def predict(self):
        return self.model.predict(self.dataframe)
    
    def predict_proba(self):
        if(hasattr(self.model, "predict_proba")):
            return [self.model.predict_proba(self.dataframe)[0][1]]
        else:
            return self.predict()
    
    @staticmethod
    def parse_json(unparsed_json: str):
        parsed_json = json.loads(unparsed_json)
        return Predictor.json_to_frame(parsed_json)
    
    @staticmethod
    def json_to_frame(parsed_json: dict):
        return Predictor(pd.DataFrame([parsed_json]))

    def convert_binary_values(self):
        
        for encoder in encoders[self.category]:
            print(encoder)
            self.dataframe[encoder] = encoders[self.category][encoder].transform(self.dataframe[encoder])

        if self.category == "HeartDisease":
            self.dataframe["sex_0"] = [1 if self.dataframe["sex"].astype("int")[0] == 0 else 0]
            self.dataframe["sex_1"] = [1 if self.dataframe["sex"].astype("int")[0] == 1 else 0]
            self.dataframe = self.dataframe.drop(columns=["sex"])
        return self

    def add_model(self, category: str, model_key: str):
        self.model = models[category][model_key]
        self.category = category
        self.model_key = model_key
        return self
    


app = Flask(__name__)
CORS(app)

"""
{
category: "HeartDisease",
model: "Linear",

}
"""

@app.route("/generate", methods=["POST"])
def generate():
    clientJson = request.json

    category = clientJson["category"]
    model = clientJson["model"]
    features = clientJson["features"]

    if(models.get(category, None) == None):
        return jsonify({"result": f"The {category} category doesn't exist."})

    if(models[category].get(model, None) == None):
        return jsonify({"result": f"The {model} model doesn't exist."})

    currModel = Predictor.json_to_frame(features).add_model(category, model).convert_binary_values()

    prediction = float(currModel.predict()[0])
    probability = float(currModel.predict_proba()[0])

    return jsonify({"result": [prediction, probability]})
if __name__ == "__main__":
    app.run()

# req = {
#     "category": "Diabetes",
#     "model": "Logistic",
#     "features" : {
#         "gender" : "Male",
#         "age" : 12.0,
#         "hypertension": 1,
#         "heart_disease": 1,
#         "smoking_history": "current",
#         "bmi" : 23.86,
#         "HbA1c_level": 4.8,
#         "blood_glucose_level": 157.0
#     }
# }

 

# print(Predictor.json_to_frame(req["features"]).add_model(req["category"], req["model"]).convert_binary_values().predict())