import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///annuaire.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False