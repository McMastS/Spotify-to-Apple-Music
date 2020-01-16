import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID') or 'secret'
    SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET') or 'secret'
    APPLE_TEAM_ID = os.environ.get('APPLE_TEAM_ID') or 'secret'
    APPLE_SECRET_KEY = os.environ.get('APPLE_SECRET_KEY') or 'secret'
    APPLE_KEY_ID = os.environ.get('APPLE_KEY_ID') or 'secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False