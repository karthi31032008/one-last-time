import os
import logging
from datetime import datetime, timezone

from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Security configuration
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "development-only-change-before-deployment"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


# ERROR HANDLERS
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Page not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    logger.exception("Internal server error")
    return jsonify({
        "error": "Internal server error"
    }), 500

@app.route("/crop-suitability")
def crop_suitability():
    return render_template("crop_suitability.html")


# START SERVER
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )

