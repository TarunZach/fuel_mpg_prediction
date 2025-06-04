from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd

app = Flask(__name__)
CORS(app)

CLUSTER_LABELS = {
    2: "Compact & Efficient",
    0: "Standard/Mid-range",
    1: "High Power / Utility",
}

# Load models and preprocessing components
regression_model = joblib.load("../models/XGBoost_simple.pkl")
clustering_model = joblib.load("../models/KMeans_simple.pkl")
key_columns = joblib.load("../models/key_columns.pkl")
simplified_scaler = joblib.load("../models/simplified_scaler.pkl")


def preprocess_input(data):
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
    return simplified_scaler.transform(encoded)


@app.route("/predict_mpg", methods=["POST"])
def predict_mpg():
    data = request.get_json()
    try:
        input_scaled = preprocess_input(data)
        prediction = regression_model.predict(input_scaled)[0]
        label = (
            "🚀 Excellent"
            if prediction >= 35
            else "👍 Good"
            if prediction >= 25
            else "😐 Average"
            if prediction >= 18
            else "👎 Poor"
        )
        return jsonify({"mpg": round(float(prediction), 2), "label": label})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/predict_cluster", methods=["POST"])
def predict_cluster():
    data = request.get_json()
    try:
        input_scaled = preprocess_input(data)
        cluster = int(clustering_model.predict(input_scaled)[0])
        label = CLUSTER_LABELS.get(cluster, f"Cluster {cluster}")
        return jsonify(
            {
                "cluster": cluster,
                "label": label,
                "confidence": 0.87,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
    # Production: app.run(host="0.0.0.0", port=5000)
