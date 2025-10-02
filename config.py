from os import environ, path, curdir
from dotenv import dotenv_values, load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class DeveloperConfig():

    SECRET_KEY= environ.get('SECRET_KEY')
    FLASK_DEBUG = environ.get('FLASK_ENV')
    PWD = path.abspath(curdir)
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}/dbase.db'.format(PWD)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 3
    MAIL_SERVER= 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'mapadetalentos@aikumby.com'
    MAIL_PASSWORD = environ.get('EMAIL_HOST_PASSWORD')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
