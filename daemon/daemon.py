import time
from config import Config
from utils.SoundcloudDownloader import SoundcloudDownloader
from utils.database import Database
from utils.utils import get_recent_likes, send_embed

database = Database(Config.database)


def start_daemon():
    print("[*] monitoring: soundcloud.com/%s\n" % Config.username)

    while True:
        new_likes = []
        likes = get_recent_likes()

        # check if we have any of the songs in the database
        for like in likes:
            item = database.find_one({'url': like})
            if item is None:
                new_likes.append(like)

        if len(new_likes) == 0:
            print("[*] no new likes found...")

        # download each new song
        for new_like in new_likes:
            downloader = SoundcloudDownloader(new_like)
            downloader.download()

            # send webhook and insert into db
            if downloader.url_type == "set":
                for item in downloader.data[0]:
                    send_embed(item)
                    database.insert_song(item)

                database.insert_set(downloader.data[1])
            else:
                send_embed(downloader.data[0])
                database.insert_song(downloader.data[0])

        print("[*] refreshing in %s seconds...\n" % Config.timeout_seconds)

        time.sleep(Config.timeout_seconds)
