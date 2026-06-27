from datetime import datetime
from flask import redirect, render_template, session, url_for
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def apology(message, code=400):
    def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"), ("%", "~p"), ("#", "~h"), ("/", "~s"), ('"', "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def format_date(date_obj):
    return date_obj.strftime("%B %d, %Y")

def calculate_total_expenses(expenses):
    return sum(exp.amount for exp in expenses)