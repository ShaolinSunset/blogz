from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

@app.route('/')
def index():
    return render_template('blog.html')

@app.route('/newpost')
def display():
    return render_template('newpost.html')

@app.route('/newpost', methods=['POST', 'GET'])
def validate():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

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
            new_blog = Blog(title, body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blogpost/' + str(new_blog.id))

@app.route('/blog')
def homepage():
    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs)

@app.route('/blogpost/<int:blog_id>')
def blog(blog_id):
    blogId = blog_id
    
    blogpost = Blog.query.filter(Blog.id == blogId).first()
    return render_template('blogpost.html', blogpost=blogpost)


if __name__ == '__main__':
    app.run()