from datetime import datetime
from app import db

class User(db.Model):
	__tablename__ = 'userList'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(80), unique=True)
	username = db.Column(db.String(50))
	pwHash = db.Column(db.String(120))

	def __init__(self, email, username,pwHash):
		self.email = email
		self.username = username
		self.pwHash = pwHash

	def __repr__(self):
		return '<User %r>' % self.username


class UserScript(db.Model):
	__tablename__ = 'userScript'
	id = db.Column(db.Integer, primary_key=True)
	user = db.Column(db.String(80))
	title = db.Column(db.String(100))
	script = db.Column(db.Text)
	pub_date = db.Column(db.DateTime)

	def __init__(self, user, title,script,pub_date=None):
		self.user = user
		self.title = title
		self.script = script
		if pub_date is None:
		    pub_date = datetime.utcnow()
		self.pub_date = pub_date

	def __repr__(self):
		return '<UserScript %r>' % self.email


class UserDoc(db.Model):
	__tablename__ = 'userDoc'
	id = db.Column(db.Integer, primary_key=True)
	user = db.Column(db.String(80))
	title = db.Column(db.String(100))
	doc = db.Column(db.Text)
	pub_date = db.Column(db.DateTime)

	def __init__(self, user, title,doc,pub_date=None):
		self.user = user
		self.title = title
		self.doc = doc
		if pub_date is None:
		    pub_date = datetime.utcnow()
		self.pub_date = pub_date

	def __repr__(self):
		return '<UserDoc %r>' % self.email




db.create_all()
