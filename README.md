# Budget Manager

**Demo**: [Deploy on Render](https://budgetmanager-x6i7.onrender.com/)

## Description
Budget Manager is a modern web application designed to help users manage their personal finances by tracking expenses, setting savings goals, and monitoring spending patterns.

The project was recently reengineered following industry-standard production practices in Python, converting the initial monolithic architecture into a modular structure based on the **Application Factory Pattern** and **Flask Blueprints**, with data isolation and configuration driven by environment variables (`.env`).

## Key Features
- **Authentication and Session Management**: Secure registration, login, and logout (with passwords protected via PBKDF2 hashing).
- **Expense Tracking**: Entry and dynamic categorization of expenses.
- **Savings Goals**: Real-time monitoring of the savings target calculated based on the user’s entered salary.
- **Profile Management**: Updating personal information (salary, target percentage) and secure password change.
- **History and Reset**: Chronological view of expenses and the option to completely reset the history.
- **Advanced Security**: Native protection against CSRF (Cross-Site Request Forgery) attacks implemented globally.

---

## Project Architecture

The application follows a highly scalable and decoupled package structure (*Package Structure*).

```text
```text
budget_manager/
│
├── src/
│   ├── __init__.py          # Application Factory (create_app), extension initialization
│   ├── config.py            # Config class and environment variable validation
│   ├── database.py          # Centralized SQLAlchemy instance (db)
│   │
│   ├── auth/                # Authentication Blueprint (Identity Isolation)
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── budget/              # Finance Core Blueprint (Dashboard, Profile, Expenses)
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── services.py      # Business Logic (decorators, calculations, formatting)
│   │
│   ├── models/              # Data Models (SQLAlchemy-independent ORM)
│   │   ├── __init__.py
│   │   └── models.py
│   │
│   ├── templates/           # HTML layouts and views organized by context
│   │   ├── auth/            # Login and registration templates
│   │   ├── budget/          # Dashboard, history, expenses, and profile
│   │   └── layout.html      # Base template inherited with Dark Mode support
│   │
│   └── static/              # Static assets served natively
│       ├── favicon.ico
│       ├── I_heart_validator.png
│       └── css/
│           └── styles.css
│
├── .env                     # Local environment variables (NOT tracked in Git)
├── Dockerfile               # Multi-stage configuration optimized for production
├── requirements.txt         # Dependencies with locked versions and python-dotenv
└── run.py                   # Entry Point
```
## Design Choices and Technology Stack
- Flask (v3.0+): Chosen as a micro-framework for its flexibility; extended using Blueprint to separate business responsibilities.
- SQLAlchemy (v2.0+): Used as an ORM paired with Flask-SQLAlchemy to interface with the database using the native and secure `db.select` syntax.
- SQLite / PostgreSQL: Lightweight local relational database (SQLite), easily swappable in production by modifying the connection string in the environment.
- Bootstrap 5: Ensures a responsive, modern, and elegant interface with native Dark Mode support built into the stylesheets.
- Python-Dotenv: Secure lifecycle management of sensitive data outside the source code.

## Local Installation and Configuration
1. Clone the repository

   ```Bash
   git clone <your-repository-url>
   cd budget_manager
   ```

2. Create and activate a virtual environment

   ```Bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies

   ```Bash
   pip install -r requirements.txt
   ```

4. Configure the environment
   Copy the sample file and fill in the required fields:

   ```Bash
   cp .env.example .env
   ```
Open the newly generated .env file and fill in the SECRET_KEY string (you can generate a secure one using the command `python -c “import secrets; print(secrets.token_hex(32))”`).

5. Start the application
   ```Bash
   python run.py
   ```
   The application will be accessible at http://localhost:5000. The database tables will be created automatically on first launch within the isolated environment.

## Containerization with Docker
The project includes a Dockerfile optimized for multi-stage builds to minimize the size of the final image and enhance security.

To build and run the container locally by passing the configuration file:

```Bash
# Build the image
docker build -t budget_manager .
```
```Bash
docker volume create budget_db_data
```
```Bash
# Run the container on port 8000 with the .env file loaded
docker run -p 8000:8000 --env-file .env -v budget_db_data:/app/instance budget_manager
```
### Docker Compose
Docker Compose automatically configures persistent volumes to prevent database data loss and loads environment variables.

Make sure you have a .env file configured in the project root directory.

Start the application in the background:
```Bash
docker compose up -d
```
The application will be accessible at http://localhost:8000.

To stop the services:
```Bash
docker compose down
```
## Deployment to Production
The application is ready for modern cloud platforms (Render, Koyeb, Railway, AWS).

Configure the startup command to point to the WSGI server: gunicorn run:app.

>Important: Configure the environment variables on your provider’s dashboard by setting `FLASK_ENV=production` and providing values for `SECRET_KEY` and `DATABASE_URL` (e.g., by connecting to a remote PostgreSQL instance). The code will validate security and block execution if any keys are missing.