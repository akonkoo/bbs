from flask.ext.admin.contrib.sqla import ModelView
# from flask import redirect, url_for
# import flask_login as login
# from flask_admin import helpers, expose, AdminIndexView
from .forms import * 
from .. import admin, db
from ..models import Category, User

class UserView(ModelView):
	column_list = ['email', 'username', 'location']
	can_delete = False
	can_create = False
	can_edit = False
			
admin.add_view(UserView(User, db.session))
admin.add_view(ModelView(Category, db.session))


 