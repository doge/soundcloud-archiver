from pymongo import MongoClient
from config import Config
import datetime
from bson.objectid import ObjectId

class Database:
    def __init__(self, credentials):
        if Config.production:
            self.client = MongoClient('mongodb://%s:%s@%s:%s' % (credentials['user'], credentials['password'],
                                                                 credentials['ip'], credentials['port']))
        else:
            self.client = MongoClient(credentials['ip'], credentials['port'])

        self.db = self.client[credentials['db_name']]
        self.collection = self.db[credentials['collection']]

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
        data = self.collection.find_one({
            "_id": ObjectId(object_id)
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
            'archive-date': current_date
        })

    def insert_set(self, song_data):
        date = datetime.datetime.now()
        current_date = date.strftime("%Y-%m-%d %H:%M")

        try:
            # if the publisher_metadata object exists inside of the song data
            # then it's more accurate than using the song uploaders username
            artist_name = song_data['publisher_metadata']['artist']
        except:
            artist_name = song_data['username']

        return self.collection.insert_one({
            'artist': artist_name,
            'title': song_data['title'],
            'description': song_data['description'],
            'url': song_data['permalink_url'],
            'artwork-url': song_data['artwork_url'],
            'upload-date': song_data['display_date'],
            'artist-url': song_data['user']['permalink_url'],
            'archive-date': current_date
        })