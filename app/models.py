import hashlib
import bleach
from datetime import datetime
from . import db, login_manager
from werkzeug import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request 
from markdown import markdown

class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(64), unique=True, index=True)
	username =db.Column(db.String(64), unique=True, index=True)
	password_hash = db.Column(db.String(128))
	confirmed = db.Column(db.Boolean, default=False)
	name = db.Column(db.String(64))
	location = db.Column(db.String(64))
	about_me = db.Column(db.Text())
	member_since = db.Column(db.DateTime(), default=datetime.utcnow)
	last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
	avatar_hash = db.Column(db.String(32))

	articles = db.relationship('Article', backref='author', lazy='dynamic')
	comments = db.relationship('Comment', backref='author', lazy='dynamic')

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.email is not None and self.avatar_hash is None:
			self.avatar_hash = hashlib.md5(
				self.email.encode('utf-8')).hexdigest()

	def generate_confirmation_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'confirm': self.id})

	def confirm(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('confirm') != self.id:
			return False
		self.confirmed = True
		db.session.add(self)
		db.session.commit()
		return True

	def generate_reset_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'reset': self.id})

	def reset_password(self, token, new_password):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('reset') != self.id:
			return False
		self.password = new_password
		db.session.add(self)
		db.session.commit()
		return True

	def ping(self):
		self.last_seen = datetime.utcnow()
		db.session.add(self)
		db.session.commit()

	def gravatar(self, size=100, default='identicon', rating='g'):
		url = 'http://cn.gravatar.com/avatar'
		hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
			url=url, hash=hash, size=size, default=default, rating=rating)

	@property 
	def password(self):
		raise AttributeError('password is not a readable attribute.')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)


	def __repr__(self):
		return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class Article(db.Model):
	__tablename__ = 'articles'
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(120))
	body = db.Column(db.Text())
	body_html = db.Column(db.Text())
	pub_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	look_views = db.Column(db.Integer, default=0)

	category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	comments = db.relationship('Comment', backref='article', lazy='dynamic')
	tags = db.relationship('Tag',
							secondary='article_tag_ref',
							backref=db.backref('articles', lazy='dynamic'),
							lazy='dynamic')

	def add_looks(self):
		self.look_views += 1
		db.session.add(self)
		db.session.commit()

	@staticmethod
	def on_change_body(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
						'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
						'h1', 'h2', 'h3', 'p']
		target.body_html = bleach.linkify(bleach.clean(
			markdown(value, output_format='html'),
			tags = allowed_tags, strip=True))
		 					
db.event.listen(Article.body, 'set', Article.on_change_body)

class Category(db.Model):
	__tablename__ = 'categories'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), unique=True)

	articles = db.relationship('Article', backref='category', lazy='dynamic')

	def __repr__(self):
		return self.name


class Tag(db.Model):
	__tablename__ = 'tags'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(10))

	def __repr__(self):
		return self.name


article_tag_ref = db.Table('article_tag_ref',
	db.Column('article_id', db.Integer, db.ForeignKey('articles.id'), nullable=True),
	db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), nullable=True)
)


class Comment(db.Model):
	__tablename__ = 'comments'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	pub_date = db.Column(db.DateTime, index=True, default=datetime.utcnow())

	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))

	@staticmethod
	def on_change_body(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
						'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
						'h1', 'h2', 'h3', 'p']
		target.body_html = bleach.linkify(bleach.clean(
			markdown(value, output_format='html'),
			tags = allowed_tags, strip=True))

db.event.listen(Comment.body, 'set', Comment.on_change_body)



from . import admin
from flask.ext.admin.contrib.sqla import ModelView

admin.add_view(ModelView(Category, db.session))
