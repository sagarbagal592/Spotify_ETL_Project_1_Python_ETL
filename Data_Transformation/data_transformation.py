import json
import boto3
from datetime import datetime
from io import StringIO
import pandas as pd

def album(data):
    album_list = []
    for i in data['items']:
        album_id = i['item']['album']['id']
        album_name = i['item']['album']['name']
        release_date = i['item']['album']['release_date']
        album_url = i['item']['external_urls']['spotify']
        
        album_element = {'album_id': album_id,
                        'album_name': album_name,
                        'release_date': release_date,
                        'album_url': album_url}
        album_list.append(album_element)

    return album_list

def artists(data):
    artist_list = []
    for i in data['items']:
        for row in i['item']['artists']:
            artist_dict = {'artist_id': row['id'], 'artist_name': row['name'], 'external_uri': row['href']}
            artist_list.append(artist_dict)

    return artist_list

def songs(data):
    songs_list = []
    for row in data['items']:
        song_id = row['item']['id']
        song_name = row['item']['name']
        song_duration = row['item']['duration_ms']
        song_url = row['item']['uri']
        songs_dict = {'song_id': song_id, 'song_name': song_name, 'song_duration': song_duration, 'song_url': song_url}
        songs_list.append(songs_dict)

    return songs_list

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    Bucket = "spotify-etl-project-1-738497419462-us-east-1-an"
    Key = "raw_data/to_processed/"

    spotify_data =[]
    spotify_keys = []

    for file in s3.list_objects(Bucket= Bucket, Prefix= Key)['Contents']:
        file_key = file['Key']
        if file_key.split('.')[-1] == "json":
            response = s3.get_object(Bucket=Bucket, Key=file_key)
            content = response['Body']
            jsonobject = json.loads(content.read())
            spotify_data.append(jsonobject)
            spotify_keys.append(file_key)

    for data in spotify_data:
        album_list = album(data)
        artist_list = artists(data)
        songs_list = songs(data)

        album_df = pd.DataFrame.from_dict(album_list)
        album_df = album_df.drop_duplicates(subset=['album_id'])
        album_df['release_date'] = pd.to_datetime(album_df['release_date'])

        artist_df = pd.DataFrame.from_dict(artist_list)
        artist_df = artist_df.drop_duplicates(subset=['artist_id'])

        song_df = pd.DataFrame.from_dict(songs_list)


        album_key = "transformed_data/album_data/album_transformed_" + str(datetime.now()) + ".csv"

        album_buffer = StringIO()
        album_df.to_csv(album_buffer, index=False)
        album_content = album_buffer.getvalue()
        s3.put_object(Bucket=Bucket, Key=album_key, Body=album_content)


        artists_key = "transformed_data/artists_data/artists_transformed_" + str(datetime.now()) + ".csv"

        artists_buffer = StringIO()
        artist_df.to_csv(artists_buffer, index = False)
        artists_content = artists_buffer.getvalue()
        s3.put_object(Bucket=Bucket, Key=artists_key, Body=artists_content)



        song_key = "transformed_data/songs_data/song_transformed_" + str(datetime.now()) + ".csv"

        song_buffer = StringIO()
        song_df.to_csv(song_buffer, index = False)
        song_content = song_buffer.getvalue()
        s3.put_object(Bucket=Bucket, Key=song_key, Body=song_content)
    
    s3_resource = boto3.resource('s3')
    for key in spotify_keys:
        copy_source = {
            'Bucket': Bucket,
            'Key': key
        }
        s3_resource.meta.client.copy(copy_source, Bucket, "raw_data/processed/" + key.split("/")[-1])
        s3_resource.Object(Bucket, key).delete()


