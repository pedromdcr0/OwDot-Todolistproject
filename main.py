from flask import Flask, render_template, redirect, request, session, jsonify
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import os
import re
from datetime import datetime, date

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
    length = len(password) >= 8

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
    completed = db.Column(db.Integer, default=False, nullable=False)
    due_time = db.Column(db.Date, nullable=False)
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


def return_id(username):
    user = User.query.filter_by(username=username).first()
    user_id = user.id
    return user_id


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


@app.route("/tasklist/<username>", methods=["GET"])
@login_required
def tasklist(username):
    user_id = return_id(username)
    tasks = Task.query.filter_by(user_id=user_id).all()
    return render_template("tasklist.html", username=username, tasks=tasks)


@app.route("/create_task/<username>", methods=["POST"])
def create_task(username):
    task_description = request.form.get("task_description")
    task_date = datetime.strptime(request.form.get("duetime"), "%Y-%m-%d").date()

    user_id = return_id(username)

    existing_task = Task.query.filter_by(description=task_description, due_time=task_date, user_id=user_id).first()
    if existing_task:
        return redirect(f"/tasklist/{username}")

    new_task = Task(description=task_description, completed=0, due_time=task_date, user_id=user_id)
    db.session.add(new_task)
    db.session.commit()

    return redirect(f"/tasklist/{username}")


@app.route("/update_status", methods=["POST"])
@login_required
def update_status():
    data = request.get_json()
    task_id = data.get("task_id")
    new_status = data.get("status")

    # Busca a tarefa pelo ID
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    # Atualiza o status no banco de dados
    task.completed = new_status
    db.session.commit()

    return jsonify({"message": "Status atualizado com sucesso!"})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
