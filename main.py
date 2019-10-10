from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog():
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User():
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup', 'users', 'singleUser']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash("Successfully logged in")
            return redirect('newpost')
        else:
            if not user:
                flash('Sorry, This Username Does Not Exist', 'error')

            elif password != user.password:
                flash('Password incorrect', 'error')
            return redirect('login')
    
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        password_error = ''
        verify_error = ''
        existing_user_error = ''   

        existing_user = User.query.filter_by(username=username).first() 

        if int(len(username)) <= 0:
            username_error = 'Thats not a valid username'
            username = ''
        else:
            if int(len(username)) < 3 or int(len(username)) > 20:
                username_error = 'Thats not a valid username'
                username = ''  

        if int(len(password)) <= 0:
            password_error = 'Thats not a valid password'
            password = ''
        else:
            if int(len(password)) < 3 or int(len(password)) > 20:
                password_error = 'Thats not a valid password'
                password = ''

        if int(len(verify)) <= 0:
            verify_error = 'Password do not match'
            verify = ''
        else:
            if password != verify:
                verify_error = 'Password do not match'
                verify = ''    

        if username_error or password_error or verify_error:
            return render_template('signup.html', username_error=username_error, 
            password_error=password_error, verify_error=verify_error,
            username=username, password=password, verify=verify)

        if not existing_user:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('newpost')
        else: 
            flash('A user with that username already exists', 'error')
            return redirect('signup')


    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('blog')

@app.route('/newpost')
def display():
    return render_template('newpost.html')

@app.route('/newpost', methods=['POST', 'GET'])
def validate():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()

        title_error = ''
        body_error = ''

        if int(len(title)) <= 0:
            title_error = 'Please fill in the title'
    
        if int(len(body)) <= 0:
            body_error = 'Please fill in the body'

        if title_error or body_error:
            return render_template('newpost.html', title_error=title_error, body_error=body_error,
            title=title, body=body)
        else:
            new_blog = Blog(title, body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blogpost/' + str(new_blog.id))

@app.route('/blog')
def index():
    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs)

@app.route('/')
def users():
    users = Blog.query.all()
    return render_template('index.html', users=users)

@app.route('/blogpost/<int:blog_id>')
def blog(blog_id):
    blogId = blog_id
    blogpost = Blog.query.filter(Blog.id == blogId).first()
    return render_template('blogpost.html', blogpost=blogpost)

@app.route('/singleUser/<int:User_id>')
def singleUser(User_id):
    username = User_id
    usernames = Blog.query.filter(Blog.owner_id == username).all()
    return render_template('singleUser.html', usernames=usernames)

if __name__ == '__main__':
    app.run()