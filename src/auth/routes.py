from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from . import auth_bp
from src.database import db
from src.models.models import User

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Se l'utente è già loggato, lo mandiamo direttamente alla dashboard
    if session.get("user_id"):
        return redirect(url_for('budget.index'))

    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                return redirect(url_for('budget.index'))

            flash('Invalid credentials')
        except Exception as e:
            flash(f'An error occurred during login submission: {e}')
            return redirect(url_for('auth.login')) # Qui il redirect è sicuro perché gestisce solo il fallimento del POST

    # Se siamo in GET, renderizziamo normalmente senza try/except distruttivi
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get("user_id"):
        return redirect(url_for('budget.index'))

    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            confirmation = request.form['confirmation']
            salary = float(request.form['salary'])

            if password != confirmation:
                flash('Passwords do not match')
                return redirect(url_for('auth.register'))

            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists')
                return redirect(url_for('auth.register'))

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=hashed_password, salary=salary)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'An error occurred during registration: {e}')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    try:
        session.pop('user_id', None)
    except Exception as e:
        flash(f'An error occurred during logout: {e}')
    return redirect(url_for('auth.login'))