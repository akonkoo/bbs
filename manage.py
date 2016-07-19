#coding: utf-8
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')

import os
from app import create_app, db
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def deploy():
	from flask.ext.migrate import upgrade

	upgrade()


if __name__ == '__main__':
	manager.run()