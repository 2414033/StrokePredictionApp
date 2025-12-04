import pytest
from app import app, db, User, Patient, calculate_stroke_risk

# --- FIXTURE: SETS UP A FAKE APP FOR TESTING ---
@pytest.fixture
def client():
    # 1. Configure app for testing mode
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable security tokens
    # Use IN-MEMORY database (RAM) so we don't touch your real users.db
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    
    # 2. FORCE DISCONNECT from real database
    with app.app_context():
        db.engine.dispose()  # <--- THIS IS THE FIX FOR "SAQLAIN" ERROR
        db.create_all()      # Create fresh tables in RAM

    # 3. Create the Test Client
    with app.test_client() as client:
        yield client
    
    # 4. Cleanup after tests
    with app.app_context():
        db.session.remove()
        db.drop_all()

# --- TEST 1: THE AI BRAIN ---
def test_ai_calculation():
    """Test if the AI correctly identifies High vs Low risk."""
    risk_high = calculate_stroke_risk(75, '1', '1', 220, 35, 'smokes')
    assert risk_high == "High Risk"

    risk_low = calculate_stroke_risk(25, '0', '0', 85, 22, 'never smoked')
    assert risk_low == "Low Risk"

# --- TEST 2: HOME PAGE ---
def test_home_page(client):
    """Test that the home page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"StrokeGuard AI" in response.data

# --- TEST 3: USER REGISTRATION ---
def test_register(client):
    """Test creating a new doctor account."""
    response = client.post('/register', data={
        'username': 'testdoctor',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    # This checks if "Account created!" appears on the page.
    # If this fails, your base.html is missing the 'get_flashed_messages' block.
    assert b"Account created!" in response.data 

# --- TEST 4: LOGIN & ADD PATIENT ---
def test_add_patient_logic(client):
    """Test the full flow: Register -> Login -> Add Patient -> Check Database"""
    
    # Register & Login
    client.post('/register', data={'username': 'doc1', 'password': 'password', 'confirm_password': 'password'}, follow_redirects=True)
    client.post('/login', data={'username': 'doc1', 'password': 'password'}, follow_redirects=True)

    # Add Patient
    response = client.post('/add_patient', data={
        'name': 'John Doe',
        'gender': 'Male',
        'age': 65,
        'hypertension': '1',
        'heart_disease': '0',
        'avg_glucose_level': 180.5,
        'bmi': 29.0,
        'smoking_status': 'formerly smoked',
        'work_type': 'Private',
        'residence_type': 'Urban',
        'ever_married': 'Yes'
    }, follow_redirects=True)

    # Check Success Message
    assert b"Patient added!" in response.data

    # Check Database (Should now find John Doe, NOT Saqlain)
    with app.app_context():
        patient = Patient.query.first()
        assert patient.name == 'John Doe'