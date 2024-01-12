from flask import Flask, render_template, redirect, request, session
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'models', 'site.db')
db = SQLAlchemy(app)
app.secret_key = "super-secret-key"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return redirect("/")

    if not existing_user:
        new_user = User(username=username, password_hash=generate_password_hash(password, method='sha256'))
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
    app.run(debug=True)
