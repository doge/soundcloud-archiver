from flask import Flask, redirect, render_template, request, send_file, jsonify, url_for, flash
from interfaces import Interfaces
import os
import zipfile
from datetime import datetime
from utils.SoundcloudDownloader import remove_forbidden_chars
from bson.objectid import InvalidId
from auth.middleware import login_required
from auth.controllers import auth
from bson.objectid import ObjectId
from json import dumps

SONGS_DIR = os.path.normpath(os.getcwd() + os.sep + os.pardir) + "/songs/"


def register_blueprints(app):
    app.register_blueprint(auth)


def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '1234567890123456'
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    register_blueprints(app)

    @app.route('/')
    def index():
        return redirect('/panel')

    @app.route('/panel')
    @login_required
    def panel():
        if not Interfaces.user_database.find():
            return redirect(url_for('auth.register'))

        # filter out the songs from the sets
        songs_not_sets = []
        songs = Interfaces.song_database.find()
        for song in songs:
            if 'set' not in song['url']:
                songs_not_sets.append(song)

        # sort them by most recent archived date first
        songs_not_sets = sorted(songs_not_sets, key=lambda s: s['archive-date'], reverse=True)

        return render_template('panel.html', songs=songs_not_sets, recent_songs=songs_not_sets[:4])

    @app.route('/info')
    @login_required
    def info():
        if 'id' in request.args:
            try:
                song = Interfaces.song_database.find_song(request.args.get('id'))
            except InvalidId:
                return jsonify({'error': 'invalid id'})

            minutes, seconds = divmod(song['duration'] / 1000, 60)

            return render_template('info.html', song=song, minutes=round(minutes), seconds=round(seconds))
        return jsonify({'error': 'no id supplied'})

    @app.route('/download')
    @login_required
    def download():
        song_id = request.args.get('id')
        if 'id' in request.args:
            try:
                song_data = Interfaces.song_database.find_song(song_id)
            except InvalidId:
                return jsonify({'error': 'invalid id'})

            path = SONGS_DIR + remove_forbidden_chars(song_data['title']) + ".mp3"
            return send_file(path, as_attachment=True)
        return jsonify({'error': 'no id supplied'})

    @app.route('/delete')
    @login_required
    def delete():
        song_id = request.args.get('id')
        song_data = Interfaces.song_database.find_song(song_id)
        if 'id' in request.args:
            try:
                # remove from db
                Interfaces.song_database.delete({'_id': ObjectId(song_id)})

                # remove from disk
                path = SONGS_DIR + remove_forbidden_chars(song_data['title']) + ".mp3"
                os.remove(path)

                flash('%s has been deleted.' % song_data['title'])
            except:
                flash('%s could not be deleted.' % song_data['title'])
            return redirect(url_for('panel'))

        return jsonify({'error': 'no id supplied'})

    @app.route('/archive')
    @login_required
    def archive():
        zipf = zipfile.ZipFile('archive.zip', 'w', zipfile.ZIP_DEFLATED)
        zipdir(SONGS_DIR, zipf)
        zipf.close()
        return send_file('archive.zip', as_attachment=True)

    return app


if __name__ == '__main__':
    create_app().run()