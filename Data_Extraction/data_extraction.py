import json
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import boto3
from datetime import datetime

def lambda_handler(event, context):
    client_id = os.environ.get('client_id')
    client_secret = os.environ.get('client_secret')
    refresh_token = os.environ.get('refresh_token')
    print("Credentials loaded")

    sp_oauth = SpotifyOAuth(
        client_id=client_id, 
        client_secret=client_secret, 
        redirect_uri="http://127.0.0.1:8889/callback", 
        scope="playlist-read-private")
        
    print("OAuth object created")

    token_info = sp_oauth.refresh_access_token(refresh_token)

    print("Access token obtained")

    access_token = token_info["access_token"]

    sp = spotipy.Spotify(auth=access_token)


    
    playlist_link = "https://open.spotify.com/playlist/7sWMgw9GUr9YlI0ZO9ULF8?si=a0137887348d4561"

    playlist_URI = playlist_link.split("/")[-1].split("?")[0]

    data = sp.playlist_items(playlist_URI)

    client = boto3.client('s3')

    filename = "spotify_raw_" + str(datetime.now()) + ".json"

    client.put_object(
        Bucket='spotify-etl-project-1-738497419462-us-east-1-an',
        Key='raw_data/to_processed/' + filename,
        Body=json.dumps(data)
    )

    return{
        'statuscode': 200,
        'body': json.dumps({
            'message': 'Data extracted successfully',
            'total_tracks': data['total']
        })
    }
