from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PatientForm(FlaskForm):
    # Added Name field
    name = StringField('Patient Name', validators=[DataRequired(), Length(min=2, max=50)])
    
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    age = IntegerField('Age', validators=[DataRequired()])
    hypertension = SelectField('Hypertension', choices=[('0', 'No'), ('1', 'Yes')])
    heart_disease = SelectField('Heart Disease', choices=[('0', 'No'), ('1', 'Yes')])
    ever_married = SelectField('Ever Married', choices=[('No', 'No'), ('Yes', 'Yes')])
    work_type = SelectField('Work Type', choices=[
        ('Private', 'Private'), 
        ('Self-employed', 'Self-employed'), 
        ('Govt_job', 'Govt_job'), 
        ('Children', 'Children'), 
        ('Never_worked', 'Never_worked')
    ])
    residence_type = SelectField('Residence Type', choices=[('Urban', 'Urban'), ('Rural', 'Rural')])
    avg_glucose_level = FloatField('Avg Glucose Level', validators=[DataRequired()])
    bmi = FloatField('BMI', validators=[DataRequired()])
    smoking_status = SelectField('Smoking Status', choices=[
        ('formerly smoked', 'Formerly Smoked'), 
        ('never smoked', 'Never Smoked'), 
        ('smokes', 'Smokes'), 
        ('Unknown', 'Unknown')
    ])
    submit = SubmitField('Save Record')