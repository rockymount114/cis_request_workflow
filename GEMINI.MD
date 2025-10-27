
# Gemini Project: CIS Request Workflow

This file documents the steps taken by the Gemini agent to create a Flask application for handling new user requests, based on a provided PDF form.

## 1. Project Setup

- **Directories:** Created `templates` and `static` directories to structure the Flask application.
- **Dependencies:** Created a `requirements.txt` file with the following dependencies:
  - `Flask`
  - `Flask-SQLAlchemy`
  - `python-dotenv`
  - `docusign-esign`
- **Installation:** Installed the dependencies using `uv add`.

## 2. Flask Application (`main.py`)

- **Initialization:** Set up a basic Flask application with a SQLite database (`requests.db`).
- **Database Model:** Defined a `UserRequest` model in SQLAlchemy to store the form data. The model includes fields for all the information in the user request form, as well as a `status` field to track the approval process.
- **Routing:**
  - `@app.route('/')`: Renders the `index.html` template for the new user request form.
  - `@app.route('/submit', methods=['POST'])`: Handles the form submission, creates a new `UserRequest` object, and saves it to the database.
  - `@app.route('/dashboard')`: Renders the `dashboard.html` template, which displays all requests that are not yet approved.
  - `@app.route('/approve/<int:request_id>')`: Implements the multi-level approval logic. The status of the request is updated based on the current approval level.
  - `@app.route('/reject/<int:request_id>')`: Updates the status of the request to "Rejected".

## 3. Frontend

- **New User Request Form (`templates/index.html`):** An HTML form with all the fields from the provided PDF, including a dropdown for "User Security Groups by JOB FUNCTION". The form has been made more compact by grouping related fields into blocks and converting radio button selections for 'Request Type' and 'Environment required' into dropdown lists.
- **Approver Dashboard (`templates/dashboard.html`):** An HTML page that displays a table of pending requests with their details and provides links to approve or reject each request.
- **Styling (`static/style.css`):** A basic CSS file to provide some styling for the form and dashboard, updated to support the new compact form layout.
