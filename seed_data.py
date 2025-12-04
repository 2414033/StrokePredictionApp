import csv
from app import app, db, Patient, calculate_stroke_risk

def import_csv():
    print("--- Starting Data Import ---")
    
    # Open the CSV file
    try:
        with open('healthcare-dataset-stroke-data.csv', 'r') as file:
            reader = csv.DictReader(file)
            
            count = 0
            with app.app_context():
                # Optional: Clear existing patients to avoid duplicates
                # db.session.query(Patient).delete()
                
                for row in reader:
                    # 1. CLEANING DATA
                    # The dataset has "N/A" for BMI sometimes. We fix that.
                    bmi_value = row['bmi']
                    if bmi_value == 'N/A':
                        bmi_value = 28.0 # Assign average BMI if missing
                    else:
                        bmi_value = float(bmi_value)

                    # 2. RUN AI PREDICTION ON IMPORTED DATA
                    risk_label = calculate_stroke_risk(
                        age=float(row['age']),
                        hypertension=row['hypertension'],
                        heart_disease=row['heart_disease'],
                        glucose=float(row['avg_glucose_level']),
                        bmi=bmi_value,
                        smoking=row['smoking_status']
                    )

                    # 3. CREATE PATIENT OBJECT
                    # Note: We assign these to User ID 1 (The first doctor/admin)
                    patient = Patient(
                        name=f"Patient {row['id']}", # Dataset doesn't have names, so we use ID
                        gender=row['gender'],
                        age=int(float(row['age'])),
                        hypertension=row['hypertension'],
                        heart_disease=row['heart_disease'],
                        ever_married=row['ever_married'],
                        work_type=row['work_type'],
                        residence_type=row['Residence_type'],
                        avg_glucose_level=float(row['avg_glucose_level']),
                        bmi=bmi_value,
                        smoking_status=row['smoking_status'],
                        stroke_risk=risk_label,
                        user_id=1 
                    )
                    
                    db.session.add(patient)
                    count += 1
                    
                    if count % 100 == 0:
                        print(f"Processed {count} records...")

                db.session.commit()
                print(f"SUCCESS! Imported {count} patients into the database.")

    except FileNotFoundError:
        print("Error: Could not find 'healthcare-dataset-stroke-data.csv'. Make sure it is in the project folder.")

if __name__ == '__main__':
    import_csv()