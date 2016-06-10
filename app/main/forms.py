#coding: utf-8

from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length, Required, Optional
from flask.ext.pagedown.fields import PageDownField

from ..models import Category

class EditProfileForm(Form):
	name = StringField('Real name', validators=[Length(0,64)])
	location = StringField('Location', validators=[Length(0,64)])
	about_me = TextAreaField('About me')
	submit = SubmitField("Submit")

def categories():
	return Category.query.all()

class ArticleForm(Form):
	title = StringField('Title', validators=[Required(), Length(0, 140)])
	category = QuerySelectField('Category', 
		query_factory=categories)
	tags = StringField('Tags', validators=[Length(0, 10), Optional()],
		description="select one or more tags, separated by spaces")
	body = PageDownField('body', validators=[Required()])
	submit = SubmitField('Post')


class CommentForm(Form):
	body = TextAreaField('', validators=[Required()])
	submit = SubmitField('Replay')

	