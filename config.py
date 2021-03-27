class Config:
    database = {
        'ip': 'localhost',
        'port': 27017,
        'user': 'root',
        'password': '',
        'db_name': 'music-archive',
        'collection': 'songs'
    }
    production = False

    username = "<your soundcloud username>"
    timeout_seconds = 5 * 60  # 5 minutes
    webhook_url = "<your discord webhook url>"