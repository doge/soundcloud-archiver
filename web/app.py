from flask import Flask, redirect, render_template, request, send_file, jsonify, url_for, flash
from interfaces import Interfaces
import os
import zipfile
import shutil
from bson.objectid import InvalidId
from auth.middleware import login_required
from auth.controllers import auth
from bson.objectid import ObjectId
import json

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
            try:
                for song in song['songs']:
                    songs_not_sets.append(song)
            except:
                songs_not_sets.append(song)

        # sort them by most recent archived date first
        songs_not_sets = sorted(songs, key=lambda s: s['archive-date'], reverse=True)

        return render_template('panel.html', songs=songs_not_sets, recent_songs=songs_not_sets[:4])

    @app.route('/info')
    @login_required
    def info():
        if 'id' in request.args:
            try:
                song = Interfaces.song_database.find_song(request.args.get('id'))
            except InvalidId:
                return jsonify({'error': 'invalid id'})

            try:
                minutes, seconds = divmod(song['duration'] / 1000, 60)
            except:
                minutes = 0
                seconds = 0

            return render_template('info.html', song=song, minutes=round(minutes), seconds=round(seconds),
                                   enumerate=enumerate)
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

            if 'song' in song_data['type']:
                path = os.path.normpath(os.getcwd() + os.sep + os.pardir) + song_data['path']
                return send_file(path, as_attachment=True)
            elif 'set' in song_data['type']:
                zipf = zipfile.ZipFile(song_data['title'] + '.zip', 'w', zipfile.ZIP_DEFLATED)
                zipdir(os.path.normpath(os.getcwd() + os.sep + os.pardir) + '/songs/' + song_data['title'], zipf)
                zipf.close()
                return send_file(song_data['title'] + '.zip', as_attachment=True)

        return jsonify({'error': 'no id supplied'})

    @app.route('/delete')
    @login_required
    def delete():
        # working on fix for sets

        song_id = request.args.get('id')
        song_data = Interfaces.song_database.find_song(song_id)
        if 'id' in request.args:
            if song_data['type'] == 'song':
                # remove from db
                Interfaces.song_database.delete({'_id': ObjectId(song_id)})
                # remove from disk
                os.remove(os.path.normpath(os.getcwd() + os.sep + os.pardir) + song_data['path'])

            elif song_data['type'] == 'set':
                # remove from db
                Interfaces.song_database.delete({'_id': ObjectId(song_id)})
                # remove from disk
                shutil.rmtree(os.path.normpath(os.getcwd() + os.sep + os.pardir) + '/songs/' + song_data['title'],
                              ignore_errors=True)

            flash('%s has been deleted.' % song_data['title'])

            return redirect(url_for('panel'))
        return jsonify({'error': 'no id supplied'})

    @app.route('/archive')
    @login_required
    def archive():
        zipf = zipfile.ZipFile('archive.zip', 'w', zipfile.ZIP_DEFLATED)
        zipdir(SONGS_DIR, zipf)
        zipf.close()
        return send_file('archive.zip', as_attachment=True)

    @app.route('/database', methods=['GET', 'POST'])
    def db():
        if request.method == "POST":
            if 'text' in request.form:
                try:
                    Interfaces.song_database.update_document(request.form['text'])
                    flash("Successsfully saved database.")
                except:
                    flash("Couldn't save database.")
            else:
                flash("No document provided.")



        db_data = Interfaces.song_database.find()
        parsed_data = []
        for item in db_data:
            item['_id'] = str(item['_id'])
            if item['type'] == 'set':
                for song in item['songs']:
                    song['_id'] = str(song['_id'])
            parsed_data.append(item)
        dumped = json.dumps(parsed_data, indent=4)
        return render_template('db.html', db_data=dumped)

    return app


if __name__ == '__main__':
    create_app().run()