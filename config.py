import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Cross site request forgery protection
    WTF_CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mysupersecretkey'

    # SQL Alchemy configuration
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True

    # Mail configuration
    MAIL_SUBJECT_PREFIX = '[WhereIam] '
    MAIL_SENDER = 'WhereIam Admin <whereiam@domain.tld>'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # App configuration
    WHEREIAM_ADMIN = os.environ.get('WHEREIAM_ADMIN')

    @staticmethod
    def init_app(app):
            pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
            'sqlite:///' + os.path.join(basedir, 'whereami-dev.db')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
            'sqlite:///' + os.path.join(basedir, 'whereami-test.db')
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
            'sqlite:///' + os.path.join(basedir, 'whereami.db')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # Email errors to administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                    secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.MAIL_SENDER,
            toaddrs=[cls.WHEREIAM_ADMIN],
            subject=cls.MAIL_SUBJECT_PREFIX + 'Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.Error)
        app.logger.addHandler(mail_handler)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

