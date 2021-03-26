from pymongo import MongoClient
import datetime


class Database:
    def __init__(self, credentials):
        #self.client = MongoClient('mongodb://%s:%s@%s:%s' % (credentials['user'], credentials['password'],
        #                                                     credentials['ip'], credentials['port']))
        self.client = MongoClient(credentials['ip'], credentials['port'])
        self.db = self.client[credentials['db_name']]
        self.collection = self.db[credentials['collection']]

    def find_one(self, query):
        return self.collection.find_one(query)

    def find(self, query=None):
        return self.collection.find(query)

    def insert(self, query):
        self.collection.insert_one(query)

    def insert_song(self, song_data):
        date = datetime.datetime.now()
        current_date = date.strftime("%Y-%m-%d %H:%M")

        return self.collection.insert_one({
            'artist': song_data['user']['username'],
            'title': song_data['title'],
            'description': song_data['description'],
            'metadata': song_data['publisher_metadata'],
            'url': song_data['permalink_url'],
            'artwork-url': song_data['artwork_url'],
            'duration': song_data['duration'],
            'upload-date': song_data['display_date'],
            'artist-url': song_data['user']['permalink_url'],
            'archive_date': current_date
        })

    def insert_set(self, song_data):
        date = datetime.datetime.now()
        current_date = date.strftime("%Y-%m-%d %H:%M")

        return self.collection.insert_one({
            'artist': song_data['user']['username'],
            'title': song_data['title'],
            'description': song_data['description'],
            'url': song_data['permalink_url'],
            'artwork-url': song_data['artwork_url'],
            'upload-date': song_data['display_date'],
            'artist-url': song_data['user']['permalink_url'],
            'archive_date': current_date
        })