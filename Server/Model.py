#imports for machine learning and parsing
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split # To split our data for fair testing
from sklearn.linear_model import LogisticRegression, LinearRegression  # The model itself!
from sklearn import preprocessing #LabelEncoders
from sklearn.preprocessing import PolynomialFeatures
from sklearn.base import RegressorMixin
from sklearn.ensemble import RandomForestClassifier
import math #for ceil
import json

import pickle
from sklearn import datasets
#server imports
from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS

#for typechecking
from typing import Sequence, Union
import numpy as np

class Model:
    def __init__(self, model: RegressorMixin, transformModel=True):
        self.model = model
    
    def test(self, model: None, features, outputs) -> float:
        if model is None: model = self.model
        return model.score(features, outputs)
    
    def predict(self, features: Union[Sequence[Sequence[float]], np.ndarray]):
        return self.model.predict(features)
    
    def fit(self, features: Union[Sequence[Sequence[float]]], outputs: Union[Sequence[Sequence[float]]]):
        return self.model.fit(features, outputs)

class LinearModel(Model):
    def __init__(self, transformModel=True):
        super().__init__(LinearRegression(), transformModel)

class LogisticModel(Model):
    def __init__(self, transformModel=True):
        super().__init__(LogisticRegression(max_iter=1000), transformModel)

class RandomForestModel(Model):
    def __init__(self, trees: int,transformModel=True):
        super().__init__(RandomForestClassifier(n_estimators=trees), transformModel)

class PolynomialModel(Model):
    def __init__(self, maxDegree: int, features_train, outputs_train):
        self.features_train = features_train
        self.outputs_train = outputs_train
        maxModel = None
        score = -1
        self.poly: PolynomialFeatures = None
        for degree in range(1,maxDegree+1):
            iterFeatures = PolynomialFeatures(degree=degree, include_bias=False)
            polyTrainedFeatures = iterFeatures.fit_transform(features_train)

            iterLinear  = LinearModel(transformModel=False)
            iterLinear.model.fit(polyTrainedFeatures, outputs_train)
    

            iterScore = self.test(iterFeatures, iterLinear.model)
            if iterScore > score:
                maxModel = iterLinear
                score = iterScore
                self.poly = iterFeatures
               
        super().__init__(maxModel.model, False)

    def test(self, polyFeatures: PolynomialFeatures=None, model: LinearRegression=None) -> float:
        if model is None: model = self.model
        if polyFeatures is None: polyFeatures = self.poly
        
        return model.score(polyFeatures.transform(self.features_train), self.outputs_train)
    
    def predict(self, features: Union[Sequence[Sequence[float]], np.array]):
        return self.model.predict(self.poly.transform(features))

def save_to_pickle(key: str, model, path: str="../Server/models/Diabetes/"):

    print(key)
    print(path)
    print(f"{model}{key}.pkl")
    pickle.dump(model, open(f"{path}{key}.pkl", "wb"))