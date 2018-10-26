from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:bloggy@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y33tifretjhggd'

class Blog(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(120))
	body = db.Column(db.String(200))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __init__(self, title, body, owner):
		self.title = title
		self.body = body  
		self.owner = owner

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True) 
	username = db.Column(db.String(120)) 
	password = db.Column(db.String(120))
	posts = db.relationship('Blog', backref='owner')

	def __init__(self, username, password):
		self.username = username
		self.password = password

@app.before_request
def require_login():
	allowed_routes = ['login', 'signup', 'posts']
	if request.endpoint not in allowed_routes and 'username' not in session:
		flash("Login!")
	else:
		redirect('/')

@app.route('/', methods=['GET', 'POST'])
def index():# for title 
	blog_db = Blog.query.all()
	users = User.query.all()
	return render_template('home.html', blog_db = blog_db, users = users)



@app.route('/posts', methods=["GET"])
def display():
	individual = request.args.get('id')
	individual_user = request.args.get('user')
	users = User.query.all()
	if individual:
		post_db = Blog.query.filter_by(id = individual)
		return render_template('posts.html', post_db = post_db, users = users)
	elif individual_user:
		post_db = Blog.query.filter_by(user_id = individual_user)
		return render_template('posts.html', post_db = post_db, users = users)
	else:
		post_db = Blog.query.all()
		return render_template('posts.html', post_db = post_db, users = users)

@app.route('/newpost', methods=['GET', 'POST'])
def submit(): 
	username = request.args.get('session')
	if username:
		owner = User.query.filter_by(username=session['username']).first()
		if request.method == 'POST':
			text_input = request.form['text']
			title_input = request.form['title']
			# Blog stuff
			title = Post(title_input,text_input,owner)
			db.session.add(title)
			db.session.commit()
			return redirect('/blog')
		else:
			return render_template('submit-page.html')
	else:
		return redirect('/login')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		verify = request.form['verify']
		existing_user = User.query.filter_by(username=username).first()
		if not existing_user:
			username = request.form['username']
			password = request.form['password']
			verify = request.form['verify']
			new_user = User(username, password)
			db.session.add(new_user)
			db.session.commit()
			session['username'] = username
			return redirect('/')
		else:
			flash("Duplicate User", 'error')
			return render_template('signup.html')
	else:
		return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		user = User.query.filter_by(username=username).first()
		if user and user.password == password:
			session['username'] = username
			flash("Logged in!")
			return redirect('/')
		else:
			flash('User password incorrect, or user does not exist', 'error')
			return render_template('login.html')
	else:
		return render_template('login.html')

@app.route('/logout')
def logout():
	username = request.args.get('session')
	if username:
		del session['username']
		return redirect('/')
	else:
		return redirect('/login')

if __name__ == '__main__':
	app.run()