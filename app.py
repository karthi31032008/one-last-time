
import os
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
# FIREBASE ADMIN CONNECTION
if not firebase_admin._apps:
    cred = credentials.Certificate(
        "/etc/secrets/serviceAccountKey.json"
    )
    firebase_admin.initialize_app(cred)

db = firestore.client()

# SECURITY
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "development-only-change-before-deployment"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GAEZ DATASET PATH
GAEZ_DATA_FILE = Path("data/gaez/crop_suitability.json")


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# HEALTH CHECK
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "application": "FarmShift AI",
        "message": "Backend is running successfully",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200


# PLATFORM INFORMATION
@app.route("/api/platform")
def platform_info():
    return jsonify({
        "name": "FarmShift AI",
        "description": "Agricultural Earth Intelligence Platform",
        "modules": [
            "Crop Suitability",
            "Water Intelligence",
            "Climate Analysis",
            "Land Observation",
            "Market Intelligence",
            "Data Intelligence"
        ],
        "status": "development"
    })


# GAEZ DATASET DETECTION
@app.route("/api/gaez-status")
def gaez_status():

    if not GAEZ_DATA_FILE.is_file():
        return jsonify({
            "status": "pending",
            "source": "FAO GAEZ",
            "dataset_available": False,
            "message": "GAEZ dataset file not found."
        })

    try:
        with GAEZ_DATA_FILE.open("r", encoding="utf-8") as file:
            dataset = json.load(file)

        if not isinstance(dataset, (dict, list)):
            raise ValueError("Unexpected dataset format")

        return jsonify({
            "status": "detected",
            "source": "FAO GAEZ",
            "dataset_available": True,
            "message": "GAEZ dataset file detected successfully."
        })

    except (OSError, json.JSONDecodeError, ValueError):
        logger.exception("GAEZ dataset validation failed")

        return jsonify({
            "status": "error",
            "source": "FAO GAEZ",
            "dataset_available": False,
            "message": "GAEZ dataset could not be validated."
        }), 500


# GAEZ CROP SUITABILITY REQUEST
@app.route("/api/gaez-detect", methods=["POST"])
def gaez_detect():

    data = request.get_json(silent=True) or {}

    try:
        latitude = float(data.get("latitude"))
        longitude = float(data.get("longitude"))
    except (TypeError, ValueError):
        return jsonify({
            "status": "error",
            "message": "Valid coordinates are required."
        }), 400

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return jsonify({
            "status": "error",
            "message": "Invalid latitude or longitude."
        }), 400

    crop = str(data.get("crop", "")).strip()

    if not crop:
        return jsonify({
            "status": "error",
            "message": "Please select a crop."
        }), 400

    if not GAEZ_DATA_FILE.is_file():
        return jsonify({
            "status": "pending",
            "source": "FAO GAEZ",
            "dataset_available": False,
            "crop": crop,
            "latitude": latitude,
            "longitude": longitude,
            "message": "GAEZ dataset integration is pending. No suitability score calculated."
        })

    return jsonify({
        "status": "detected",
        "source": "FAO GAEZ",
        "dataset_available": True,
        "crop": crop,
        "latitude": latitude,
        "longitude": longitude,
        "message": "Dataset detected. Actual spatial suitability processing requires the GAEZ dataset schema and raster lookup."
    })
# CROP SUITABILITY
@app.route("/crop-suitability")
def crop_suitability():
    return render_template("crop_suitability.html")

# WATER INTELLIGENCE
@app.route("/water-intelligence")
def water_intelligence():
    return render_template("water_intelligence.html")


# CLIMATE ANALYSIS
@app.route("/climate-analysis")
def climate_analysis():
    return render_template("climate_analysis.html")


# LAND OBSERVATION
@app.route("/land-observation")
def land_observation():
    return render_template("land_observation.html")


# MARKET INTELLIGENCE
@app.route("/market-intelligence")
def market_intelligence():
    return render_template("market_intelligence.html")


# DATA INTELLIGENCE
@app.route("/data-intelligence")
def data_intelligence():
    return render_template("data_intelligence.html")




# ERROR HANDLERS
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Page not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.exception("Internal server error")
    return jsonify({"error": "Internal server error"}), 500


# START SERVER
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
