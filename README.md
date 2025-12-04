StrokeGuard AI: System Architecture and Design Specification
1. Executive Summary and Architectural Pattern StrokeGuard AI is a web-based medical informatics application designed to assist healthcare professionals in the early detection of stroke risk. The system is built upon the Model-View-Controller (MVC) architectural pattern, adapted for the Flask web framework. This architecture ensures a clean separation of concerns:
The Model: Represented by the SQLite database and SQLAlchemy ORM, handling data structure and storage logic.
The View: Represented by the HTML templates and Jinja2 engine, handling the user interface and presentation.
The Controller: Represented by the app.py routes and functions, handling user input, the AI processing logic, and application flow.

2. Detailed Technology Stack The project relies on a specific set of robust, industry-standard technologies. Each was chosen to meet the security and functionality requirements of the assessment.

Python 3.12: The core programming language, selected for its strong support for data science and web development libraries.
Flask Framework: A micro-web framework used to build the server. Unlike heavy frameworks like Django, Flask allows for granular control over security implementations, which is essential for demonstrating the "Secure Software Development" learning outcomes.
SQLite: A serverless, self-contained SQL database engine. It was chosen for its reliability and ease of integration with Python, allowing the database to exist as a single file (users.db) within the project folder.
SQLAlchemy ORM: An Object-Relational Mapper that serves as the bridge between Python code and the SQLite database. It allows database manipulation using Python classes instead of raw SQL queries, which is a critical security feature for preventing SQL Injection attacks.
Flask-Login: A specialized extension that manages user sessions. It handles the complex logic of logging users in, maintaining their "logged-in" state across different pages via secure browser cookies, and logging them out.
Flask-WTF: An extension that integrates the WTForms library with Flask. It is primarily used for generating HTML forms and, most importantly, generating and validating CSRF (Cross-Site Request Forgery) tokens to prevent malicious attacks.
Werkzeug Security: A utility library that provides standard cryptographic hashing functions. It is used here specifically for generate_password_hash and check_password_hash to ensure passwords are never stored in plain text.
Bootstrap 5: A front-end CSS framework used to ensure the application is responsive (works on mobile and desktop) and aesthetically professional without requiring extensive custom CSS coding.
Chart.js: A JavaScript library used to render the dynamic data visualization (the Doughnut Chart) on the dashboard. It runs in the user's browser, taking data passed from the Python backend to draw interactive graphics.
Pytest: The testing framework used to verify the application's stability. It allows for the creation of automated test cases that simulate user actions and verify functionality without manual intervention.

3. Application Logic and The AI Engine The core intellectual property of this system is the Rule-Based AI Engine, implemented as a pure Python function named calculate_stroke_risk. This function represents a deterministic algorithm rather than a probabilistic machine learning model. This approach was chosen for its transparency—medical professionals can trace exactly why a patient was flagged as high risk.
The algorithm accepts six key clinical inputs: Age, Hypertension status, Heart Disease history, Glucose Level, BMI, and Smoking Status. It initializes a risk score of zero and iterates through a series of conditional checks (If-Then statements). Each check corresponds to a clinically validated risk factor derived from the Kaggle dataset attributes. For example, being over 70 years old adds 20 points, having hypertension adds 30 points, and having a BMI over 30 adds 10 points.
The final score is capped at 100. The output is then classified into three distinct tiers:
High Risk (Score 60-100): Indicates immediate medical attention is advised.
Medium Risk (Score 30-59): Indicates lifestyle intervention is required.
Low Risk (Score 0-29): Indicates the patient is currently within healthy parameters.

4. Database Design and Schema The database is structured into two primary tables, defined as Python Classes in app.py.
The User Table This table handles authentication. It contains three columns:
id: An Integer Primary Key that uniquely identifies each doctor.
username: A String column (max 150 characters) that must be unique across the system.
password_hash: A String column storing the encrypted version of the password.
The Patient Table This table acts as the digital health record. It matches the schema of the provided Stroke Prediction Dataset. It includes:
Demographics: Name, Gender, Age, Marital Status, Residence Type, Work Type.
Medical Metrics: Hypertension (0/1), Heart Disease (0/1), Average Glucose Level (Float), Body Mass Index (Float), Smoking Status.
AI Metadata: A specific column named stroke_risk stores the result of the AI prediction (e.g., "High Risk").
Foreign Key Relationship: A column named user_id links every patient record to the specific User.id of the doctor who created it. This establishes a "One-to-Many" relationship (One Doctor can have Many Patients) and enforces data ownership.

5. Detailed File Structure and Purpose

app.py: This is the controller and entry point. It initializes the Flask app, configures the database connection strings, defines the database models, and contains all the "Routes" (URL endpoints). Every time a user visits a page (like /dashboard), a function in this file is executed to fetch data and render the page.

forms.py: This file handles Data Validation. It defines the RegistrationForm, LoginForm, and PatientForm classes. By defining fields as IntegerFields or FloatFields with specific validators (like DataRequired), this file ensures that bad data (like text in an age field) is rejected before it ever reaches the database or the AI engine.

seed_data.py: This is an ETL (Extract, Transform, Load) utility script. It is designed to open the external CSV file (healthcare-dataset-stroke-data.csv), clean the data (specifically handling missing BMI values by assigning a safe average), run the data through the AI engine to generate risk labels, and bulk-insert the results into the database.
test_app.py: This file contains the suite of automated tests. It uses fixtures to create a temporary, isolated memory-database so that tests do not overwrite real data. It includes tests for the AI calculation logic, HTTP response codes (ensuring pages load), and database integration (ensuring records are saved and retrieved).
templates/ folder: This contains the HTML files.
base.html: The master template containing the navigation bar and footer. All other pages "extend" this file to maintain a consistent look.
dashboard.html: The main interface containing the logic for the data table and charts.
login.html / register.html: Secure forms for authentication.
static/ folder: Contains style.css. This file overrides the default Bootstrap styles to provide custom animations (like the hovering effect on dashboard cards) and specific color branding (black headers/footers) to meet the professional design criteria.

6. Security Protocol Implementation The application implements a "Defense in Depth" security strategy:
Input Sanitization: By using the SQLAlchemy ORM, all database inputs are automatically parameterized. This means user input is treated strictly as data, never as executable code, effectively neutralizing SQL Injection attacks.
CSRF Tokens: Every form includes a hidden csrf_token generated by Flask-WTF. The server validates this token with every POST request. If a malicious site tries to force a user's browser to submit a form on StrokeGuard AI, the token will be missing or invalid, and the request will be blocked.
Session Security: Flask-Login manages the session cookie. It uses the application's SECRET_KEY to cryptographically sign the cookie, preventing tampering. If a user tries to modify their cookie to impersonate another user (Session Hijacking), the server detects the broken signature and invalidates the session.
Access Control: The @login_required decorator acts as a gatekeeper for sensitive routes. If an unauthenticated user attempts to access /dashboard or /export_data, the application intercepts the request and redirects them to the login page.

7. Data Flow and User Journey
Registration: A user submits the registration form. The forms.py validation checks if the username meets length requirements. app.py receives the data, hashes the password using Werkzeug, and creates a new User record in SQLite.
Authentication: The user logs in. app.py retrieves the user by username and compares the provided password against the stored hash. If they match, a session is created.
Data Entry: The user clicks "Add Patient". A modal opens. Data is entered and submitted.
Processing: The application receives the data. First, it is passed to the calculate_stroke_risk function (The AI). The result is appended to the patient object.
Storage: The patient object (containing input data + AI result) is committed to the SQLite database.
Visualization: The dashboard reloads. The new patient appears in the table. The Chart.js script recalculates the totals of High/Medium/Low risk patients and updates the Doughnut chart visuals instantly.

8. Advanced Features To meet the Distinction/Exceptional criteria, the application includes:
Visual Analytics: Integration of Chart.js for real-time data visualization.
Data Export: A dedicated endpoint that serializes database records into CSV format and triggers a browser download, allowing for external data portability.
Search Functionality: A dynamic SQL query filter that allows real-time searching of patient records by name.
Responsive Design: A fluid grid layout that adapts to different screen sizes, ensuring the application is usable on tablets and mobile devices.