from os import environ, path, curdir
from dotenv import dotenv_values, load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class DeveloperConfig():

    SECRET_KEY= environ.get('SECRET_KEY')
    FLASK_DEBUG = environ.get('FLASK_ENV')
    PWD = path.abspath(curdir)
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://neondb_owner:npg_kS5Obash2Lnf@ep-tiny-morning-advu7ex4-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 3
    MAIL_SERVER= 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'aikumby.vocacional@gmail.com'
    MAIL_PASSWORD = environ.get('EMAIL_HOST_PASSWORD')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
