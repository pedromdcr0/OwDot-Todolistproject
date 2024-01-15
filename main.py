from flask import Flask, render_template, redirect, request, session
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import os
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'models', 'users.db')
db = SQLAlchemy(app)
app.secret_key = "super-secret-key"


def verify_complexity(password):
    regex_lower = re.compile(r'[a-z]')

    regex_upper = re.compile(r'[A-Z]')

    regex_number = re.compile(r'\d')

    regex_symbol = re.compile(r'[!@#$%^&*(),.?":{}|<>]')

    lower = regex_upper.search(password) is not None
    upper = regex_lower.search(password) is not None
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
        email = request.form['email']
        print(password)

        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user is not None or not verify_complexity(password) or existing_email is not None:
            return redirect("/register")

        if verify_complexity(password) and not existing_user and not existing_email:
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

    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        return redirect(f'/tasklist/{username}')
    else:
        return redirect("/")


@app.route("/tasklist/<username>")
@login_required
def tasklist(username):
    return username


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
