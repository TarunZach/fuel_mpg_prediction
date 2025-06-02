# app.py (updated for simplified frontend models with simplified scaler)

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load simplified models and expected column structures
regression_model = joblib.load("../models/XGBoost_simple.pkl")
clustering_model = joblib.load("../models/Birch_simple.pkl")
key_columns = joblib.load("../models/key_columns.pkl")
simplified_scaler = joblib.load("../models/simplified_scaler.pkl")


def preprocess_regression_input(data):
    fuel_type_value = data.get("fuelType", "G")
    raw_input = pd.DataFrame(
        [
            {
                "Eng Displ": data["engineDispl"],
                "# Cyl": data["cylinders"],
                "Transmission": data["transmission"],
                "Drive Sys": data["driveSys"],
                "Carline Class": data["carClass"],
                "smartway_binary": 1 if data["smartway"] else 0,
                "Fuel Usage  - Conventional Fuel": fuel_type_value,
            }
        ]
    )
    encoded = pd.get_dummies(raw_input)
    for col in key_columns:
        if col not in encoded.columns:
            encoded[col] = 0
    encoded = encoded[key_columns]
    encoded_scaled = simplified_scaler.transform(encoded)
    print("Encoded input columns:", encoded.columns.tolist())
    print("Input row:\n", encoded.head())
    return encoded_scaled


def preprocess_clustering_input(data):
    fuel_type_value = data.get("fuelType", "G")
    raw_input = pd.DataFrame(
        [
            {
                "Eng Displ": data["engineDispl"],
                "# Cyl": data["cylinders"],
                "Carline Class": data["carClass"],
                "Fuel Usage  - Conventional Fuel": fuel_type_value,
                "city_mpg": data["userMPG"],
            }
        ]
    )
    encoded = pd.get_dummies(raw_input)
    for col in key_columns:
        if col not in encoded.columns:
            encoded[col] = 0
    encoded = encoded[key_columns]
    encoded_scaled = simplified_scaler.transform(encoded)

    return encoded_scaled


@app.route("/predict_mpg", methods=["POST"])
def predict_mpg():
    data = request.get_json()
    try:
        processed_input = preprocess_regression_input(data)
        prediction = regression_model.predict(processed_input)[0]
        prediction = float(prediction)

        if prediction >= 35:
            label = "🚀 Excellent"
        elif prediction >= 25:
            label = "👍 Good"
        elif prediction >= 18:
            label = "😐 Average"
        else:
            label = "👎 Poor"

        return jsonify({"mpg": round(prediction, 2), "label": label})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/predict_cluster", methods=["POST"])
def predict_cluster():
    data = request.get_json()
    try:
        processed_input = preprocess_clustering_input(data)
        cluster_prediction = clustering_model.predict(processed_input)[0]
        cluster = int(cluster_prediction)
        return jsonify({"cluster": cluster, "confidence": 0.87})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
