from flask import Flask, render_template, redirect, request, session
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import os
import re
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'models', 'users.db')
db = SQLAlchemy(app)
app.secret_key = "super-secret-key"

task_tags = db.Table('task_tags', db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True), db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True))


def verify_complexity(password):
    regex_lower = re.compile(r'[a-z]')

    regex_upper = re.compile(r'[A-Z]')

    regex_number = re.compile(r'\d')

    regex_symbol = re.compile(r'[!@#$%^&*(),.?":{}|<>]')

    upper = regex_upper.search(password) is not None
    lower = regex_lower.search(password) is not None
    number = regex_number.search(password) is not None
    symbol = regex_symbol.search(password) is not None
    length = len(password) > 8

    return (
        lower and
        upper and
        number and
        symbol and
        length
    )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.String(255), default=False, nullable=False)
    due_time = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tags = db.relationship('Tag', secondary=task_tags, lazy='subquery', backref=db.backref('tasks', lazy=True))


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conf_password = request.form['conf_password']
        email = request.form['email']
        print(password)

        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user is not None or not verify_complexity(password) or existing_email is not None:
            return redirect("/register")

        if verify_complexity(password) and not existing_user and not existing_email and conf_password == password:
            new_user = User(username=username, email=email, password_hash=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            return redirect("/")

    return render_template("register.html")


@app.route('/')
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if user is not None and check_password_hash(user.password_hash, password):
        print(user.id)
        session['user_id'] = user.id
        session['user'] = user.username
        print("passou")
        return redirect(f"/tasklist/{user.username}")
    else:
        print('nao passou')
        return redirect("/")


@app.route("/tasklist/<username>")
@login_required
def tasklist(username):
    return render_template("tasklist.html", username=username)


@app.route("/create_task/<username>", methods=["GET", "POST"])
def create_task(username):
    # description = request.form.get('description')
    # tags = request.form.get('tags')  # Assuming that tags are provided as a comma-separated string
    # tag_list = [Tag(name=tag.strip()) for tag in tags.split(',') if tag.strip()]
    #
    # new_task = Task(description=description, user=current_user, tags=tag_list)
    # db.session.add(new_task)
    # db.session.commit()
    return render_template('create_task.html', username=username)


@app.route("/add_task", methods=["POST"])
def add_task():
    return "sasdfg"


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
