import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY ='\xd6\xa9]\xe2/\x82\x1e6\xa4J_\x89f\xde\x9a\xc9\x1c\xdd\x97}|\x04\x85\x01'
	SQLALCHEMY_COMMINT_ON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	FLASK_MAIL_SUBJECT_PREFIX = '[Hcode]'
	FLASK_MAIL_SENDER = 'Hcode Admin <348013444@qq.com>'

	@staticmethod
	def init_app(app):
		pass


class DevelopmentConfig(Config):	
	DEBUG = True
	MAIL_SERVER = 'smtp.qq.com'
	MAIL_PORT = 25
	MAIL_USE_TLS = True
	MAIL_USERNAME = '348013444'
	MAIL_PASSWORD = 'dspojtiezgmicaaj'
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
	TESTING = True

config = {
	'development': DevelopmentConfig,
	'production': ProductionConfig,
	'tesing': TestingConfig,

	'default': DevelopmentConfig
}

