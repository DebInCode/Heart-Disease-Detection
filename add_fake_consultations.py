import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random

def debug_print_db():
    print('--- Database Debug Info ---')
    # Doctors
    conn = sqlite3.connect('data/doctors.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM doctors')
    doctors = c.fetchall()
    print(f'Doctors ({len(doctors)}):', [d[0] for d in doctors[:3]])
    c.execute('SELECT COUNT(*) FROM consultations')
    print('Consultations:', c.fetchone()[0])
    conn.close()
    # Patients
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()
    c.execute('SELECT id, username FROM users WHERE role = "patient"')
    patients = c.fetchall()
    print(f'Patients ({len(patients)}):', [p[0] for p in patients[:3]])
    conn.close()
    print('--------------------------')

def add_fake_consultations():
    """Add fake consultations for testing"""
    try:
        # Connect to doctors database
        doctors_db = Path("data/doctors.db")
        conn = sqlite3.connect(str(doctors_db))
        cursor = conn.cursor()
        
        # Get some doctors
        cursor.execute('SELECT id FROM doctors LIMIT 10')
        doctor_ids = [row[0] for row in cursor.fetchall()]
        print('Doctor IDs:', doctor_ids)
        
        # Get users from users database
        users_conn = sqlite3.connect("data/users.db")
        users_cursor = users_conn.cursor()
        users_cursor.execute('SELECT id FROM users WHERE role = "patient" LIMIT 15')
        patient_ids = [row[0] for row in users_cursor.fetchall()]
        users_conn.close()
        print('Patient IDs:', patient_ids)
        
        if doctor_ids and patient_ids:
            # Generate dates for the next 30 days
            base_date = datetime.now()
            dates = [(base_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
            
            # Consultation types and statuses
            consultation_types = ['Video Consultation', 'Chat Consultation', 'In-Person', 'Emergency Consultation']
            statuses = ['pending', 'confirmed', 'completed', 'cancelled']
            
            # Medical conditions and notes
            medical_conditions = [
                'Chest pain and shortness of breath',
                'High blood pressure management',
                'Heart disease risk assessment',
                'Regular cardiovascular check-up',
                'Family history of heart disease',
                'Post-heart attack follow-up',
                'Arrhythmia symptoms',
                'Cholesterol management',
                'Diabetes and heart health',
                'Stress-related heart symptoms',
                'Exercise-induced chest discomfort',
                'Heart valve disorder monitoring',
                'Cardiac rehabilitation consultation',
                'Preventive cardiology assessment',
                'Heart failure management'
            ]
            
            fake_consultations = []
            
            # Generate 50 fake consultations
            for i in range(50):
                doctor_id = random.choice(doctor_ids)
                patient_id = random.choice(patient_ids)
                consultation_type = random.choice(consultation_types)
                status = random.choice(statuses)
                date = random.choice(dates)
                time_hour = random.randint(9, 18)  # 9 AM to 6 PM
                time_minute = random.choice([0, 15, 30, 45])
                consultation_time = f"{time_hour:02d}:{time_minute:02d}:00"
                notes = random.choice(medical_conditions)
                
                fake_consultations.append({
                    'doctor_id': doctor_id,
                    'patient_id': patient_id,
                    'consultation_type': consultation_type,
                    'consultation_date': date,
                    'consultation_time': consultation_time,
                    'status': status,
                    'notes': notes
                })
            
            # Clear existing consultations (optional - comment out if you want to keep existing ones)
            cursor.execute('DELETE FROM consultations')
            
            # Insert new consultations
            for consultation in fake_consultations:
                cursor.execute('''
                    INSERT INTO consultations (
                        doctor_id, patient_id, consultation_type, consultation_date,
                        consultation_time, status, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    consultation['doctor_id'], consultation['patient_id'],
                    consultation['consultation_type'], consultation['consultation_date'],
                    consultation['consultation_time'], consultation['status'],
                    consultation['notes']
                ))
            
            conn.commit()
            print("✅ Fake consultations added successfully!")
            print(f"Added {len(fake_consultations)} consultations")
            
            # Show summary statistics
            cursor.execute('SELECT status, COUNT(*) FROM consultations GROUP BY status')
            status_counts = cursor.fetchall()
            print("\n📊 Consultation Status Summary:")
            for status, count in status_counts:
                print(f"- {status.capitalize()}: {count}")
            
            cursor.execute('SELECT consultation_type, COUNT(*) FROM consultations GROUP BY consultation_type')
            type_counts = cursor.fetchall()
            print("\n📋 Consultation Type Summary:")
            for consult_type, count in type_counts:
                print(f"- {consult_type}: {count}")
            
            # Show some recent consultations
            try:
                # First get consultations from doctors database
                cursor.execute('''
                    SELECT c.*, d.name as doctor_name
                    FROM consultations c
                    JOIN doctors d ON c.doctor_id = d.id
                    ORDER BY c.consultation_date DESC, c.consultation_time DESC
                    LIMIT 10
                ''')
                
                consultations = cursor.fetchall()
                
                # Now get patient names from users database
                users_conn = sqlite3.connect("data/users.db")
                users_cursor = users_conn.cursor()
                
                print("\n📋 Recent Consultations:")
                for consultation in consultations:
                    # Get patient name from users database
                    users_cursor.execute('SELECT username FROM users WHERE id = ?', (consultation[2],))  # consultation[2] is patient_id
                    user_result = users_cursor.fetchone()
                    patient_name = user_result[0] if user_result else f"Patient ID {consultation[2]}"
                    
                    # Use correct indices based on table structure
                    print(f"- Dr. {consultation[9]} with {patient_name} on {consultation[4]} at {consultation[5]} ({consultation[6]}) - {consultation[7]}")
                
                users_conn.close()
                
            except Exception as e:
                print(f"\n⚠️ Could not show detailed consultations: {e}")
                # Show consultations without patient names
                cursor.execute('''
                    SELECT c.*, d.name as doctor_name
                    FROM consultations c
                    JOIN doctors d ON c.doctor_id = d.id
                    ORDER BY c.consultation_date DESC, c.consultation_time DESC
                    LIMIT 10
                ''')
                
                consultations = cursor.fetchall()
                print("\n📋 Recent Consultations:")
                for consultation in consultations:
                    print(f"- Dr. {consultation[9]} with Patient ID {consultation[2]} on {consultation[4]} at {consultation[5]} ({consultation[6]}) - {consultation[7]}")
        else:
            print("❌ No doctors or patients found in database")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error adding fake consultations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_print_db()
    add_fake_consultations() 