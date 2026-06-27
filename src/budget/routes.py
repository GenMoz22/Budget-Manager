from flask import render_template, request, redirect, url_for, flash, session
from datetime import date
from collections import defaultdict
from werkzeug.security import generate_password_hash, check_password_hash
from . import budget_bp
from src.database import db
from src.models.models import User, Expense, History
from src.budget.services import login_required, apology, format_date, calculate_total_expenses

@budget_bp.route('/')
@login_required
def index():
    try:
        user = User.query.get(session['user_id'])
        if user is None:
            session.clear()
            return redirect(url_for('auth.login'))

        expenses = Expense.query.filter(Expense.user_id == user.id, Expense.category != 'Savings').all()
        total_expenses = calculate_total_expenses(expenses)

        monthly_salary = user.salary / 12

        savings = monthly_salary - total_expenses

        savings_goal_amount = round(monthly_salary * user.savings_goal, 2)

        savings_goal_reached = savings >= savings_goal_amount
        # ----------------------------------

        current_date = format_date(date.today())

        expenses_by_category = defaultdict(float)
        for expense in expenses:
            expenses_by_category[expense.category] += expense.amount

        return render_template('budget/index.html', user=user, expenses_by_category=expenses_by_category,
                               total_expenses=total_expenses, savings=savings, savings_goal_amount=savings_goal_amount,
                               savings_goal_reached=savings_goal_reached, current_date=current_date, monthly_salary=monthly_salary)
    except Exception as e:
        flash(f'An error occurred while loading the index page: {e}')
        return redirect(url_for('auth.login'))

@budget_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    try:
        user = User.query.get(session['user_id'])
        if request.method == 'POST':
            if request.form.get("change_password"):
                old_password = request.form['old_password']
                new_password = request.form['password']
                confirmation = request.form['confirmation']

                if not old_password or not new_password or not confirmation:
                    return apology("missing fields", 400)
                if new_password != confirmation:
                    return apology("new passwords do not match", 400)
                if not check_password_hash(user.password, old_password):
                    return apology("invalid old password", 400)

                user.password = generate_password_hash(new_password)
            else:
                user.salary = float(request.form['salary'])
                user.savings_goal = float(request.form['savings_goal']) / 100

            db.session.commit()
            flash('Profile updated successfully')
        return render_template('budget/profile.html', user=user)
    except Exception as e:
        flash(f'An error occurred while updating profile: {e}')
        return redirect(url_for('budget.profile'))

@budget_bp.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    try:
        if request.method == 'POST':
            category = request.form['category']
            amount = float(request.form['amount'])
            new_expense = Expense(user_id=session['user_id'], category=category, amount=amount)
            db.session.add(new_expense)
            db.session.commit()
            return redirect(url_for('budget.index'))
        return render_template('budget/add_expense.html')
    except Exception as e:
        flash(f'An error occurred while adding expense: {e}')
        return redirect(url_for('budget.index'))

@budget_bp.route('/history')
@login_required
def history():
    try:
        user = User.query.get(session['user_id'])
        expenses = Expense.query.filter_by(user_id=user.id).all()
        formatted_expenses = [{
            "category": exp.category,
            "amount": exp.amount,
            "timestamp": exp.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        } for exp in expenses]
        return render_template("budget/history.html", expenses=formatted_expenses)
    except Exception as e:
        flash(f'An error occurred while fetching history: {e}')
        return redirect(url_for('budget.index'))

@budget_bp.route('/reset_expenses', methods=['POST'])
@login_required
def reset_expenses():
    try:
        user = User.query.get(session['user_id'])
        Expense.query.filter_by(user_id=user.id).delete()
        History.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        flash('All expenses and history have been reset successfully')
        return redirect(url_for('budget.profile'))
    except Exception as e:
        flash(f'An error occurred while resetting expenses and history: {e}')
        return redirect(url_for('budget.profile'))