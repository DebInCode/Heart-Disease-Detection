import streamlit as st
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import secrets

class DoctorRegistry:
    """Doctor registry system with ratings, experience, and contact features."""
    
    def __init__(self):
        self.db_path = Path("data/doctors.db")
        self.init_doctor_database()
        self.add_fake_doctors()
        self.add_fake_consultations()
    
    def init_doctor_database(self):
        """Initialize the doctor database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
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
                    country TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT NOT NULL,
                    consultation_fee REAL NOT NULL,
                    rating REAL DEFAULT 0.0,
                    total_reviews INTEGER DEFAULT 0,
                    is_verified BOOLEAN DEFAULT FALSE,
                    is_available BOOLEAN DEFAULT TRUE,
                    bio TEXT,
                    qualifications TEXT,
                    languages TEXT,
                    consultation_hours TEXT,
                    emergency_contact BOOLEAN DEFAULT FALSE,
                    video_consultation BOOLEAN DEFAULT FALSE,
                    chat_consultation BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create doctor reviews table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS doctor_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doctor_id INTEGER,
                    patient_id INTEGER,
                    rating INTEGER NOT NULL,
                    review_text TEXT,
                    consultation_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create consultation bookings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS consultations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doctor_id INTEGER,
                    patient_id INTEGER,
                    consultation_type TEXT NOT NULL,
                    consultation_date DATE NOT NULL,
                    consultation_time TIME NOT NULL,
                    duration_minutes INTEGER DEFAULT 15,
                    status TEXT DEFAULT 'pending',
                    notes TEXT,
                    video_call_link TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create chat messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    consultation_id INTEGER,
                    sender_id INTEGER,
                    sender_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (consultation_id) REFERENCES consultations (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Database initialization error: {e}")
    
    def add_fake_doctors(self):
        """Add fake doctor data for prototype"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Check if fake doctors already exist
            cursor.execute('SELECT COUNT(*) FROM doctors')
            count = cursor.fetchone()[0]
            
            if count == 0:
                fake_doctors = [
                    {
                        'name': 'Dr. Rajesh Kumar',
                        'specialization': 'Cardiologist',
                        'years_experience': 15,
                        'location': 'Apollo Heart Institute',
                        'city': 'Mumbai',
                        'state': 'Maharashtra',
                        'country': 'India',
                        'phone': '+91 98765 43210',
                        'email': 'dr.rajesh@apollo.com',
                        'consultation_fee': 1500,
                        'rating': 4.8,
                        'total_reviews': 127,
                        'bio': 'Senior Cardiologist with 15+ years of experience in interventional cardiology.',
                        'qualifications': 'MBBS, MD (Cardiology), DM (Interventional Cardiology)',
                        'languages': 'English, Hindi, Marathi',
                        'consultation_hours': 'Mon-Fri: 9 AM - 6 PM\nSat: 9 AM - 2 PM',
                        'emergency_contact': True,
                        'video_consultation': True,
                        'chat_consultation': True
                    },
                    {
                        'name': 'Dr. Priya Sharma',
                        'specialization': 'Cardiovascular Surgeon',
                        'years_experience': 12,
                        'location': 'Fortis Heart Hospital',
                        'city': 'Delhi',
                        'state': 'Delhi',
                        'country': 'India',
                        'phone': '+91 98765 43211',
                        'email': 'dr.priya@fortis.com',
                        'consultation_fee': 2000,
                        'rating': 4.9,
                        'total_reviews': 89,
                        'bio': 'Expert in minimally invasive cardiac surgeries and heart transplants.',
                        'qualifications': 'MBBS, MS (General Surgery), MCh (Cardiovascular Surgery)',
                        'languages': 'English, Hindi, Punjabi',
                        'consultation_hours': 'Mon-Sat: 10 AM - 7 PM',
                        'emergency_contact': True,
                        'video_consultation': True,
                        'chat_consultation': False
                    },
                    {
                        'name': 'Dr. Amit Patel',
                        'specialization': 'Interventional Cardiologist',
                        'years_experience': 10,
                        'location': 'Medanta Heart Institute',
                        'city': 'Gurgaon',
                        'state': 'Haryana',
                        'country': 'India',
                        'phone': '+91 98765 43212',
                        'email': 'dr.amit@medanta.com',
                        'consultation_fee': 1800,
                        'rating': 4.7,
                        'total_reviews': 156,
                        'bio': 'Specialist in angioplasty, stenting, and structural heart interventions.',
                        'qualifications': 'MBBS, MD (Cardiology), FSCAI',
                        'languages': 'English, Hindi, Gujarati',
                        'consultation_hours': 'Mon-Fri: 8 AM - 5 PM',
                        'emergency_contact': True,
                        'video_consultation': True,
                        'chat_consultation': True
                    },
                    {
                        'name': 'Dr. Meera Reddy',
                        'specialization': 'Heart Failure Specialist',
                        'years_experience': 8,
                        'location': 'Narayana Health',
                        'city': 'Bangalore',
                        'state': 'Karnataka',
                        'country': 'India',
                        'phone': '+91 98765 43213',
                        'email': 'dr.meera@narayana.com',
                        'consultation_fee': 1200,
                        'rating': 4.6,
                        'total_reviews': 94,
                        'bio': 'Dedicated to managing heart failure and cardiac rehabilitation.',
                        'qualifications': 'MBBS, MD (Cardiology), Fellowship in Heart Failure',
                        'languages': 'English, Hindi, Telugu, Kannada',
                        'consultation_hours': 'Mon-Sat: 9 AM - 4 PM',
                        'emergency_contact': False,
                        'video_consultation': True,
                        'chat_consultation': True
                    },
                    {
                        'name': 'Dr. Sanjay Verma',
                        'specialization': 'Preventive Cardiologist',
                        'years_experience': 20,
                        'location': 'Max Super Speciality Hospital',
                        'city': 'Pune',
                        'state': 'Maharashtra',
                        'country': 'India',
                        'phone': '+91 98765 43214',
                        'email': 'dr.sanjay@max.com',
                        'consultation_fee': 1000,
                        'rating': 4.9,
                        'total_reviews': 203,
                        'bio': 'Focus on preventive cardiology and lifestyle medicine.',
                        'qualifications': 'MBBS, MD (Cardiology), MPH',
                        'languages': 'English, Hindi, Marathi',
                        'consultation_hours': 'Mon-Fri: 10 AM - 6 PM',
                        'emergency_contact': False,
                        'video_consultation': True,
                        'chat_consultation': True
                    }
                ]
                
                for doctor in fake_doctors:
                    cursor.execute('''
                        INSERT INTO doctors (
                            name, specialization, years_experience, location, city, state, country,
                            phone, email, consultation_fee, rating, total_reviews, bio, qualifications,
                            languages, consultation_hours, emergency_contact, video_consultation, chat_consultation
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        doctor['name'], doctor['specialization'], doctor['years_experience'],
                        doctor['location'], doctor['city'], doctor['state'], doctor['country'],
                        doctor['phone'], doctor['email'], doctor['consultation_fee'],
                        doctor['rating'], doctor['total_reviews'], doctor['bio'],
                        doctor['qualifications'], doctor['languages'], doctor['consultation_hours'],
                        doctor['emergency_contact'], doctor['video_consultation'], doctor['chat_consultation']
                    ))
                
                conn.commit()
                st.success("✅ Fake doctor data added successfully!")
            
            conn.close()
            
        except Exception as e:
            st.error(f"Error adding fake doctors: {e}")
    
    def register_doctor(self, user_id: int, doctor_data: dict) -> dict:
        """Register a new doctor"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO doctors (
                    user_id, name, specialization, years_experience, location, city, state, country,
                    phone, email, consultation_fee, bio, qualifications, languages, consultation_hours,
                    emergency_contact, video_consultation, chat_consultation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, doctor_data['name'], doctor_data['specialization'], doctor_data['years_experience'],
                doctor_data['location'], doctor_data['city'], doctor_data['state'], doctor_data['country'],
                doctor_data['phone'], doctor_data['email'], doctor_data['consultation_fee'],
                doctor_data.get('bio', ''), doctor_data.get('qualifications', ''),
                doctor_data.get('languages', ''), doctor_data.get('consultation_hours', ''),
                doctor_data.get('emergency_contact', False), doctor_data.get('video_consultation', False),
                doctor_data.get('chat_consultation', False)
            ))
            
            doctor_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {'success': True, 'doctor_id': doctor_id, 'message': 'Doctor registered successfully'}
            
        except Exception as e:
            return {'success': False, 'message': f'Registration failed: {str(e)}'}
    
    def get_doctors(self, filters: dict = None) -> list:
        """Get doctors with optional filters"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            
            query = '''
                SELECT d.*, 
                       COUNT(r.id) as review_count,
                       AVG(r.rating) as avg_rating
                FROM doctors d
                LEFT JOIN doctor_reviews r ON d.id = r.doctor_id
                WHERE d.is_available = TRUE
            '''
            
            params = []
            
            if filters:
                if filters.get('specialization'):
                    query += ' AND d.specialization = ?'
                    params.append(filters['specialization'])
                
                if filters.get('city'):
                    query += ' AND d.city = ?'
                    params.append(filters['city'])
                
                if filters.get('min_experience'):
                    query += ' AND d.years_experience >= ?'
                    params.append(filters['min_experience'])
                
                if filters.get('max_fee'):
                    query += ' AND d.consultation_fee <= ?'
                    params.append(filters['max_fee'])
            
            query += ' GROUP BY d.id ORDER BY avg_rating DESC, d.years_experience DESC'
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            st.error(f"Error fetching doctors: {e}")
            return []
    
    def get_doctor_details(self, doctor_id: int) -> dict:
        """Get detailed doctor information"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM doctors WHERE id = ?', (doctor_id,))
            doctor = cursor.fetchone()
            
            if doctor:
                # Get reviews
                cursor.execute('''
                    SELECT r.*, u.username as patient_name
                    FROM doctor_reviews r
                    JOIN users u ON r.patient_id = u.id
                    WHERE r.doctor_id = ?
                    ORDER BY r.created_at DESC
                ''', (doctor_id,))
                
                reviews = cursor.fetchall()
                
                conn.close()
                
                return {
                    'doctor': dict(zip([col[0] for col in cursor.description], doctor)),
                    'reviews': reviews
                }
            
            conn.close()
            return None
            
        except Exception as e:
            st.error(f"Error fetching doctor details: {e}")
            return None
    
    def book_consultation(self, doctor_id: int, patient_id: int, consultation_data: dict) -> dict:
        """Book a consultation with a doctor"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Check if duration_minutes column exists
            cursor.execute("PRAGMA table_info(consultations)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Generate video call link for video consultations
            video_call_link = None
            if consultation_data['type'] == 'Video Consultation':
                video_call_link = f"https://meet.jit.si/heartcare-{secrets.token_urlsafe(8)}"
            
            if 'duration_minutes' in columns:
                # Column exists, use it
                cursor.execute('''
                    INSERT INTO consultations (
                        doctor_id, patient_id, consultation_type, consultation_date, 
                        consultation_time, duration_minutes, notes, video_call_link
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    doctor_id, patient_id, consultation_data['type'],
                    consultation_data['date'], consultation_data['time'], 
                    consultation_data.get('duration_minutes', 15),
                    consultation_data.get('notes', ''), video_call_link
                ))
            else:
                # Column doesn't exist, insert without it
                cursor.execute('''
                    INSERT INTO consultations (
                        doctor_id, patient_id, consultation_type, consultation_date, 
                        consultation_time, notes, video_call_link
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    doctor_id, patient_id, consultation_data['type'],
                    consultation_data['date'], consultation_data['time'],
                    consultation_data.get('notes', ''), video_call_link
                ))
            
            consultation_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'success': True, 
                'consultation_id': consultation_id, 
                'video_call_link': video_call_link,
                'message': 'Consultation booked successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Booking failed: {str(e)}'}
    
    def get_doctor_consultations(self, doctor_id: int) -> list:
        """Get consultations for a specific doctor"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get consultations without user data first
            cursor.execute('''
                SELECT c.*
                FROM consultations c
                WHERE c.doctor_id = ?
                ORDER BY c.consultation_date DESC, c.consultation_time DESC
            ''', (doctor_id,))
            
            consultations = cursor.fetchall()
            conn.close()
            
            # Now get user data from the users database
            enriched_consultations = []
            if consultations:
                users_conn = sqlite3.connect("data/users.db")
                users_cursor = users_conn.cursor()
                
                for consultation in consultations:
                    # Get patient name from users database
                    users_cursor.execute('SELECT username, email FROM users WHERE id = ?', (consultation[2],))  # consultation[2] is patient_id
                    user_data = users_cursor.fetchone()
                    
                    if user_data:
                        # Create enriched consultation tuple with patient name and email
                        enriched_consultation = consultation + (user_data[0], user_data[1])  # Add username and email
                        enriched_consultations.append(enriched_consultation)
                    else:
                        # If user not found, add placeholder data
                        enriched_consultation = consultation + ("Unknown Patient", "unknown@email.com")
                        enriched_consultations.append(enriched_consultation)
                
                users_conn.close()
            
            return enriched_consultations
            
        except Exception as e:
            st.error(f"Error fetching consultations: {e}")
            return []
    
    def get_patient_consultations(self, patient_id: int) -> list:
        """Get consultations for a specific patient"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get consultations with doctor data
            cursor.execute('''
                SELECT c.*, d.name as doctor_name, d.specialization
                FROM consultations c
                JOIN doctors d ON c.doctor_id = d.id
                WHERE c.patient_id = ?
                ORDER BY c.consultation_date DESC, c.consultation_time DESC
            ''', (patient_id,))
            
            consultations = cursor.fetchall()
            conn.close()
            
            return consultations
            
        except Exception as e:
            st.error(f"Error fetching consultations: {e}")
            return []
    
    def update_consultation_status(self, consultation_id: int, status: str) -> dict:
        """Update consultation status"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('UPDATE consultations SET status = ? WHERE id = ?', (status, consultation_id))
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Status updated successfully'}
            
        except Exception as e:
            return {'success': False, 'message': f'Update failed: {str(e)}'}
    
    def send_chat_message(self, consultation_id: int, sender_id: int, sender_type: str, message: str) -> dict:
        """Send a chat message"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO chat_messages (consultation_id, sender_id, sender_type, message)
                VALUES (?, ?, ?, ?)
            ''', (consultation_id, sender_id, sender_type, message))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Message sent successfully'}
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to send message: {str(e)}'}
    
    def get_chat_messages(self, consultation_id: int) -> list:
        """Get chat messages for a consultation"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM chat_messages 
                WHERE consultation_id = ?
                ORDER BY created_at ASC
            ''', (consultation_id,))
            
            messages = cursor.fetchall()
            conn.close()
            
            return messages
            
        except Exception as e:
            st.error(f"Error fetching chat messages: {e}")
            return []
    
    def add_fake_consultations(self):
        """Add fake consultations for testing"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Check if consultations already exist
            cursor.execute('SELECT COUNT(*) FROM consultations')
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Get some doctors and patients
                cursor.execute('SELECT id FROM doctors LIMIT 3')
                doctor_ids = [row[0] for row in cursor.fetchall()]
                
                # Get users from users database
                users_conn = sqlite3.connect("data/users.db")
                users_cursor = users_conn.cursor()
                users_cursor.execute('SELECT id FROM users WHERE role = "patient" LIMIT 5')
                patient_ids = [row[0] for row in users_cursor.fetchall()]
                users_conn.close()
                
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
                        },
                        {
                            'doctor_id': doctor_ids[1],
                            'patient_id': patient_ids[3],
                            'consultation_type': 'In-Person',
                            'consultation_date': '2025-07-01',
                            'consultation_time': '15:00:00',
                            'status': 'confirmed',
                            'notes': 'Regular check-up for heart health monitoring'
                        },
                        {
                            'doctor_id': doctor_ids[2],
                            'patient_id': patient_ids[4],
                            'consultation_type': 'Video Consultation',
                            'consultation_date': '2025-07-02',
                            'consultation_time': '09:00:00',
                            'status': 'pending',
                            'notes': 'Patient with family history of heart disease'
                        }
                    ]
                    
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
                    st.success("✅ Fake consultations added successfully!")
            
            conn.close()
            
        except Exception as e:
            st.error(f"Error adding fake consultations: {e}")

def render_doctor_registration():
    """Render doctor registration form - only for doctors"""
    from components.login_auth import is_doctor
    
    if not is_doctor():
        st.error("❌ Access Denied: Only doctors can register as healthcare professionals.")
        return
    
    st.markdown("## 👨‍⚕️ Doctor Registration")
    st.markdown("Register your professional profile to help patients.")
    
    registry = DoctorRegistry()
    
    with st.form("doctor_registration_form"):
        st.markdown("### Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", placeholder="Dr. John Doe")
            specialization = st.selectbox("Specialization", [
                "Cardiologist", "General Physician", "Cardiovascular Surgeon",
                "Interventional Cardiologist", "Heart Failure Specialist",
                "Electrophysiologist", "Preventive Cardiologist"
            ])
            years_experience = st.number_input("Years of Experience", min_value=0, max_value=50, value=5)
            location = st.text_input("Clinic/Hospital Name", placeholder="City Heart Hospital")
        
        with col2:
            city = st.text_input("City", placeholder="Mumbai")
            state = st.text_input("State", placeholder="Maharashtra")
            country = st.text_input("Country", placeholder="India")
            phone = st.text_input("Phone Number", placeholder="+91 98765 43210")
        
        st.markdown("### Contact & Consultation")
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input("Email", placeholder="doctor@example.com")
            consultation_fee = st.number_input("Consultation Fee (₹)", min_value=0, value=500)
            consultation_hours = st.text_area("Consultation Hours", placeholder="Mon-Fri: 9 AM - 6 PM\nSat: 9 AM - 2 PM")
        
        with col2:
            emergency_contact = st.checkbox("Available for Emergency")
            video_consultation = st.checkbox("Video Consultation Available")
            chat_consultation = st.checkbox("Chat Consultation Available")
        
        st.markdown("### Professional Details")
        bio = st.text_area("Bio", placeholder="Brief description about your practice and expertise...")
        qualifications = st.text_area("Qualifications", placeholder="MBBS, MD (Cardiology), FSCAI...")
        languages = st.text_input("Languages Spoken", placeholder="English, Hindi, Marathi")
        
        if st.form_submit_button("📝 Register as Doctor", type="primary"):
            if name and specialization and phone and email:
                doctor_data = {
                    'name': name,
                    'specialization': specialization,
                    'years_experience': years_experience,
                    'location': location,
                    'city': city,
                    'state': state,
                    'country': country,
                    'phone': phone,
                    'email': email,
                    'consultation_fee': consultation_fee,
                    'consultation_hours': consultation_hours,
                    'emergency_contact': emergency_contact,
                    'video_consultation': video_consultation,
                    'chat_consultation': chat_consultation,
                    'bio': bio,
                    'qualifications': qualifications,
                    'languages': languages
                }
                
                if 'user_data' in st.session_state:
                    user_data = st.session_state.user_data
                    result = registry.register_doctor(user_data['user_id'], doctor_data)
                    
                    if result['success']:
                        st.success("✅ Doctor registration successful!")
                        st.info("Your profile will be reviewed and verified within 24 hours.")
                    else:
                        st.error(f"❌ {result['message']}")
                else:
                    st.error("Please log in to register as a doctor.")
            else:
                st.error("Please fill in all required fields.")

def render_doctor_search():
    """Render doctor search and listing - only for patients"""
    from components.login_auth import is_patient
    
    if not is_patient():
        st.error("❌ Access Denied: Only patients can search for doctors.")
        return
    
    st.markdown("## 🔍 Find a Doctor")
    st.markdown("Search for qualified healthcare professionals in your area.")
    
    registry = DoctorRegistry()
    
    # Search filters
    with st.expander("🔍 Search Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            specialization = st.selectbox("Specialization", [
                "All", "Cardiologist", "General Physician", "Cardiovascular Surgeon",
                "Interventional Cardiologist", "Heart Failure Specialist",
                "Electrophysiologist", "Preventive Cardiologist"
            ])
            city = st.text_input("City", placeholder="Mumbai")
        
        with col2:
            min_experience = st.number_input("Min Experience (years)", min_value=0, max_value=50, value=0)
            max_fee = st.number_input("Max Fee (₹)", min_value=0, value=2000)
        
        with col3:
            consultation_type = st.multiselect("Consultation Type", [
                "Video Consultation", "Chat Consultation", "Emergency Contact"
            ])
    
    # Apply filters
    filters = {}
    if specialization != "All":
        filters['specialization'] = specialization
    if city:
        filters['city'] = city
    if min_experience > 0:
        filters['min_experience'] = min_experience
    if max_fee > 0:
        filters['max_fee'] = max_fee
    
    # Get doctors
    doctors = registry.get_doctors(filters)
    
    if doctors:
        st.markdown(f"### Found {len(doctors)} Doctors")
        
        for doctor in doctors:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**Dr. {doctor['name']}**")
                    st.markdown(f"*{doctor['specialization']}*")
                    st.markdown(f"📍 {doctor['city']}, {doctor['state']}")
                    st.markdown(f"🏥 {doctor['location']}")
                    st.markdown(f"📞 {doctor['phone']}")
                
                with col2:
                    st.markdown(f"**₹{doctor['consultation_fee']}**")
                    # Fix the rating display to handle None values
                    rating = doctor.get('avg_rating', doctor.get('rating', 0))
                    if rating is None:
                        rating = 0.0
                    review_count = doctor.get('review_count', doctor.get('total_reviews', 0))
                    if review_count is None:
                        review_count = 0
                    st.markdown(f"⭐ {float(rating):.1f} ({int(review_count)} reviews)")
                    st.markdown(f"👨‍⚕️ {doctor['years_experience']} years exp.")
                
                with col3:
                    if st.button("👁️ View Details", key=f"view_{doctor['id']}"):
                        st.session_state.selected_doctor = doctor['id']
                        st.rerun()
                    
                    if st.button("📅 Book Consultation", key=f"book_{doctor['id']}"):
                        st.session_state.booking_doctor = doctor['id']
                        st.rerun()
                
                st.divider()
    else:
        st.info("No doctors found matching your criteria. Try adjusting your filters.")
    
    # Doctor details view
    if 'selected_doctor' in st.session_state:
        render_doctor_details(st.session_state.selected_doctor)
    
    # Booking form
    if 'booking_doctor' in st.session_state:
        render_consultation_booking(st.session_state.booking_doctor)

def render_doctor_details(doctor_id: int):
    """Render detailed doctor information"""
    st.markdown("## 👨‍⚕️ Doctor Details")
    
    registry = DoctorRegistry()
    doctor_info = registry.get_doctor_details(doctor_id)
    
    if doctor_info:
        doctor = doctor_info['doctor']
        reviews = doctor_info['reviews']
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### Dr. {doctor['name']}")
            st.markdown(f"**Specialization:** {doctor['specialization']}")
            st.markdown(f"**Experience:** {doctor['years_experience']} years")
            st.markdown(f"**Location:** {doctor['location']}")
            st.markdown(f"**Address:** {doctor['city']}, {doctor['state']}, {doctor['country']}")
            
            if doctor['bio']:
                st.markdown(f"**Bio:** {doctor['bio']}")
            
            if doctor['qualifications']:
                st.markdown(f"**Qualifications:** {doctor['qualifications']}")
            
            if doctor['languages']:
                st.markdown(f"**Languages:** {doctor['languages']}")
            
            if doctor['consultation_hours']:
                st.markdown(f"**Consultation Hours:** {doctor['consultation_hours']}")
        
        with col2:
            st.markdown(f"**Consultation Fee:** ₹{doctor['consultation_fee']}")
            # Fix the rating display to handle None values
            rating = doctor.get('rating', 0)
            if rating is None:
                rating = 0.0
            total_reviews = doctor.get('total_reviews', 0)
            if total_reviews is None:
                total_reviews = 0
            st.markdown(f"**Rating:** ⭐ {float(rating):.1f} ({int(total_reviews)} reviews)")
            
            # Contact options
            st.markdown("### Contact Options")
            if doctor['video_consultation']:
                st.success("✅ Video Consultation")
            if doctor['chat_consultation']:
                st.success("✅ Chat Consultation")
            if doctor['emergency_contact']:
                st.warning("🚨 Emergency Contact")
            
            st.markdown(f"**Phone:** {doctor['phone']}")
            st.markdown(f"**Email:** {doctor['email']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📅 Book Consultation"):
                    st.session_state.booking_doctor = doctor_id
                    st.rerun()
            with col2:
                if st.button("⭐ Add Review"):
                    st.session_state.reviewing_doctor = doctor_id
                    st.rerun()
        
        # Reviews section
        if reviews:
            st.markdown("### 📝 Patient Reviews")
            for review in reviews:
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.markdown(f"⭐ {review[3]}/5")
                    with col2:
                        st.markdown(f"**{review[8]}** - {review[6]}")
                        if review[4]:
                            st.markdown(f"*{review[4]}*")
                    st.divider()
        
        if st.button("← Back to Search"):
            if 'selected_doctor' in st.session_state:
                del st.session_state.selected_doctor
            st.rerun()

def render_consultation_booking(doctor_id: int):
    """Render consultation booking form"""
    st.markdown("## 📅 Book Consultation")
    
    registry = DoctorRegistry()
    
    # Get doctor info (simplified)
    conn = sqlite3.connect(str(registry.db_path))
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM doctors WHERE id = ?', (doctor_id,))
    doctor = cursor.fetchone()
    conn.close()
    
    if doctor:
        doctor_data = dict(zip([col[0] for col in cursor.description], doctor))
        
        st.markdown(f"**Booking consultation with Dr. {doctor_data['name']}**")
        st.markdown(f"**Specialization:** {doctor_data['specialization']}")
        st.markdown(f"**Fee:** ₹{doctor_data['consultation_fee']}")
        st.markdown(f"**Duration:** 15 minutes")
        
        with st.form("consultation_booking_form"):
            consultation_type = st.selectbox("Consultation Type", [
                "Video Consultation" if doctor_data['video_consultation'] else None,
                "Chat Consultation" if doctor_data['chat_consultation'] else None,
                "In-Person"
            ])
            
            consultation_date = st.date_input("Preferred Date", min_value=datetime.now().date())
            consultation_time = st.time_input("Preferred Time")
            notes = st.text_area("Additional Notes", placeholder="Describe your symptoms or concerns...")
            
            if st.form_submit_button("📅 Book Consultation", type="primary"):
                if consultation_type and consultation_date and consultation_time:
                    if 'user_data' in st.session_state:
                        user_data = st.session_state.user_data
                        consultation_data = {
                            'type': consultation_type,
                            'date': consultation_date,
                            'time': consultation_time,
                            'notes': notes
                        }
                        
                        result = registry.book_consultation(doctor_id, user_data['user_id'], consultation_data)
                        
                        if result['success']:
                            st.success("✅ Consultation booked successfully!")
                            if result.get('video_call_link'):
                                st.info(f"Video call link: {result['video_call_link']}")
                            st.info("The doctor will contact you to confirm the appointment.")
                            
                            if 'booking_doctor' in st.session_state:
                                del st.session_state.booking_doctor
                            st.rerun()
                        else:
                            st.error(f"❌ {result['message']}")
                    else:
                        st.error("Please log in to book a consultation.")
                else:
                    st.error("Please fill in all required fields.")
        
        if st.button("← Back to Doctor Details"):
            if 'booking_doctor' in st.session_state:
                del st.session_state.booking_doctor
            st.rerun()

def render_doctor_dashboard():
    """Render doctor dashboard for registered doctors"""
    from components.login_auth import is_doctor
    
    if not is_doctor():
        st.error("❌ Access Denied: Only doctors can access this dashboard.")
        return
    
    st.markdown("## 👨‍⚕️ Doctor Dashboard")
    
    if 'user_data' not in st.session_state:
        st.error("Please log in to access the doctor dashboard.")
        return
    
    registry = DoctorRegistry()
    
    # Check if user is a registered doctor
    conn = sqlite3.connect(str(registry.db_path))
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM doctors WHERE user_id = ?', (st.session_state.user_data['user_id'],))
    doctor = cursor.fetchone()
    
    if not doctor:
        st.info("You are not registered as a doctor. Please register first.")
        if st.button("📝 Register as Doctor"):
            st.session_state.current_page = "doctor_registration"
            st.rerun()
        return
    
    # Doctor is registered, show dashboard
    doctor_data = dict(zip([col[0] for col in cursor.description], doctor))
    
    # Get consultations
    consultations = registry.get_doctor_consultations(doctor_data['id'])
    
    # Dashboard metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Consultations", len(consultations))
    
    with col2:
        pending_consultations = len([c for c in consultations if c[6] == 'pending'])
        st.metric("Pending", pending_consultations)
    
    with col3:
        completed_consultations = len([c for c in consultations if c[6] == 'completed'])
        st.metric("Completed", completed_consultations)
    
    with col4:
        # Fix the rating display to handle None values
        rating = doctor_data.get('rating', 0)
        if rating is None:
            rating = 0.0
        st.metric("Rating", f"{float(rating):.1f} ⭐")
    
    # Recent consultations
    st.markdown("### 📅 Recent Consultations")
    
    if consultations:
        for consultation in consultations[:5]:  # Show last 5
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**Patient:** {consultation[9]}")
                    st.markdown(f"**Type:** {consultation[3]}")
                    st.markdown(f"**Date:** {consultation[4]} at {consultation[5]}")
                    if consultation[8]:  # video_call_link
                        st.markdown(f"**Video Call:** {consultation[8]}")
                
                with col2:
                    status_color = {
                        'pending': '🟡',
                        'confirmed': '🟢',
                        'completed': '🔵',
                        'cancelled': '🔴'
                    }.get(consultation[6], '⚪')
                    st.markdown(f"{status_color} {consultation[6].title()}")
                
                with col3:
                    if consultation[6] == 'pending':
                        if st.button("✅ Confirm", key=f"confirm_{consultation[0]}"):
                            result = registry.update_consultation_status(consultation[0], 'confirmed')
                            if result['success']:
                                st.success("Consultation confirmed!")
                                st.rerun()
                
                with col4:
                    if st.button("💬 Chat", key=f"chat_{consultation[0]}"):
                        st.session_state.chat_consultation = consultation[0]
                        st.rerun()
                
                st.divider()
    else:
        st.info("No consultations yet.")
    
    # Chat interface
    if 'chat_consultation' in st.session_state:
        render_chat_interface(st.session_state.chat_consultation)

def render_chat_interface(consultation_id: int):
    """Render chat interface for consultation"""
    st.markdown("## 💬 Consultation Chat")
    
    registry = DoctorRegistry()
    
    # Get consultation details
    conn = sqlite3.connect(str(registry.db_path))
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, d.name as doctor_name, c.patient_id, c.video_call_link
        FROM consultations c
        JOIN doctors d ON c.doctor_id = d.id
        WHERE c.id = ?
    ''', (consultation_id,))
    consultation = cursor.fetchone()
    conn.close()
    
    patient_name = "Unknown Patient"
    video_call_link = None
    if consultation:
        # Fetch patient name from users.db
        patient_id = consultation[-2]
        video_call_link = consultation[-1]
        users_conn = sqlite3.connect("data/users.db")
        users_cursor = users_conn.cursor()
        users_cursor.execute('SELECT username FROM users WHERE id = ?', (patient_id,))
        user_result = users_cursor.fetchone()
        if user_result:
            patient_name = user_result[0]
        users_conn.close()
        st.markdown(f"**Chat with {consultation[-3]} (Patient: {patient_name})**")
        
        # Video call section
        if not video_call_link:
            if st.button("🎥 Start Video Call"):
                import secrets
                video_call_link = f"https://meet.jit.si/heartcare-{secrets.token_urlsafe(8)}"
                # Save the link to the consultation
                conn = sqlite3.connect(str(registry.db_path))
                cursor = conn.cursor()
                cursor.execute('UPDATE consultations SET video_call_link = ? WHERE id = ?', (video_call_link, consultation_id))
                conn.commit()
                conn.close()
                st.session_state.video_call_link = video_call_link
                st.success("Video call link generated!")
                st.rerun()
        else:
            st.markdown(f"**Video Call Link:** [Join Video Call]({video_call_link})")
            st.info("Share this link with the other participant to join the call.")
        
        # Get chat messages
        messages = registry.get_chat_messages(consultation_id)
        
        # Display messages
        st.markdown("### Messages")
        for message in messages:
            sender_type = message[3]
            message_text = message[4]
            timestamp = message[5]
            
            if sender_type == 'doctor':
                st.markdown(f"**👨‍⚕️ Doctor:** {message_text}")
            else:
                st.markdown(f"**👤 Patient:** {message_text}")
            st.caption(f"Sent at {timestamp}")
            st.divider()
        
        # Send message
        with st.form("send_message_form"):
            message = st.text_area("Type your message...")
            if st.form_submit_button("📤 Send Message"):
                if message:
                    sender_id = st.session_state.user_data['user_id']
                    sender_type = 'doctor' if is_doctor() else 'patient'
                    
                    result = registry.send_chat_message(consultation_id, sender_id, sender_type, message)
                    if result['success']:
                        st.success("Message sent!")
                        st.rerun()
                    else:
                        st.error(f"Failed to send message: {result['message']}")
        
        if st.button("← Back to Dashboard"):
            if 'chat_consultation' in st.session_state:
                del st.session_state.chat_consultation
            st.rerun()

def render_patient_dashboard():
    """Render patient dashboard"""
    from components.login_auth import is_patient
    
    if not is_patient():
        st.error("❌ Access Denied: Only patients can access this dashboard.")
        return
    
    st.markdown("## 👤 Patient Dashboard")
    
    if 'user_data' not in st.session_state:
        st.error("Please log in to access the patient dashboard.")
        return
    
    registry = DoctorRegistry()
    
    # Get patient consultations
    consultations = registry.get_patient_consultations(st.session_state.user_data['user_id'])
    
    # Dashboard metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Consultations", len(consultations))
    
    with col2:
        upcoming_consultations = len([c for c in consultations if c[6] in ['pending', 'confirmed']])
        st.metric("Upcoming", upcoming_consultations)
    
    with col3:
        completed_consultations = len([c for c in consultations if c[6] == 'completed'])
        st.metric("Completed", completed_consultations)
    
    # Recent consultations
    st.markdown("### 📅 My Consultations")
    
    if consultations:
        for consultation in consultations[:5]:  # Show last 5
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**Doctor:** Dr. {consultation[9]}")
                    st.markdown(f"**Specialization:** {consultation[10]}")
                    st.markdown(f"**Type:** {consultation[3]}")
                    st.markdown(f"**Date:** {consultation[4]} at {consultation[5]}")
                
                with col2:
                    status_color = {
                        'pending': '🟡',
                        'confirmed': '🟢',
                        'completed': '🔵',
                        'cancelled': '🔴'
                    }.get(consultation[6], '⚪')
                    st.markdown(f"{status_color} {consultation[6].title()}")
                
                with col3:
                    if consultation[8]:  # video_call_link
                        st.markdown(f"**Video Call:** {consultation[8]}")
                
                with col4:
                    if st.button("💬 Chat", key=f"chat_{consultation[0]}"):
                        st.session_state.chat_consultation = consultation[0]
                        st.rerun()
                
                st.divider()
    else:
        st.info("No consultations yet. Book your first consultation!")
    
    # Chat interface
    if 'chat_consultation' in st.session_state:
        render_chat_interface(st.session_state.chat_consultation)

# Helper function to get user data (import from login_auth)
def get_user_data():
    """Get current user data - placeholder"""
    if 'user_data' in st.session_state:
        return st.session_state.user_data
    return None 