import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
import secrets

def create_fake_users():
    """Create fake users for testing the application"""
    
    db_path = Path("data/users.db")
    
    # Fake users data
    fake_users = [
        # Patients
        {
            'username': 'John Smith',
            'email': 'john.smith@email.com',
            'phone': '+91 98765 43201',
            'password': 'password123',
            'role': 'patient'
        },
        {
            'username': 'Sarah Johnson',
            'email': 'sarah.johnson@email.com',
            'phone': '+91 98765 43202',
            'password': 'password123',
            'role': 'patient'
        },
        {
            'username': 'Mike Wilson',
            'email': 'mike.wilson@email.com',
            'phone': '+91 98765 43203',
            'password': 'password123',
            'role': 'patient'
        },
        {
            'username': 'Emily Davis',
            'email': 'emily.davis@email.com',
            'phone': '+91 98765 43204',
            'password': 'password123',
            'role': 'patient'
        },
        {
            'username': 'David Brown',
            'email': 'david.brown@email.com',
            'phone': '+91 98765 43205',
            'password': 'password123',
            'role': 'patient'
        },
        
        # Doctors
        {
            'username': 'Dr. Rajesh Kumar',
            'email': 'dr.rajesh@apollo.com',
            'phone': '+91 98765 43210',
            'password': 'password123',
            'role': 'doctor'
        },
        {
            'username': 'Dr. Priya Sharma',
            'email': 'dr.priya@fortis.com',
            'phone': '+91 98765 43211',
            'password': 'password123',
            'role': 'doctor'
        },
        {
            'username': 'Dr. Amit Patel',
            'email': 'dr.amit@medanta.com',
            'phone': '+91 98765 43212',
            'password': 'password123',
            'role': 'doctor'
        },
        {
            'username': 'Dr. Meera Reddy',
            'email': 'dr.meera@narayana.com',
            'phone': '+91 98765 43213',
            'password': 'password123',
            'role': 'doctor'
        },
        {
            'username': 'Dr. Sanjay Verma',
            'email': 'dr.sanjay@max.com',
            'phone': '+91 98765 43214',
            'password': 'password123',
            'role': 'doctor'
        }
    ]
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if users already exist
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        
        if count == 0:
            for user in fake_users:
                # Hash password
                password_hash = hashlib.sha256(user['password'].encode()).hexdigest()
                
                # Insert user
                cursor.execute('''
                    INSERT INTO users (username, email, phone, password_hash, role, is_verified)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user['username'], user['email'], user['phone'], 
                    password_hash, user['role'], True
                ))
            
            conn.commit()
            print("✅ Fake users created successfully!")
            print("\n📋 Test Users:")
            print("\n👤 Patients:")
            for user in fake_users[:5]:
                print(f"  - {user['username']} ({user['email']}) - Password: {user['password']}")
            
            print("\n👨‍⚕️ Doctors:")
            for user in fake_users[5:]:
                print(f"  - {user['username']} ({user['email']}) - Password: {user['password']}")
            
        else:
            print("ℹ️ Users already exist in database")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating fake users: {e}")

def add_more_fake_patients():
    db_path = Path("data/users.db")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "patient"')
    count = cursor.fetchone()[0]
    needed = 5 - count
    if needed > 0:
        fake_patients = [
            {'username': 'John Smith', 'email': 'john.smith@email.com', 'phone': '+91 98765 43201'},
            {'username': 'Sarah Johnson', 'email': 'sarah.johnson@email.com', 'phone': '+91 98765 43202'},
            {'username': 'Mike Wilson', 'email': 'mike.wilson@email.com', 'phone': '+91 98765 43203'},
            {'username': 'Emily Davis', 'email': 'emily.davis@email.com', 'phone': '+91 98765 43204'},
            {'username': 'David Brown', 'email': 'david.brown@email.com', 'phone': '+91 98765 43205'},
        ]
        # Only add as many as needed
        for patient in fake_patients[:needed]:
            salt = secrets.token_hex(16)
            password_hash = hashlib.sha256(('password123' + salt).encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, email, phone, password_hash, salt, role, is_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (patient['username'], patient['email'], patient['phone'], password_hash, salt, 'patient', True))
        conn.commit()
        print(f"✅ Added {needed} fake patients.")
    else:
        print("ℹ️ Enough fake patients already exist.")
    conn.close()

if __name__ == "__main__":
    add_more_fake_patients()
    create_fake_users() 