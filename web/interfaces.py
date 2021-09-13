from config import Config
from utils.database import Database

class Interfaces:
    song_database = Database(Config.database, "songs")
    user_database = Database(Config.database, "users")
