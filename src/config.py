import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        if os.environ.get('FLASK_ENV') == 'production':
            raise ValueError("CRITICAL: SECRET_KEY environment variable is missing in production!")
        SECRET_KEY = 'dev_fallback_insecure_key'

    # Gestione dinamica dell'URI del Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///../instance/budget.db')

    # Ottimizzazione SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False