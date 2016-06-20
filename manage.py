#coding: utf-8

import os
from app import create_app, db
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def deploy():
	from flask.ext.migrate import upgrade
	from app.models import Category

	upgrade()

	c1 = Category(name='初学入门')
	c2 = Category(name='编程语言')
	c3 = Category(name='招聘求职')
	c4 = Category(name='建议反馈')
	db.session.add_all([c1, c2, c3, c4])
	db.session.commit()

if __name__ == '__main__':
	manager.run()