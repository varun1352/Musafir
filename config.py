import os

basedir = os.path.abspath(os.path.dirname(__file__))

# SQLite configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'musafir.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
