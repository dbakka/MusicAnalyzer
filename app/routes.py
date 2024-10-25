from flask import Blueprint, render_template, jsonify, request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        spotify_url = data.get("spotify_url")
        
        if not spotify_url:
            return jsonify({"error": "No Spotify URL provided"}), 400

        # Add your analysis logic here
        return jsonify({
            "success": True,
            "results": {}
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
