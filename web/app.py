from flask import Flask, redirect, render_template, request, send_file
from utils.database import Database
from config import Config
import os
from utils.SoundcloudDownloader import remove_forbidden_chars

database = Database(Config.database)
SONGS_DIR = os.path.normpath(os.getcwd() + os.sep + os.pardir) + "/songs/"

def register_blueprints(app):
    pass


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '1234567890123456'
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    register_blueprints(app)

    @app.route('/')
    def index():
        return redirect('/panel')

    @app.route('/panel')
    def panel():
        return render_template('panel.html', songs=database.find())

    @app.route('/info')
    def info():
        song_id = request.args.get('id')
        if song_id:
            song = database.find_song(song_id)
            return render_template('info.html', song=song)

    @app.route('/download')
    def download():
        song_id = request.args.get('id')
        song_data = database.find_song(song_id)
        if song_id:
            path = SONGS_DIR + remove_forbidden_chars(song_data['title']) + ".mp3"
            return send_file(path)

    return app


if __name__ == '__main__':
    create_app().run()
    print(database.find())