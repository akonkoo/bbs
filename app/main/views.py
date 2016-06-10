from datetime import datetime
from flask import render_template, session, redirect, url_for, abort,flash
from flask.ext.login import login_required, current_user

from . import main
from .forms import *
from .. import db
from ..models import *

@main.route('/')
def index():
	page = request.args.get('page', 1, type=int)
	pagination = Article.query.order_by(Article.pub_date.desc()).paginate(
										page, per_page=15, error_out=False)
	articles = pagination.items
	return render_template('index.html', articles=articles, pagination=pagination)


@main.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		abort(404)
	return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user)
		db.session.commit()
		flash('Your profile has been updated.')
		return redirect(url_for('.user', username=current_user.username))
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', form=form)


@main.route('/post', methods=['GET', 'POST'])
@login_required
def post():
	form = ArticleForm()
	if form.validate_on_submit():
		article = Article(title = form.title.data,
					body = form.body.data,
					category = form.category.data,
					author = current_user._get_current_object())
		tags = form.tags.data 
		for i in tags.split(' '):
			tag = Tag(name=i)
			article.tags.append(tag)
		db.session.add(article)
		db.session.commit()
		flash('You have posted the article.')
		return redirect(url_for('.index'))
	return render_template('post.html', form=form)

@main.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def article_detail(id):
	form = CommentForm()
	article = Article.query.get_or_404(id)
	article.add_looks()

	if form.validate_on_submit():
		comment = Comment(body = form.body.data,
						article = article,
						author = current_user._get_current_object())
		db.session.add(comment)
		db.session.commit()
		flash('Your comment has been published.')
		return redirect(url_for('.article_detail', id=article.id, page=-1))
	page = request.args.get('page', 1, type=int)
	if page == -1:
		page = (article.comments.count() - 1) / 15 + 1
	pagination = article.comments.order_by(Comment.pub_date.asc()).paginate(
		page, per_page=15, error_out=False)
	comments = pagination.items 
	return render_template('article_detail.html', article=article, form=form,
							comments=comments, pagination=pagination)


@main.route('/delete/<int:id>')
@login_required
def article_delete(id):
	article = Article.query.get_or_404(id)
	if current_user == article.author:	
		db.session.delete(article)
		db.session.commit()
		flash('You have delete the article.')
		return redirect(url_for('.index'))
	else:
		flash('You cannot delete this article.')


@main.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def article_update(id):
	form = ArticleForm()
	article = Article.query.get_or_404(id)
	if form.validate_on_submit():
		article.title = form.title.data
		article.body = form.body.data
		article.category = form.category.data
		article.author = current_user._get_current_object()

		for i in article.tags:article.tags.remove(i)
		tags = form.tags.data 
		for i in tags.split(' '):
			tag = Tag(name=i)
			article.tags.append(tag)
		db.session.add(article)
		db.session.commit()
		flash('You have updated the article.')
		return redirect(url_for('.article_detail', id=article.id))
	form.title.data=article.title
	form.body.data=article.body
	form.category.data=article.category
	form.tags.data=" ".join(str(i) for i in article.tags)
	return render_template('post.html', form=form) 


@main.route('/category/<int:id>')
def category(id):
	#category = Category.query.get(id)
	page = request.args.get('page', 1, type=int)
	pagination = Article.query.filter_by(category_id=id).order_by(
		Article.pub_date.desc()).paginate(
			page, per_page=15, error_out=False)
	articles = pagination.items
	return render_template('index.html', articles=articles, pagination=pagination)


import sys  
reload(sys)  
sys.setdefaultencoding('utf8')




		




