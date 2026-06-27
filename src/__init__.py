import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from src.config import Config
from src.database import db

# Carica esplicitamente le variabili dal file .env all'avvio del modulo
load_dotenv()

csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inizializzazione estensioni
    db.init_app(app)
    csrf.init_app(app)

    # Registrazione dei Blueprints
    from src.auth.routes import auth_bp
    from src.budget.routes import budget_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(budget_bp, url_prefix='')

    # Creazione tabelle all'avvio
    with app.app_context():
        from src.models.models import User
        try:
            db.session.execute(db.select(User)).first()
        except Exception:
            db.create_all()
            print("Database initialized through production factory.")

    return app