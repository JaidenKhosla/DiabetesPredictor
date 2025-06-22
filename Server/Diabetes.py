#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#imports for machine learning and parsing
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split # To split our data for fair testing
from sklearn.linear_model import LogisticRegression, LinearRegression  # The model itself!
from sklearn import preprocessing #LabelEncoders
from sklearn.preprocessing import PolynomialFeatures
from sklearn.base import RegressorMixin, ClassifierMixin
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVR
import math #for ceil
import json



#for typechecking
from typing import Sequence, Union
import numpy as np

#have to use threading bc svrs take way too long
import threading


# In[2]:


#loading our dataframe
diabetes_dataframe = pd.read_csv("Server/datasets/diabetes_prediction_dataset.csv")



# In[3]:


#replacements
#To convert categorical data into numerical data, I googled it and you use labelencoding.
genderEncoder = preprocessing.LabelEncoder()
smokingEncoder = preprocessing.LabelEncoder()

diabetes_dataframe["gender"] = genderEncoder.fit_transform(diabetes_dataframe["gender"])
diabetes_dataframe["smoking_history"] = smokingEncoder.fit_transform(diabetes_dataframe["smoking_history"])


# 1

# 

# In[4]:


#splitting
features = diabetes_dataframe[['gender', 'age', 'hypertension', 'heart_disease', 'smoking_history', 'bmi', 'HbA1c_level', 'blood_glucose_level']]
outputs = diabetes_dataframe[['diabetes']].values.ravel()

print(outputs)

features_train, features_test, outputs_train, outputs_test = train_test_split(features, outputs, test_size=0.1, random_state=1845)


# In[5]:


class Model:
    def __init__(self, model: RegressorMixin, transformModel=True):
        self.model = model
        if transformModel: model.fit(features_train, outputs_train)

    def test(self, model: RegressorMixin=None, features=features_test, outputs=outputs_test) -> float:
        if model is None: model = self.model
        return model.score(features, outputs)

    def predict(self, features: Union[Sequence[Sequence[float]], np.ndarray]):
        return self.model.predict(features)

    def predict_proba(self, features: Union[Sequence[Sequence[float]], np.ndarray]):
        if(hasattr(self.model, "predict_proba")):
            return [self.model.predict_proba(features)[0][1]]
        else:
            return self.predict(features)


class LinearModel(Model):
    def __init__(self, transformModel=True):
        super().__init__(LinearRegression(), transformModel)

class LogisticModel(Model):
    def __init__(self, max_iter: int, transformModel=True):
        super().__init__(LogisticRegression(max_iter=max_iter), transformModel)

class RandomForestClassifierModel(Model):
    def __init__(self, n_estimators: int, transformModel=True):
        super().__init__(RandomForestClassifier(n_estimators=n_estimators), transformModel)

class SupportVectorRegressionModel(Model):
    def __init__(self, mode:str, transformModel=True):
        super().__init__(SVR(kernel=mode), transformModel)

class PolynomialModel(Model):
    def __init__(self, maxDegree: int):
        maxModel = None
        score = -1
        self.poly: PolynomialFeatures = None
        for degree in range(1,maxDegree+1):
            iterFeatures = PolynomialFeatures(degree=degree, include_bias=False)
            polyTrainedFeatures = iterFeatures.fit_transform(features_train)

            iterLinear  = LinearModel(transformModel=False)
            iterLinear.model.fit(polyTrainedFeatures, outputs_train)


            iterScore = PolynomialModel.test(None,iterFeatures, iterLinear.model)
            if iterScore > score:
                maxModel = iterLinear
                score = iterScore
                self.poly = iterFeatures

        super().__init__(maxModel.model, False)

    def test(self, polyFeatures: PolynomialFeatures=None, model: LinearRegression=None) -> float:
        if model is None: model = self.model
        if polyFeatures is None: polyFeatures = self.poly

        return model.score(polyFeatures.transform(features_test), outputs_test)

    def predict(self, features: Union[Sequence[Sequence[float]], np.array]):
        return self.model.predict(self.poly.transform(features))


# In[6]:


# 

# In[ ]:


#multithreading for svcs
class Models:

    #model initialization
    
    models: dict[str, Model] = {}
    model_locks: dict[str, threading.Lock] = {}


    #linear model
    @staticmethod
    def linear_init():
        try:
            with Models.model_locks["linear"]:
                Models.models["linear"] = LinearModel()
                print("Linear model ready!")
        except Exception as e:
            print(f"Error initializing Linear model: {e}")

    #logisitc model
    @staticmethod
    def logistic_init():
        try:
            with Models.model_locks["logistic"]:
                Models.models["logistic"] = LogisticModel(1000)
                print("Logistic model ready!")
        except Exception as e:
            print(f"Error initializing Logistic model: {e}")

    #random forest model
    @staticmethod
    def random_forest_init():
        try:
            with Models.model_locks["random_forest"]:
                Models.models["random_forest"] = RandomForestClassifierModel(500)
                print("Random Forest ready!")
        except Exception as e:
            print(f"Error initializing Random Forest model: {e}")

    #support_vector linear model
    @staticmethod
    def svc_poly_init():
        try:
            with Models.model_locks["support_vector_linear"]:
                Models.models["support_vector_linear"] = SupportVectorRegressionModel("linear")
                print("SVC Linear Ready!")
        except Exception as e:
            print(f"Error initializing SVC Linear model: {e}")

    #support_vector polynomial model
    @staticmethod
    def svc_linear_init():
        try:
            with Models.model_locks["support_vector_poly"]:
                Models.models["support_vector_poly"] = SupportVectorRegressionModel("poly")
                print("SVC Poly Ready!")
        except Exception as e:
            print(f"Error initializing SVC Poly model: {e}")

    #polynomial model
    @staticmethod
    def poly_init():
        try:
            with Models.model_locks["poly"]:
                Models.models["polynomial"] = PolynomialModel(8)
                print("Poly model ready!")
        except Exception as e:
            print(f"Error initializing Poly model: {e}")


Models.model_locks = {k: threading.Lock() for k in ["linear", "logistic", "random_forest", "poly"]}
Models.threads = {
    "linear": threading.Thread(target=Models.linear_init),
    "logistic": threading.Thread(target=Models.logistic_init),
    "random_forest": threading.Thread(target=Models.random_forest_init),
    "poly": threading.Thread(target=Models.poly_init)
}
for thread in Models.threads.values():
    thread.start()



# In[14]:


# def test():
#   error = 0
#   for i in range(0, len(outputs_test)):
#     error+=(float(prediction_test[i])-float(outputs_test[i]))**2
#   error/=len(outputs_test)
#   error**=0.5
#   print(f"Error: {error}")
#   print(f"R^2: {model.score(features_test,outputs_test)}")

#   newDf = pd.DataFrame([{
#     "gender": "Male",
#     "age": 12.0,
#     "hypertension": 1,
#     "heart_disease": 1,
#     "smoking_history": "current",
#     "bmi": 23.86,
#     "HbA1c_level": 4.8,
#     "blood_glucose_level": 157.0
#   }])

#   newDf["gender"] = genderEncoder.transform(newDf["gender"])
#   newDf["smoking_history"] = smokingEncoder.transform(newDf["smoking_history"])




# In[15]:


class Predictor:


    def __init__(self, dataframe: pd.DataFrame, model: Model=None):
        self.dataframe = dataframe
        self.model = model

    def predict(self):
        return self.model.predict(self.dataframe)

    def predict_proba(self):
        return self.model.predict_proba(self.dataframe)

    @staticmethod
    def parse_json(unparsed_json: str):
        parsed_json = json.loads(unparsed_json)
        return Predictor.json_to_frame(parsed_json)

    @staticmethod
    def json_to_frame(parsed_json: dict):
        return Predictor(pd.DataFrame([parsed_json]))

    def add_model(self, model: Model):
        return Predictor(self.dataframe, model)

    def convert_binary_values(self):

        self.dataframe["gender"] = genderEncoder.transform(self.dataframe["gender"])
        self.dataframe["smoking_history"] = smokingEncoder.transform(self.dataframe["smoking_history"])

        return self



# jsonPredict = Predictor.parse_json("""{
#     \"gender\" : \"Male\",
#     \"age\" : 12.0,
#     \"hypertension\": 1,
#     \"heart_disease\": 1,
#     \"smoking_history\": \"current\",
#     \"bmi\" : 23.86,
#     \"HbA1c_level\": 4.8,
#     \"blood_glucose_level\": 157.0
# }""").convert_binary_values().add_model(models["logistic"]).predict()
# print(jsonPredict)

