# Budget Manager

Demo: https://mature-yolanda-genmoz22-209d36c1.koyeb.app/

#### Description:
Budget Manager is a web application designed to help users manage their personal finances by tracking expenses, setting savings goals, and visualizing spending patterns. The application is built using Flask, a lightweight web framework for Python, and utilizes SQLite for data storage. The user interface is designed with Bootstrap for a responsive and modern look.

## Features
- **User Registration and Authentication**: Users can create an account, log in, and log out securely.
- **Expense Tracking**: Users can add, view, and delete expenses. Expenses are categorized for better organization.
- **Savings Goal**: Users can set a savings goal and track their progress towards achieving it.
- **Profile Management**: Users can update their profile information, including salary and savings goal, and change their password.
- **Expense History**: Users can view a history of their expenses.
- **Expense Reset**: Users can reset all their expenses and history.

## Files
- **app.py**: The main application file that contains the Flask routes and logic for handling user requests.
- **helpers.py**: A helper file that contains utility functions.
- **templates/**: A directory containing HTML templates for rendering the web pages.
  - **layout.html**: The base layout template that includes the common structure for all pages.
  - **index.html**: The home page template that displays the user's expenses and savings information.
  - **login.html**: The login page template.
  - **register.html**: The registration page template.
  - **profile.html**: The profile page template where users can update their profile and change their password.
  - **history.html**: The history page template that displays the user's expense history.
  - **add_expense.html**: The page template for adding new expenses.
- **static/**: A directory containing static files such as CSS and JavaScript.
  - **styles.css**: The main stylesheet for the application.
- **README.md**: This file, which provides an overview of the project, its features, and the structure of the codebase.
- **.python-version, Procfile, requirements.txt**: for Koyeb hosting

## Design Choices
- **Flask**: Chosen for its simplicity and flexibility, making it easy to build and scale the application.
- **SQLite**: Used as the database for its lightweight nature and ease of setup, suitable for a small-scale application.
- **Bootstrap**: Utilized for the front-end design to ensure a responsive and modern user interface.
