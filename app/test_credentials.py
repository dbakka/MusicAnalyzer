# Quick test script to verify credentials
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

load_dotenv()

def test_spotify_credentials():
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
        )
        spotify = Spotify(client_credentials_manager=client_credentials_manager)
        
        # Test API call
        results = spotify.search(q='test', limit=1)
        print("Credentials working correctly!")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_spotify_credentials()