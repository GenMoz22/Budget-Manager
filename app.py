import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from collections import defaultdict
from helpers import apology, login_required, format_date, calculate_total_expenses, calculate_average_expense
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
# Set a strong secret key for production environments.
# it should be a randomly generated string stored as an environment variable.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key_development_only')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
csrf = CSRFProtect(app) #CSRFProtect

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    savings_goal = db.Column(db.Float, default=0.2)

# Define the Expense model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

    user = db.relationship('User', backref=db.backref('expenses', lazy=True))

# Define the History model
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

    user = db.relationship('User', backref=db.backref('history', lazy=True))

# Create database tables if they don't exist
# This block runs when the app module is loaded by Gunicorn or directly executed.
# It ensures the database schema is created on startup in environments like Koyeb.
with app.app_context():
    # Check if the 'user' table exists. If not, create all tables.
    if not db.engine.has_table('user'):
        db.create_all()
        print("Database tables created.")
    else:
        print("Database tables already exist. Skipping creation.")


@app.route('/')
@login_required
def index():
    """Render the home page with user's expenses and savings information."""
    try:
        user = User.query.get(session['user_id'])
        expenses = Expense.query.filter(Expense.user_id == user.id, Expense.category != 'Savings').all()
        total_expenses = calculate_total_expenses(expenses)
        savings = user.salary - total_expenses
        savings_goal_amount = user.salary * user.savings_goal
        savings_goal_reached = savings >= savings_goal_amount
        current_date = format_date(date.today())

        expenses_by_category = defaultdict(float)
        for expense in expenses:
            expenses_by_category[expense.category] += expense.amount

        return render_template('index.html', user=user, expenses_by_category=expenses_by_category, total_expenses=total_expenses, savings=savings, savings_goal_amount=savings_goal_amount, savings_goal_reached=savings_goal_reached, current_date=current_date)
    except Exception as e:
        flash(f'An error occurred while loading the index page: {e}')
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log in the user."""
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                return redirect(url_for('index'))
            flash('Invalid credentials')
        return render_template('login.html')
    except Exception as e:
        flash(f'An error occurred during login: {e}')
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            confirmation = request.form['confirmation']
            salary = float(request.form['salary'])

            # Check if passwords match
            if password != confirmation:
                flash('Passwords do not match')
                return redirect(url_for('register'))

            # Check if username already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists')
                return redirect(url_for('register'))

            # Create a new user
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=hashed_password, salary=salary)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('register.html')
    except Exception as e:
        flash(f'An error occurred during registration: {e}')
        return redirect(url_for('register'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Update user's profile and change password."""
    try:
        user = User.query.get(session['user_id'])
        if request.method == 'POST':
            if request.form.get("change_password"):
                old_password = request.form['old_password']
                new_password = request.form['password']
                confirmation = request.form['confirmation']

                # Ensure old password was submitted
                if not old_password:
                    return apology("must provide old password", 400)

                # Ensure new password was submitted
                elif not new_password:
                    return apology("must provide new password", 400)

                # Ensure confirmation was submitted
                elif not confirmation:
                    return apology("must provide confirmation", 400)

                # Ensure new passwords match
                elif new_password != confirmation:
                    return apology("new passwords do not match", 400)

                # Ensure old password is correct
                if not check_password_hash(user.password, old_password):
                    return apology("invalid old password", 400)

                # Hash the new password
                user.password = generate_password_hash(new_password)

            else:
                user.salary = float(request.form['salary'])
                user.savings_goal = float(request.form['savings_goal']) / 100

            db.session.commit()
            flash('Profile updated successfully')
        return render_template('profile.html', user=user)
    except Exception as e:
        flash(f'An error occurred while updating profile: {e}')
        return redirect(url_for('profile'))

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    """Add a new expense."""
    try:
        if request.method == 'POST':
            category = request.form['category']
            amount = float(request.form['amount'])
            new_expense = Expense(user_id=session['user_id'], category=category, amount=amount)
            db.session.add(new_expense)
            db.session.commit()
            return redirect(url_for('index'))
        return render_template('add_expense.html')
    except Exception as e:
        flash(f'An error occurred while adding expense: {e}')
        return redirect(url_for('index'))

@app.route('/history')
@login_required
def history():
    """Show history of expenses."""
    try:
        user = User.query.get(session['user_id'])
        # Retrieve expenses for the current user
        expenses = Expense.query.filter_by(user_id=user.id).all()

        # Format expenses (optional)
        formatted_expenses = []
        for expense in expenses:
            #Formatting
            formatted_expense = {
                "category": expense.category,
                "amount": expense.amount,
                "timestamp": expense.timestamp.strftime("%Y-%m-%d %H:%M:%S"),  # Format timestamp
            }
            formatted_expenses.append(formatted_expense)

        return render_template("history.html", expenses=formatted_expenses)
    except Exception as e:
        flash(f'An error occurred while fetching history: {e}')
        return redirect(url_for('index'))

@app.route('/reset_expenses', methods=['POST'])
@login_required
def reset_expenses():
    """Reset all expenses and history for the current user."""
    try:
        user = User.query.get(session['user_id'])
        # Delete all expenses for the user
        Expense.query.filter_by(user_id=user.id).delete()
        # Delete all history for the user
        History.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        flash('All expenses and history have been reset successfully')
        return redirect(url_for('profile'))
    except Exception as e:
        flash(f'An error occurred while resetting expenses and history: {e}')
        return redirect(url_for('profile'))

@app.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    try:
        session.pop('user_id', None)
        return redirect(url_for('login'))
    except Exception as e:
        flash(f'An error occurred during logout: {e}')
        return redirect(url_for('index'))

def archive_expenses():
    """Archive expenses at the end of the month."""
    try:
        users = User.query.all()
        for user in users:
            expenses = Expense.query.filter_by(user_id=user.id).all()
            for expense in expenses:
                history_entry = History(user_id=user.id, category=expense.category, amount=expense.amount, timestamp=expense.timestamp)
                db.session.add(history_entry)
                db.session.delete(expense)
            db.session.commit()
    except Exception as e:
        flash(f'An error occurred while archiving expenses: {e}')

if __name__ == '__main__':
    # This block ensures app.run() is only called when app.py is executed directly.
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
