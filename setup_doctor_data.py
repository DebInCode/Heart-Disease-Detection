#!/usr/bin/env python3
"""
Script to set up the doctor database with fake doctors and consultations
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def setup_doctor_data():
    """Set up the doctor database with fake data"""
    print("🔧 Setting up doctor database...")
    
    # Database path
    db_path = Path("data/doctors.db")
    
    # Initialize database
    print("📊 Initializing database...")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create doctors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            years_experience INTEGER NOT NULL,
            location TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            country TEXT DEFAULT 'India',
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            consultation_fee INTEGER NOT NULL,
            rating REAL DEFAULT 4.5,
            total_reviews INTEGER DEFAULT 0,
            bio TEXT,
            qualifications TEXT,
            languages TEXT,
            consultation_hours TEXT,
            video_consultation BOOLEAN DEFAULT 1,
            chat_consultation BOOLEAN DEFAULT 1,
            emergency_contact BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create consultations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER NOT NULL,
            patient_id INTEGER NOT NULL,
            consultation_type TEXT NOT NULL,
            consultation_date DATE NOT NULL,
            consultation_time TIME NOT NULL,
            duration_minutes INTEGER DEFAULT 15,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            video_call_link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doctor_id) REFERENCES doctors (id)
        )
    ''')
    
    # Create reviews table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER NOT NULL,
            patient_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doctor_id) REFERENCES doctors (id)
        )
    ''')
    
    # Create chat_messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consultation_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            sender_type TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (consultation_id) REFERENCES consultations (id)
        )
    ''')
    
    conn.commit()
    
    # Add fake doctors
    print("👨‍⚕️ Adding fake doctors...")
    fake_doctors = [
        {
            'name': 'Dr. Rajesh Kumar',
            'specialization': 'Cardiologist',
            'years_experience': 15,
            'location': 'Apollo Hospital',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'phone': '+91-9876543210',
            'email': 'dr.rajesh@apollo.com',
            'consultation_fee': 1500,
            'bio': 'Experienced cardiologist with expertise in interventional cardiology and heart failure management.',
            'qualifications': 'MBBS, MD (Cardiology), DM (Interventional Cardiology)',
            'languages': 'English, Hindi, Marathi'
        },
        {
            'name': 'Dr. Priya Sharma',
            'specialization': 'General Physician',
            'years_experience': 12,
            'location': 'Fortis Hospital',
            'city': 'Delhi',
            'state': 'Delhi',
            'phone': '+91-9876543211',
            'email': 'dr.priya@fortis.com',
            'consultation_fee': 800,
            'bio': 'General physician specializing in preventive care and chronic disease management.',
            'qualifications': 'MBBS, MD (General Medicine)',
            'languages': 'English, Hindi'
        },
        {
            'name': 'Dr. Amit Patel',
            'specialization': 'Cardiovascular Surgeon',
            'years_experience': 20,
            'location': 'Medanta Hospital',
            'city': 'Gurgaon',
            'state': 'Haryana',
            'phone': '+91-9876543212',
            'email': 'dr.amit@medanta.com',
            'consultation_fee': 2500,
            'bio': 'Senior cardiovascular surgeon with extensive experience in complex heart surgeries.',
            'qualifications': 'MBBS, MS (General Surgery), MCh (Cardiovascular Surgery)',
            'languages': 'English, Hindi, Gujarati'
        }
    ]
    
    for doctor in fake_doctors:
        cursor.execute('''
            INSERT OR IGNORE INTO doctors (
                name, specialization, years_experience, location, city, state,
                phone, email, consultation_fee, bio, qualifications, languages
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            doctor['name'], doctor['specialization'], doctor['years_experience'],
            doctor['location'], doctor['city'], doctor['state'], doctor['phone'],
            doctor['email'], doctor['consultation_fee'], doctor['bio'],
            doctor['qualifications'], doctor['languages']
        ))
    
    conn.commit()
    
    # Add fake consultations
    print("📅 Adding fake consultations...")
    
    # Get doctor IDs
    cursor.execute('SELECT id FROM doctors LIMIT 3')
    doctor_ids = [row[0] for row in cursor.fetchall()]
    
    # Get patient IDs from users database
    try:
        users_conn = sqlite3.connect("data/users.db")
        users_cursor = users_conn.cursor()
        users_cursor.execute('SELECT id FROM users WHERE role = "patient" LIMIT 5')
        patient_ids = [row[0] for row in users_cursor.fetchall()]
        users_conn.close()
    except:
        # If users.db doesn't exist, create fake patient IDs
        patient_ids = [1, 2, 3, 4, 5]
    
    if doctor_ids and patient_ids:
        fake_consultations = [
            {
                'doctor_id': doctor_ids[0],
                'patient_id': patient_ids[0],
                'consultation_type': 'Video Consultation',
                'consultation_date': '2025-06-30',
                'consultation_time': '10:00:00',
                'status': 'pending',
                'notes': 'Patient experiencing chest pain and shortness of breath'
            },
            {
                'doctor_id': doctor_ids[0],
                'patient_id': patient_ids[1],
                'consultation_type': 'Chat Consultation',
                'consultation_date': '2025-06-30',
                'consultation_time': '14:00:00',
                'status': 'confirmed',
                'notes': 'Follow-up consultation for heart disease risk assessment'
            },
            {
                'doctor_id': doctor_ids[1],
                'patient_id': patient_ids[2],
                'consultation_type': 'Video Consultation',
                'consultation_date': '2025-07-01',
                'consultation_time': '11:00:00',
                'status': 'pending',
                'notes': 'Patient with high blood pressure seeking consultation'
            }
        ]
        
        for consultation in fake_consultations:
            cursor.execute('''
                INSERT OR IGNORE INTO consultations (
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
    conn.close()
    
    # Verify the setup
    print("✅ Verifying setup...")
    
    # Check doctors
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM doctors')
    doctor_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM consultations')
    consultation_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"   Found {doctor_count} doctors")
    print(f"   Found {consultation_count} consultations")
    
    print("✅ Doctor database setup completed!")
    print("\n📋 Summary:")
    print(f"   - {doctor_count} doctors in the database")
    print(f"   - {consultation_count} consultations added")
    print("   - Database ready for testing")

if __name__ == "__main__":
    setup_doctor_data() 