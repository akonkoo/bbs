import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY ='\xd6\xa9]\xe2/\x82\x1e6\xa4J_\x89f\xde\x9a\xc9\x1c\xdd\x97}|\x04\x85\x01'
	SQLALCHEMY_COMMINT_ON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	FLASK_MAIL_SUBJECT_PREFIX = '[Hcode]'
	FLASK_MAIL_SENDER = 'Hcode Admin <348013444@qq.com>'
	FLASK_ADMIN = '348013444@qq.com'
	SSL_DISBALE = True

	@staticmethod
	def init_app(app):
		pass


class DevelopmentConfig(Config):	
	DEBUG = True
	MAIL_SERVER = 'smtp.qq.com'
	MAIL_PORT = 25
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class ProductionConfig(Config):
	DEBUG = True
	MAIL_SERVER = 'smtp.qq.com'
	MAIL_PORT = 25
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

	@classmethod
	def init_app(cls, app):
		Config.init_app(app)

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
				fromaddr=cls.FLASK_MAIL_SENDER,
				toaddrs=[cls.FLASK_ADMIN],
				subject=cls.FLASK_MAIL_SUBJECT_PREFIX + 'Application Error',
				credentials=credentials,
				secure=secure)
			mail_handler.setLevel(logging.ERROR)
			app.logger.addHandler(mail_handler)


class TestingConfig(Config):
	TESTING = True


class HerokuConfig(ProductionConfig):
	SSL_DISBALE = bool(os.environ.get('SSL_DISBALE'))
	@classmethod
	def init_app(cls, app):
		ProductionConfig.init_app()

		import logging
		from logging import StreamHandler
		file_handler = StreamHandler()
		file_handler.setLevel(logging.WARNING)
		app.logger.addHandler(file_handler)

		from werkzeug.contrib.fixers import ProxyFix
		app.wsgi_app = ProxyFix(app.wsgi_app)
		

config = {
	'development': DevelopmentConfig,
	'production': ProductionConfig,
	'tesing': TestingConfig,

	'default': DevelopmentConfig
}

