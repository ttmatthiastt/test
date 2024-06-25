from flask import Flask, request, jsonify, Response, render_template, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import logging
import traceback

load_dotenv()


logging.basicConfig(level=logging.INFO)


client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spotify.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Artist(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=True)
    followers = db.Column(db.Integer, nullable=True)
    popularity = db.Column(db.Integer, nullable=True)
    image_url = db.Column(db.String(200), nullable=True)


class Track(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    artist_id = db.Column(db.String(50), db.ForeignKey('artist.id'), nullable=False)
    preview_url = db.Column(db.String(200), nullable=True)
    album = db.Column(db.String(100), nullable=True)

def get_token() -> str:
    """
    Function to get Spotify API token.
    Returns:
        str: Access token.
    """
    auth_string = f"{client_id}:{client_secret}"
    auth_base64 = base64.b64encode(auth_string.encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    return result.json()["access_token"]

def get_auth_header(token: str) -> dict:
    """
    Helper function to get the authorization header.
    Args:
        token (str): Access token.
    Returns:
        dict: Authorization header.
    """
    return {"Authorization": f"Bearer {token}"}

def get_song_info(song_name: str, token: str) -> str:
    """
    Function to get song ID by song name.
    Args:
        song_name (str): Name of the song.
        token (str): Access token.
    Returns:
        str: Song ID.
    """
    url = f"https://api.spotify.com/v1/search?q={song_name}&type=track"
    result = get(url, headers=get_auth_header(token)).json()
    tracks = result.get("tracks", {}).get("items", [])
    return tracks[0].get("id") if tracks else None

def get_artist_genres(artist_id: str, token: str) -> list:
    """
    Function to get genres of an artist by artist ID.
    Args:
        artist_id (str): ID of the artist.
        token (str): Access token.
    Returns:
        list: List of genres.
    """
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    result = get(url, headers=get_auth_header(token)).json()
    return result.get("genres", [])

def get_recommendations(song_name: str, popularity: int) -> list:
    """
    Function to get song recommendations based on song name and popularity.
    Args:
        song_name (str): Name of the song.
        popularity (int): Popularity threshold.
    Returns:
        list: List of recommended tracks.
    """
    logging.info("Fetching recommendations with parameters: song_name=%s, popularity=%d", song_name, popularity)
    token = get_token()
    song_id = get_song_info(song_name, token)
    if not song_id:
        logging.warning("Song not found: %s", song_name)
        return []

    url = "https://api.spotify.com/v1/recommendations"
    headers = get_auth_header(token)
    params = {
        "seed_tracks": song_id,
        "limit": 4
    }

    try:
        response = get(url, headers=headers, params=params)
        if response.status_code != 200:
            logging.error("Failed to fetch recommendations: %s", response.text)
            return []

        recommendations = response.json().get("tracks", [])
        if not recommendations:
            logging.info("No recommendations found")
            return []

        return sorted(
            [{
                "name": track["name"],
                "genre": ", ".join(get_artist_genres(track["artists"][0]["id"], token)),
                "popularity": track["popularity"],
                "image_url": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
                "external_url": track["external_urls"]["spotify"],
                "artist_name": track["artists"][0]["name"]
            } for track in recommendations],
            key=lambda x: x['popularity'], reverse=True)[:3]
    except Exception as e:
        logging.error("Error fetching recommendations: %s", str(e))
        return []

@app.route('/recommendations', methods=['GET'])
def recommendations():
    """
    Endpoint to get recommendations based on song name and popularity.
    Returns:
        Response: JSON response with recommendations.
    """
    song_name = request.args.get('song_name')
    popularity = request.args.get('popularity')

    if not song_name:
        return jsonify({"error": "Please provide a song name"}), 400

    try:
        recommendations = get_recommendations(song_name, int(popularity))
        if not recommendations:
            return jsonify({"message": "No recommendations found"}), 404
        print(recommendations)
        return jsonify(recommendations)
    except ValueError:
        return jsonify({"error": "Popularity must be an integer"}), 400
    except Exception as e:
        logging.error("Error fetching recommendations: %s", traceback.format_exc())  
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
