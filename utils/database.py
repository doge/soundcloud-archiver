from pymongo import MongoClient
from config import Config
import datetime
from bson.objectid import ObjectId
import re

def remove_forbidden_chars(string):
    return re.sub(r'[\\/*?:"<>|]', "", string)

class Database:
    def __init__(self, credentials, collection):
        if Config.production:
            self.client = MongoClient('mongodb://%s:%s@%s:%s' % (credentials['user'], credentials['password'],
                                                                 credentials['ip'], credentials['port']))
        else:
            self.client = MongoClient(credentials['ip'], credentials['port'])

        self.db = self.client[credentials['db_name']]
        self.collection = self.db[collection]

    def delete(self, query):
        return self.collection.delete_one(query)

    def update(self, query, new_values):
        return self.collection.update_one(query, new_values)

    def find_one(self, query):
        return self.collection.find_one(query)

    def find(self, query=None):
        to_return = []

        found = self.collection.find(query)
        for item in found:
            to_return.append(item)

        return to_return

    def insert(self, query):
        self.collection.insert_one(query)

    def find_song(self, object_id):
        try:
            data = self.collection.find_one({
                "songs._id": ObjectId(object_id)
            })
            for song in data['songs']:
                if str(song['_id']) == object_id:
                    return song
        except:
            data = self.collection.find_one({
                '_id': ObjectId(object_id)
            })

        try:
            data['_id'] = str(data['_id'])
        except:
            pass



        return data

    def insert_song(self, song_data):
        date = datetime.datetime.now()
        current_date = date.strftime("%Y-%m-%d %H:%M")

        try:
            # if the publisher_metadata object exists inside of the song data
            # then it's more accurate than using the song uploaders username
            artist_name = song_data['publisher_metadata']['artist']
        except:
            artist_name = song_data['user']['username']

        try:
            # some songs don't have artwork so we will just use their soundcloud
            # profile picture just how the website does
            artwork_url = song_data['artwork_url'].replace('-large', '-t500x500')
        except:
            artwork_url = song_data['user']['avatar_url'].replace('-large', '-t500x500')

        return self.collection.insert_one({
            'artist': artist_name,
            'title': song_data['title'],
            'description': song_data['description'],
            'metadata': song_data['publisher_metadata'],
            'url': song_data['permalink_url'],
            'artwork-url': artwork_url,
            'duration': song_data['duration'],
            'upload-date': song_data['display_date'],
            'artist-url': song_data['user']['permalink_url'],
            'type': 'song',
            'archive-date': current_date,
            'path': '/songs/' + remove_forbidden_chars(song_data['title']) + ".mp3"
        })

    def insert_set(self, song_data):
        date = datetime.datetime.now()
        current_date = date.strftime("%Y-%m-%d %H:%M")

        try:
            # if the publisher_metadata object exists inside of the song data
            # then it's more accurate than using the song uploaders username
            artist_name = song_data[1]['publisher_metadata']['artist']
        except:
            artist_name = song_data[1]['user']['username']

        formatted_songs = []
        for song in song_data[0]:
            try:
                artist_name_song = song['publisher_metadata']['artist']
            except:
                artist_name_song = song['user']['username']

            try:
                artwork_url = song['artwork_url'].replace('-large', '-t500x500')
            except:
                artwork_url = song['user']['avatar_url'].replace('-large', '-t500x500')

            formatted_songs.append({
                '_id': ObjectId(),
                'artist': artist_name_song,
                'title': song['title'],
                'description': song['description'],
                'metadata': song['publisher_metadata'],
                'url': song['permalink_url'],
                'artwork-url': artwork_url,
                'duration': song['duration'],
                'upload-date': song['display_date'],
                'artist-url': song['user']['permalink_url'],
                'archive-date': current_date,
                'type': 'song',
                'path': '/songs/' + remove_forbidden_chars(song_data[1]['title']) + "/" + remove_forbidden_chars(song['title']) + ".mp3"
            })

        return self.collection.insert_one({
            'artist': artist_name,
            'title': song_data[1]['title'],
            'description': song_data[1]['description'],
            'url': song_data[1]['permalink_url'],
            'artwork-url': song_data[1]['artwork_url'].replace('-large', '-t500x500'),
            'upload-date': song_data[1]['display_date'],
            'artist-url': song_data[1]['user']['permalink_url'],
            'archive-date': current_date,
            'type': 'set',
            'songs': formatted_songs
        })