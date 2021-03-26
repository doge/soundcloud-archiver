import time
import requests
from bs4 import BeautifulSoup
from config import Config
from discord_webhook import DiscordWebhook, DiscordEmbed
from SoundcloudDownloader import SoundcloudDownloader
from database import Database

SOUNDCLOUD_URL = "https://soundcloud.com"
SOUNDCLOUD_LIKES_URL = "https://soundcloud.com/" + Config.username + "/likes"
TIMEOUT_SECONDS = 5 * 60  # 5 minutes

database = Database(Config.database)


def get_recent_likes():
    recent_likes = []

    with requests.Session() as sess:
        response = sess.get(SOUNDCLOUD_LIKES_URL)
        soup = BeautifulSoup(response.text, 'html.parser')

        like_container = soup.find_all('article')
        for like in like_container:
            if like.h2.a is not None:
                recent_likes.append(SOUNDCLOUD_URL + like.h2.a['href'])

    return recent_likes


def send_embed(song_data):
    webhook = DiscordWebhook(Config.webhook_url)

    try:
        embed = DiscordEmbed(title=song_data['title'], description=song_data['description'], color="c0c4c4")
    except:
        embed = DiscordEmbed(title=song_data['title'], description=None, color="c0c4c4")

    embed.add_embed_field(name="Artist", value=song_data['user']['username'], inline=False)
    embed.add_embed_field(name="URL", value=str(song_data['permalink_url']), inline=False)

    embed.add_embed_field(name="Duration (ms)", value=song_data['duration'], inline=True)
    embed.add_embed_field(name="Upload Date", value=song_data['display_date'], inline=True)
   
    embed.set_image(url=song_data['artwork_url'].replace('-large', '-t500x500'))
    webhook.add_embed(embed)

    response = webhook.execute()
    return response


def main():
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

        print("[*] refreshing in %s seconds...\n" % TIMEOUT_SECONDS)

        time.sleep(TIMEOUT_SECONDS)


if __name__ == "__main__":
    main()
