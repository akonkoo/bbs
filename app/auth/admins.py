from flask.ext.admin.contrib.sqla import ModelView
from flask import redirect, url_for
import flask_login as login
from .. import admin, db
from ..models import Category



admin.add_view(ModelView(Category, db.session))

 