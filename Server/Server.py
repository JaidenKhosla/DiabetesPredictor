import pickle
import shutil
import os

import pandas as pd
import numpy

from Model import *
from sklearn.preprocessing import LabelEncoder

from flask import Flask
import flask_cors

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
    print(directory)
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
        if(hasattr(self.model.model, "predict_proba")):
            return [self.model.model.predict_proba(self.dataframe)[0][1]]
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
            self.dataframe[encoder] = encoder[self.category][encoder].transform(self.dataframe[encoder])

        return self

    def add_model(self, category: str, model_key: str):
        self.model = models[category][model_key]
        self.category = category
        self.model_key = model_key
        return self
    