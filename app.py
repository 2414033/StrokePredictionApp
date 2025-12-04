import csv
import io
from flask import Flask, render_template, redirect, url_for, flash, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, PatientForm
import os

app = Flask(__name__)

# --- CONFIGURATION ---
app.config['SECRET_KEY'] = 'your-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- THE AI ENGINE (PREDICTION LOGIC) ---
def calculate_stroke_risk(age, hypertension, heart_disease, glucose, bmi, smoking):
    """
    A Rule-Based AI algorithm to predict stroke risk score (0-100).
    """
    score = 0
    
    # 1. Age Factor
    if age > 50: score += 10
    if age > 70: score += 20
    
    # 2. Medical History
    if hypertension == '1': score += 30
    if heart_disease == '1': score += 20
    
    # 3. Glucose Levels
    if glucose > 200: score += 20
    elif glucose > 140: score += 10
    
    # 4. BMI
    if bmi > 30: score += 10
    
    # 5. Smoking Status
    if smoking == 'smokes': score += 15
    elif smoking == 'formerly smoked': score += 5

    # Cap at 100
    if score > 100: score = 100
    
    # Return Label
    if score >= 60:
        return "High Risk"
    elif score >= 30:
        return "Medium Risk"
    else:
        return "Low Risk"

# --- DATABASE MODELS ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    hypertension = db.Column(db.String(10), nullable=False)
    heart_disease = db.Column(db.String(10), nullable=False)
    ever_married = db.Column(db.String(10), nullable=False)
    work_type = db.Column(db.String(50), nullable=False)
    residence_type = db.Column(db.String(20), nullable=False)
    avg_glucose_level = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    smoking_status = db.Column(db.String(50), nullable=False)
    
    # AI Prediction Result
    stroke_risk = db.Column(db.String(20), nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    form = PatientForm()
    
    # 1. HANDLE SEARCH QUERY
    search_query = request.args.get('q')
    if search_query:
        # Filter patients by name (case insensitive)
        patients = Patient.query.filter(Patient.name.contains(search_query)).all()
    else:
        patients = Patient.query.all()

    # 2. CALCULATE STATISTICS FOR CHARTS
    high_risk_count = Patient.query.filter_by(stroke_risk='High Risk').count()
    medium_risk_count = Patient.query.filter_by(stroke_risk='Medium Risk').count()
    low_risk_count = Patient.query.filter_by(stroke_risk='Low Risk').count()

    return render_template('dashboard.html', 
                           form=form, 
                           patients=patients,
                           high_risk=high_risk_count,
                           medium_risk=medium_risk_count,
                           low_risk=low_risk_count)

@app.route('/add_patient', methods=['POST'])
@login_required
def add_patient():
    form = PatientForm()
    if form.validate_on_submit():
        # RUN AI PREDICTION
        predicted_risk = calculate_stroke_risk(
            age=form.age.data,
            hypertension=form.hypertension.data,
            heart_disease=form.heart_disease.data,
            glucose=form.avg_glucose_level.data,
            bmi=form.bmi.data,
            smoking=form.smoking_status.data
        )

        new_patient = Patient(
            name=form.name.data,
            gender=form.gender.data,
            age=form.age.data,
            hypertension=form.hypertension.data,
            heart_disease=form.heart_disease.data,
            ever_married=form.ever_married.data,
            work_type=form.work_type.data,
            residence_type=form.residence_type.data,
            avg_glucose_level=form.avg_glucose_level.data,
            bmi=form.bmi.data,
            smoking_status=form.smoking_status.data,
            stroke_risk=predicted_risk, # Save AI Result
            user_id=current_user.id
        )
        db.session.add(new_patient)
        db.session.commit()
        flash(f'Patient added! AI Prediction: {predicted_risk}', 'success')
    else:
        flash(f'Error adding patient: {form.errors}', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = PatientForm()

    if form.validate_on_submit():
        patient.name = form.name.data
        patient.gender = form.gender.data
        patient.age = form.age.data
        patient.hypertension = form.hypertension.data
        patient.avg_glucose_level = form.avg_glucose_level.data
        patient.bmi = form.bmi.data
        patient.heart_disease = form.heart_disease.data
        patient.work_type = form.work_type.data
        patient.ever_married = form.ever_married.data
        patient.residence_type = form.residence_type.data
        patient.smoking_status = form.smoking_status.data
        
        # RE-CALCULATE AI RISK
        patient.stroke_risk = calculate_stroke_risk(
            age=form.age.data,
            hypertension=form.hypertension.data,
            heart_disease=form.heart_disease.data,
            glucose=form.avg_glucose_level.data,
            bmi=form.bmi.data,
            smoking=form.smoking_status.data
        )
        
        db.session.commit()
        flash(f'Record Updated! New AI Prediction: {patient.stroke_risk}', 'success')
        return redirect(url_for('dashboard'))

    elif request.method == 'GET':
        form.name.data = patient.name
        form.gender.data = patient.gender
        form.age.data = patient.age
        form.hypertension.data = patient.hypertension
        form.avg_glucose_level.data = patient.avg_glucose_level
        form.bmi.data = patient.bmi
        form.heart_disease.data = patient.heart_disease
        form.work_type.data = patient.work_type
        form.ever_married.data = patient.ever_married
        form.residence_type.data = patient.residence_type
        form.smoking_status.data = patient.smoking_status

    return render_template('edit_patient.html', form=form, patient=patient)

@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
@login_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    flash('Patient record deleted.', 'info')
    return redirect(url_for('dashboard'))

# --- EXPORT DATA TO EXCEL ---
@app.route('/export_data')
@login_required
def export_data():
    patients = Patient.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow(['ID', 'Name', 'Gender', 'Age', 'Hypertension', 'Heart Disease', 
                     'Glucose Level', 'BMI', 'Smoking Status', 
                     'Work Type', 'Residence Type', 'Married', 'Stroke Risk'])

    # Data
    for p in patients:
        writer.writerow([p.id, p.name, p.gender, p.age, p.hypertension, p.heart_disease, 
                         p.avg_glucose_level, p.bmi, p.smoking_status, 
                         p.work_type, p.residence_type, p.ever_married, p.stroke_risk])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=patient_data.csv"}
    )

# --- AUTH ROUTES ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username taken', 'danger')
            return redirect(url_for('register'))
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Failed', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)