
import os
import json
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
import requests
import firebase_admin
from firebase_admin import credentials, firestore

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
# FIREBASE ADMIN CONNECTION
if not firebase_admin._apps:
    cred = credentials.Certificate(
        "/etc/secrets/serviceAccountKey.json"
    )
    firebase_admin.initialize_app(cred)

db = firestore.client()
print("Firebase connected successfully!")
try:
    db.collection("connection_test").document("test").set({
        "status": "connected"
    })
    print("FIREBASE DATABASE CONNECTED")
except Exception as e:
    print("FIREBASE DATABASE ERROR:", e)

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

# ==========================================
# SCIENTIFIC DATA SOURCE DETAILS
# ==========================================

DATA_SOURCES = {
    "nasa-power": {
        "title": "NASA POWER",
        "category": "Climate Intelligence",
        "agency": "NASA Langley Research Center",
        "description": "NASA POWER provides satellite and model-based solar and meteorological data for agricultural and environmental applications.",
        "observations": [
            "T2M - Air temperature at 2 metres",
            "T2M_MAX - Maximum air temperature",
            "T2M_MIN - Minimum air temperature",
            "PRECTOTCORR - Corrected precipitation",
            "RH2M - Relative humidity",
            "WS2M - Wind speed at 2 metres",
            "ALLSKY_SFC_SW_DWN - Solar radiation"
        ],
        "applications": [
            "Crop climate assessment",
            "Rainfall and temperature analysis",
            "Agricultural weather indicators",
            "Climate-based crop planning"
        ],
        "status": "Live API connection available through the existing FarmShift AI NASA POWER endpoint.",
        "integration": "live"
    },

    "modis-landsat": {
        "title": "NASA MODIS & Landsat",
        "category": "Satellite Earth Observation",
        "agency": "NASA / USGS",
        "description": "MODIS and Landsat provide Earth observation imagery for monitoring land surfaces, vegetation and environmental changes.",
        "observations": [
            "MODIS surface reflectance",
            "Land surface observation",
            "Vegetation condition",
            "Land cover patterns",
            "Landsat multispectral imagery",
            "Surface change observations"
        ],
        "applications": [
            "Land observation",
            "Vegetation monitoring",
            "Surface change assessment",
            "Agricultural landscape analysis"
        ],
        "status": "Resource information displayed. Direct imagery and analysis integration is pending.",
        "integration": "pending"
    },

    "nasa-smap": {
        "title": "NASA SMAP",
        "category": "Water Intelligence",
        "agency": "NASA Jet Propulsion Laboratory",
        "description": "Soil Moisture Active Passive (SMAP) observes global surface soil moisture and freeze-thaw conditions.",
        "observations": [
            "Surface soil moisture",
            "Root-zone soil moisture products",
            "Freeze-thaw state",
            "Soil moisture variation",
            "Global soil moisture observations"
        ],
        "applications": [
            "Agricultural water awareness",
            "Soil moisture monitoring",
            "Drought assessment support",
            "Irrigation planning support"
        ],
        "status": "Resource information displayed. SMAP data API integration is pending.",
        "integration": "pending"
    },

    "sentinel-2": {
        "title": "Copernicus Sentinel-2",
        "category": "Crop & Vegetation Monitoring",
        "agency": "European Space Agency (ESA)",
        "description": "Sentinel-2 provides multispectral optical imagery useful for vegetation, crop and land monitoring.",
        "observations": [
            "Blue, green and red bands",
            "Near-infrared band",
            "Shortwave infrared bands",
            "Vegetation reflectance",
            "Multispectral surface imagery"
        ],
        "applications": [
            "Crop monitoring",
            "Vegetation index analysis",
            "Agricultural field observation",
            "Land cover assessment"
        ],
        "status": "Resource information displayed. Sentinel-2 imagery integration is pending.",
        "integration": "pending"
    },

    "soilgrids-gaez": {
        "title": "SoilGrids & FAO GAEZ",
        "category": "Soil & Crop Suitability",
        "agency": "ISRIC / FAO",
        "description": "SoilGrids provides global soil property information. FAO GAEZ provides agro-ecological suitability and land productivity information.",
        "observations": [
            "Soil pH",
            "Soil organic carbon",
            "Soil texture",
            "Soil property information",
            "Agro-ecological suitability",
            "Crop suitability information"
        ],
        "applications": [
            "Soil condition assessment",
            "Crop suitability research",
            "Agro-ecological analysis",
            "Land productivity assessment"
        ],
        "status": "Resource information displayed. Actual soil and GAEZ spatial dataset processing is pending.",
        "integration": "pending"
    },

    "nasa-gedi": {
        "title": "NASA GEDI",
        "category": "Forest Intelligence",
        "agency": "NASA",
        "description": "Global Ecosystem Dynamics Investigation (GEDI) uses spaceborne lidar observations to study forest structure and vegetation.",
        "observations": [
            "Canopy height",
            "Forest vertical structure",
            "Above-ground biomass",
            "Vegetation structure",
            "Forest ecosystem observations"
        ],
        "applications": [
            "Forest structure monitoring",
            "Canopy assessment",
            "Biomass research",
            "Forest ecosystem analysis"
        ],
        "status": "Resource information displayed. GEDI data processing integration is pending.",
        "integration": "pending"
    }
}


@app.route("/data-source/<source_id>")
def data_source_detail(source_id):

    source = DATA_SOURCES.get(source_id)

    if source is None:
        return "Data source not found", 404

    return render_template(
        "data_source_detail.html",
        source=source
    )


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


# ==========================================
# FARM SHIFT AI - NASA CROP CLIMATE API
# Data Source: NASA POWER
# ==========================================

@app.route("/api/crop-climate", methods=["GET"])
def crop_climate_api():

    try:
        lat = float(request.args.get("lat", 11.0168))
        lon = float(request.args.get("lon", 76.9558))

        if not (-90 <= lat <= 90):
            return jsonify({
                "status": "error",
                "message": "Invalid latitude"
            }), 400

        if not (-180 <= lon <= 180):
            return jsonify({
                "status": "error",
                "message": "Invalid longitude"
            }), 400

        end_date = datetime.utcnow() - timedelta(days=5)
        start_date = end_date - timedelta(days=29)

        params = {
            "parameters": "T2M,PRECTOTCORR,RH2M",
            "community": "AG",
            "longitude": lon,
            "latitude": lat,
            "start": start_date.strftime("%Y%m%d"),
            "end": end_date.strftime("%Y%m%d"),
            "format": "JSON"
        }

        api_url = (
            "https://power.larc.nasa.gov/api/temporal/"
            "daily/point"
        )

        response = requests.get(
            api_url,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        nasa_data = response.json()

        climate = nasa_data.get(
            "properties", {}
        ).get("parameter", {})

        def clean_values(parameter):
            return [
                float(value)
                for value in parameter.values()
                if isinstance(value, (int, float))
                and value > -900
            ]

        temperatures = clean_values(
            climate.get("T2M", {})
        )

        rainfall = clean_values(
            climate.get("PRECTOTCORR", {})
        )

        humidity = clean_values(
            climate.get("RH2M", {})
        )

        if not temperatures or not rainfall or not humidity:
            return jsonify({
                "status": "error",
                "message": "NASA climate data unavailable"
            }), 502

        return jsonify({
            "status": "success",
            "source": "NASA POWER",
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            },
            "climate": {
                "average_temperature_c": round(
                    sum(temperatures) / len(temperatures), 2
                ),
                "total_rainfall_mm": round(
                    sum(rainfall), 2
                ),
                "average_humidity_percent": round(
                    sum(humidity) / len(humidity), 2
                )
            }
        })

    except requests.RequestException:
        app.logger.exception("NASA POWER API request failed")
        return jsonify({
            "status": "error",
            "message": "NASA POWER service unavailable"
        }), 502

    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": "Invalid input"
        }), 400

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
    return redirect("/#sources")




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
