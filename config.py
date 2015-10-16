import os

class Config:
    basedir = os.path.abspath(os.path.dirname(__file__))
    # Cross site request forgery protection
    WTF_CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mysupersecretkey'

    # SQL Alchemy configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'whereami.db')
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # Mail configuration
    MAIL_SUBJECT_PREFIX = '[WhereIam] '
    MAIL_SENDER = 'WhereIam Admin <whereiam@mgebm.net>'

    # App configuration
    WHEREIAM_ADMIN = os.environ.get('WHEREIAM_ADMIN')

    @staticmethod
    def init_app(app):
            pass

class DevelopmentConfig(Config):
    DEBUG = True

config = {
    'development': DevelopmentConfig,
    'production': Config,
    'default': DevelopmentConfig
}

