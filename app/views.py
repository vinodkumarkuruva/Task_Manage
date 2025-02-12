from flask import Blueprint, render_template, redirect, url_for, flash ,jsonify
from flask_jwt_extended import create_access_token,create_refresh_token, set_access_cookies, set_refresh_cookies, unset_jwt_cookies, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.forms import RegistrationForm, LoginForm, TaskForm
from app.models import User, Task

app = Blueprint('app', __name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('app.login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            # Generate JWT tokens
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            # Set cookies for tokens
            response = redirect(url_for('app.dashboard'))
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)

            flash('Login successful!', 'success')
            return response
        flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/dashboard')
def dashboard():
    tasks = Task.query.all()
    return render_template('dashboard.html', tasks=tasks)

@app.route('/add_task', methods=['GET', 'POST'])
@jwt_required()  # Protect the route
def add_task():
    form = TaskForm()
    current_user_id = get_jwt_identity()  # Get the logged-in user ID from the token
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            status=form.status.data,
            user_id=current_user_id  # Associate the task with the current user
        )
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('app.dashboard'))
    return render_template('add_task.html', form=form)


@app.route('/logout', methods=['POST'])
def logout():
    response = jsonify({'msg': 'Logout successful'})
    unset_jwt_cookies(response)  # Clear access and refresh cookies
    return response



@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.status = form.status.data
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('app.dashboard'))
    return render_template('edit_task.html', form=form, task=task)


@app.route('/delete_task/<int:task_id>', methods=['GET', 'POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task Deleted successfully!', 'success')
    return redirect(url_for('app.dashboard'))


@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)  # Protect with refresh token
def refresh():
    current_user_id = get_jwt_identity()  # Get the user ID from the refresh token
    new_access_token = create_access_token(identity=current_user_id)
    response = jsonify({'msg': 'Token refreshed'})
    set_access_cookies(response, new_access_token)  # Set the new access token in cookies
    return response
