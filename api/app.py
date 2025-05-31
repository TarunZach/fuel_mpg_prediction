# app.py (updated to handle numpy data types for JSON serialization)

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

# Load models and expected column structure
regression_model = joblib.load("../models/XGBoost.pkl")
clustering_model = joblib.load("../models/Birch.pkl")
model_columns = joblib.load("../models/model_columns.pkl")


def preprocess_input(data):
    # Extract simplified fuel type (e.g., "G", "DU", "GPR", etc.)
    fuel_type_value = data.get("fuelType", "G")

    # Build raw input DataFrame
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

    # One-hot encode
    encoded = pd.get_dummies(raw_input)

    # Add missing columns
    for col in model_columns:
        if col not in encoded.columns:
            encoded[col] = 0

    # Reorder to match model input
    encoded = encoded[model_columns]
    return encoded


@app.route("/predict_mpg", methods=["POST"])
def predict_mpg():
    data = request.get_json()
    try:
        processed_input = preprocess_input(data)
        prediction = regression_model.predict(processed_input)[0]

        # Convert numpy float32 to Python float for JSON serialization
        prediction = float(prediction)

        # MPG rating label
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
        processed_input = preprocess_input(data)
        cluster_prediction = clustering_model.predict(processed_input)[0]

        # Convert numpy types to Python types for JSON serialization
        cluster = int(cluster_prediction)

        return jsonify(
            {
                "cluster": cluster,
                "confidence": 0.87,  # Placeholder value
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
