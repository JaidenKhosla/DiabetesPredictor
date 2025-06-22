#server imports
from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS

from Diabetes import Predictor, Models

import tracemalloc

app = Flask(__name__)
CORS(app)

#App Route
@app.route("/generate", methods=["POST"])
def generate():
        try:
            clientJson = request.json

            model = clientJson["model"]
            features = clientJson["features"]


            if model not in Models.threads or model not in Models.model_locks:
                return jsonify({"res": f"The {model} model isn't a model."})
            
            if Models.threads[model].is_alive():
                return jsonify({"res": f"The {model} model isn't ready yet."})
            
            if model not in Models.models:
                return jsonify({"res": f"The {model} model hasn't be initialized yet."})
            
            with Models.model_locks[model]:
                print("Features:", features)
                predictModel = Predictor.json_to_frame(features)
                print("DataFrame after json_to_frame:", predictModel.dataframe)
                predictModel = predictModel.convert_binary_values()
                print("DataFrame after convert_binary_values:", predictModel.dataframe)
                predictModel = predictModel.add_model(Models.models[model])
                res = [float(predictModel.predict()[0]), float(predictModel.predict_proba()[0])]
                
                return jsonify({"result": res})

        except Exception as e:
             import traceback
             traceback.print_exc()
             return jsonify({"error": str(e)}), 500
    
@app.route("/ping", methods=["GET"])
def ping():
     return "pong"

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)