from flask import Flask, request, jsonify, render_template
import os
import requests
import librosa
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from dotenv import load_dotenv
import json
from datetime import datetime
import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.parse import urlparse, parse_qs
import tempfile

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedMusicAnalyzer:
    def __init__(self):
        # Initialize API keys
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        self.spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not all([self.perplexity_api_key, self.spotify_client_id, self.spotify_client_secret]):
            raise ValueError("Missing required API keys in .env file")
        
        # Initialize Spotify client
        self.spotify = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=self.spotify_client_id,
                client_secret=self.spotify_client_secret
            )
        )
        
        self.audio_model = self._build_audio_model()
        self.success_predictor = RandomForestClassifier()
        self.scaler = StandardScaler()
        logger.info("EnhancedMusicAnalyzer initialized successfully")

    def extract_spotify_id(self, spotify_url):
        """Extract Spotify ID from various types of Spotify URLs"""
        try:
            parsed = urlparse(spotify_url)
            
            # Handle different Spotify URL formats
            if 'open.spotify.com' in parsed.netloc:
                path_parts = parsed.path.split('/')
                if len(path_parts) >= 3:
                    return path_parts[-1].split('?')[0]
            elif 'spotify:' in spotify_url:
                return spotify_url.split(':')[-1]
                
            raise ValueError("Invalid Spotify URL format")
        except Exception as e:
            logger.error(f"Error extracting Spotify ID: {str(e)}")
            raise

    def get_spotify_track_data(self, spotify_url):
        """Get track data from Spotify"""
        try:
            track_id = self.extract_spotify_id(spotify_url)
            track_data = self.spotify.track(track_id)
            audio_features = self.spotify.audio_features(track_id)[0]
            
            # Download preview URL for audio analysis
            preview_url = track_data.get('preview_url')
            if not preview_url:
                raise ValueError("No preview available for this track")
                
            return {
                'track_name': track_data['name'],
                'artist_name': track_data['artists'][0]['name'],
                'preview_url': preview_url,
                'popularity': track_data['popularity'],
                'audio_features': audio_features
            }
        except Exception as e:
            logger.error(f"Error getting Spotify track data: {str(e)}")
            raise

    def download_preview(self, preview_url):
        """Download preview file to temporary location"""
        try:
            response = requests.get(preview_url)
            response.raise_for_status()
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.write(response.content)
            temp_file.close()
            
            return temp_file.name
        except Exception as e:
            logger.error(f"Error downloading preview: {str(e)}")
            raise

    def analyze_from_spotify(self, spotify_url):
        """Analyze track from Spotify URL"""
        try:
            # Get Spotify data
            spotify_data = self.get_spotify_track_data(spotify_url)
            
            # Download preview
            temp_audio_path = self.download_preview(spotify_data['preview_url'])
            
            try:
                # Analyze audio
                audio_features, mel_spec = self.analyze_audio(temp_audio_path)
                
                # Get artist data
                artist_data = self.scrape_artist_data(spotify_data['artist_name'])
                
                # Combine with Spotify-provided features
                enhanced_features = {
                    **audio_features,
                    **spotify_data['audio_features']
                }
                
                # Generate prediction
                prediction = self.predict_success(enhanced_features, artist_data)
                
                return {
                    'track_data': spotify_data,
                    'audio_analysis': enhanced_features,
                    'artist_metrics': artist_data,
                    'prediction': prediction
                }
            finally:
                # Clean up temporary file
                os.unlink(temp_audio_path)
                
        except Exception as e:
            logger.error(f"Error analyzing from Spotify: {str(e)}")
            raise

    # ... (rest of the existing MusicInvestmentAnalyzer methods remain the same)

# Initialize analyzer
analyzer = EnhancedMusicAnalyzer()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        spotify_url = data.get('spotify_url')
        
        if not spotify_url:
            return jsonify({'error': 'No Spotify URL provided'}), 400
            
        # Analyze track
        results = analyzer.analyze_from_spotify(spotify_url)
        
        # Save report
        report_path = analyzer._save_report(results)
        
        return jsonify({
            'success': True,
            'results': results,
            'report_path': report_path
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)