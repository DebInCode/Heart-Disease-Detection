import streamlit as st
import os
from pathlib import Path
import sys
import json
from datetime import datetime
import pandas as pd
import sqlite3

# Add the project root to the Python path for imports
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import authentication system
from components.login_auth import render_login_page, check_authentication, logout_user, is_doctor, is_patient

# Import new features
try:
    from components.doctor_registry import render_doctor_registration, render_doctor_search, render_doctor_details
    DOCTOR_REGISTRY_AVAILABLE = True
except ImportError:
    DOCTOR_REGISTRY_AVAILABLE = False

try:
    from reports.pdf_generator import render_pdf_generator
    PDF_GENERATOR_AVAILABLE = True
except ImportError:
    PDF_GENERATOR_AVAILABLE = False

# Import prediction module
try:
    from utils.predict import HeartDiseasePredictor
    PREDICTOR_AVAILABLE = True
except ImportError as e:
    PREDICTOR_AVAILABLE = False
    print(f"Predictor not available: {e}")

def main():
    """
    Main entry point for the Heart Disease Prediction Streamlit application.
    Unified application with modern UI, header, footer, and all features.
    """
    
    # Page configuration
    st.set_page_config(
        page_title="Heart Disease Detector - AI-Powered Cardiovascular Risk Assessment",
        page_icon="❤️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # If not authenticated, show login page and stop
    if not check_authentication():
        render_login_page()
        st.stop()
    
    # Custom CSS for modern UI
    st.markdown("""
        <style>
        /* Modern CSS Reset and Base Styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        /* Header Styles - Fixed positioning */
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            width: 100%;
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }
        
        .logo-section {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .logo-text {
            font-size: 1.5rem;
            font-weight: bold;
        }
        
        .nav-menu {
            display: flex;
            gap: 2rem;
            list-style: none;
            align-items: center;
        }
        
        .nav-menu a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: background-color 0.3s;
        }
        
        .nav-menu a:hover {
            background-color: rgba(255,255,255,0.1);
        }
        
        .profile-icon {
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .profile-icon:hover {
            background: rgba(255,255,255,0.3);
        }
        
        /* Main Content Styles - Add top margin to avoid header overlap */
        .main-content {
            min-height: calc(100vh - 200px);
            padding: 2rem;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            margin-top: 80px; /* Space for fixed header */
        }
        
        .hero-section {
            text-align: center;
            padding: 4rem 2rem;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 3rem;
        }
        
        .hero-title {
            font-size: 3rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        
        .hero-subtitle {
            font-size: 1.2rem;
            color: #7f8c8d;
            margin-bottom: 2rem;
        }
        
        .cta-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .cta-button {
            padding: 1rem 2rem;
            border: none;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        
        .cta-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .cta-secondary {
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
        }
        
        .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        /* Feature Cards */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin: 3rem 0;
        }
        
        .feature-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .feature-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        
        .feature-description {
            color: #7f8c8d;
            line-height: 1.6;
        }
        
        /* Footer Styles */
        .footer {
            background: #2c3e50;
            color: white;
            padding: 3rem 0 1rem;
            margin-top: 4rem;
        }
        
        .footer-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
        }
        
        .footer-section h3 {
            margin-bottom: 1rem;
            color: #3498db;
        }
        
        .footer-section p, .footer-section a {
            color: #bdc3c7;
            text-decoration: none;
            line-height: 1.6;
        }
        
        .footer-section a:hover {
            color: #3498db;
        }
        
        .footer-bottom {
            text-align: center;
            padding-top: 2rem;
            border-top: 1px solid #34495e;
            margin-top: 2rem;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                gap: 1rem;
            }
            
            .nav-menu {
                flex-direction: column;
                gap: 0.5rem;
            }
            
            .hero-title {
                font-size: 2rem;
            }
            
            .cta-buttons {
                flex-direction: column;
                align-items: center;
            }
            
            .main-content {
                margin-top: 120px; /* More space for mobile header */
            }
        }
        
        /* Streamlit Specific Overrides */
        .main .block-container {
            padding: 0;
            max-width: none;
            margin-top: 80px; /* Space for fixed header */
        }
        
        /* Prevent page scrolling on load */
        .stApp {
            margin-top: 0;
        }
        
        /* Ensure content starts at the top after header */
        .main .block-container > div:first-child {
            margin-top: 0;
        }
        
        .stButton > button {
            border-radius: 50px;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        /* Hide Streamlit's default header */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    if "user_mode" not in st.session_state:
        st.session_state.user_mode = None
    
    # Render Header
    render_header()
    
    # Render Main Content based on current page
    if st.session_state.current_page == "home":
        render_home_page()
    elif st.session_state.current_page == "patient":
        render_patient_page()
    elif st.session_state.current_page == "doctor":
        render_doctor_page()
    elif st.session_state.current_page == "doctor_search" and DOCTOR_REGISTRY_AVAILABLE and is_patient():
        render_doctor_search()
    elif st.session_state.current_page == "doctor_registration" and DOCTOR_REGISTRY_AVAILABLE and is_doctor():
        render_doctor_registration()
    elif st.session_state.current_page == "pdf_generator" and PDF_GENERATOR_AVAILABLE:
        render_pdf_generator()
    elif st.session_state.current_page == "about":
        render_about_page()
    elif st.session_state.current_page == "profile":
        render_profile_page()
        return
    
    # Chat interface
    if 'chat_consultation' in st.session_state:
        from components.chatbot import render_chat_interface
        render_chat_interface(st.session_state.chat_consultation)
        return
    
    # Render Footer
    render_footer()

def render_header():
    """Render the modern header with role-based navigation"""
    st.markdown("""
        <div class="header">
            <div class="header-content">
                <div class="logo-section">
                    <span style="font-size: 2rem;">❤️</span>
                    <span class="logo-text">HeartCare Pro</span>
                </div>
                <nav>
                    <ul class="nav-menu">
                        <li><a href="#" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'home'}, '*')">Home</a></li>
                        <li><a href="#" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'patient'}, '*')">Patient Mode</a></li>
                        <li><a href="#" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'doctor'}, '*')">Doctor Mode</a></li>
                        <li><a href="#" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'about'}, '*')">About</a></li>
                    </ul>
                </nav>
                <div class="profile-icon" title="Profile" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'profile'}, '*')">👤</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Role-based navigation buttons
    user_role = "doctor" if is_doctor() else "patient"
    
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
    
    with col1:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = "home"
            st.rerun()
    
    with col2:
        if st.button("👤 Patient", use_container_width=True):
            st.session_state.current_page = "patient"
            st.rerun()
    
    with col3:
        if st.button("👨‍⚕️ Doctor", use_container_width=True):
            st.session_state.current_page = "doctor"
            st.rerun()
    
    with col4:
        # Show "Find Doctors" only for patients
        if is_patient():
            if st.button("🔍 Find Doctors", use_container_width=True):
                if DOCTOR_REGISTRY_AVAILABLE:
                    st.session_state.current_page = "doctor_search"
                    st.rerun()
                else:
                    st.error("Doctor registry feature not available")
        else:
            # Show "My Profile" for registered doctors, "Register" for unregistered doctors
            if DOCTOR_REGISTRY_AVAILABLE:
                from components.doctor_registry import DoctorRegistry
                registry = DoctorRegistry()
                
                # Check if user is a registered doctor
                if 'user_data' in st.session_state:
                    conn = sqlite3.connect(str(registry.db_path))
                    cursor = conn.cursor()
                    cursor.execute('SELECT id FROM doctors WHERE user_id = ?', (st.session_state.user_data['user_id'],))
                    doctor = cursor.fetchone()
                    conn.close()
                    
                    if doctor:
                        # Doctor is registered, show "My Profile"
                        if st.button("👤 My Profile", use_container_width=True):
                            st.session_state.current_page = "doctor"
                            st.rerun()
                    else:
                        # Doctor is not registered, show "Register"
                        if st.button("📝 Register", use_container_width=True):
                            st.session_state.current_page = "doctor_registration"
                            st.rerun()
                else:
                    if st.button("📝 Register", use_container_width=True):
                        st.session_state.current_page = "doctor_registration"
                        st.rerun()
            else:
                st.error("Doctor registry feature not available")
    
    with col5:
        if st.button("📄 Reports", use_container_width=True):
            if PDF_GENERATOR_AVAILABLE:
                st.session_state.current_page = "pdf_generator"
                st.rerun()
            else:
                st.error("PDF generator feature not available")
    
    with col6:
        if st.button("ℹ️ About", use_container_width=True):
            st.session_state.current_page = "about"
            st.rerun()

def render_home_page():
    """Render the home page with welcome message and features"""
    st.markdown("## 🏠 Welcome to Heart Disease Detector")
    st.markdown("AI-powered heart disease risk assessment and healthcare platform.")
    
    # Feature overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔍 Key Features")
        st.markdown("""
        - **AI Risk Assessment**: Get instant heart disease risk predictions
        - **Doctor Directory**: Find qualified healthcare professionals
        - **Consultation Booking**: Schedule appointments with doctors
        - **Chat Support**: Real-time communication with healthcare providers
        - **PDF Reports**: Generate detailed health reports
        - **Batch Analysis**: Professional tools for healthcare providers
        """)
    
    with col2:
        st.markdown("### 👥 For Different Users")
        st.markdown("""
        **👤 Patients:**
        - Heart disease risk assessment
        - Find and book doctors
        - Chat with healthcare providers
        - Generate health reports
        
        **👨‍⚕️ Doctors:**
        - Patient consultation management
        - Batch patient analysis
        - Professional profile registration
        - Patient communication tools
        """)
    
    # AI Chatbot
    st.markdown("### 🤖 AI Health Assistant")
    from components.chatbot import render_ai_chatbot
    render_ai_chatbot()

def render_patient_page():
    """Render the patient dashboard and assessment page"""
    from components.login_auth import is_patient
    
    if not is_patient():
        st.error("❌ Access Denied: Only patients can access this page.")
        return
    
    st.markdown("## 👤 Patient Dashboard")
    
    # Patient dashboard tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Heart Assessment", "📅 My Consultations", "👨‍⚕️ Find Doctors"])
    
    with tab1:
        render_heart_assessment()
    
    with tab2:
        render_patient_consultations()
    
    with tab3:
        if DOCTOR_REGISTRY_AVAILABLE:
            render_doctor_search()
        else:
            st.error("Doctor registry feature not available")

def render_heart_assessment():
    """Render the heart disease assessment form"""
    st.markdown("### 🔍 Heart Disease Assessment")
    st.markdown("Enter your medical information to get an AI-powered risk assessment.")
    
    if not PREDICTOR_AVAILABLE:
        st.error("❌ Prediction model not available. Please ensure the model files are present.")
        return
    
    # Initialize predictor
    try:
        predictor = HeartDiseasePredictor()
        st.success("✅ AI Model loaded successfully!")
    except Exception as e:
        st.error(f"❌ Error loading AI model: {str(e)}")
        return
    
    # Patient information form
    with st.form("patient_assessment"):
        st.markdown("### Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.slider("Age", 18, 100, 45, help="Your current age")
            sex = st.selectbox("Sex", ["Male", "Female"], help="Your biological sex")
            chest_pain = st.selectbox("Chest Pain Type", 
                ["Typical Angina", "Atypical Angina", "Non-anginal Pain", "Asymptomatic"],
                help="Type of chest pain if experienced")
        
        with col2:
            resting_bp = st.slider("Resting Blood Pressure (mm Hg)", 90, 200, 130, help="Systolic blood pressure")
            cholesterol = st.slider("Cholesterol (mg/dl)", 100, 600, 200, help="Total cholesterol level")
            fasting_bs = st.selectbox("Fasting Blood Sugar > 120 mg/dl", ["No", "Yes"], help="High fasting blood sugar")
        
        st.markdown("### Medical Information")
        col1, col2 = st.columns(2)
        
        with col1:
            resting_ecg = st.selectbox("Resting ECG Results", 
                ["Normal", "ST-T Wave Abnormality", "Left Ventricular Hypertrophy"],
                help="Results of resting electrocardiogram")
            max_hr = st.slider("Maximum Heart Rate", 60, 202, 150, help="Maximum heart rate achieved")
        
        with col2:
            exercise_angina = st.selectbox("Exercise-Induced Angina", ["No", "Yes"], help="Chest pain during exercise")
            st_depression = st.slider("ST Depression", 0.0, 6.2, 0.0, step=0.1, help="ST depression induced by exercise")
        
        # Additional required fields for the model
        st.markdown("### Additional Medical Parameters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            slope = st.selectbox("Slope of Peak Exercise ST Segment", 
                ["Upsloping", "Flat", "Downsloping"], help="Slope of the peak exercise ST segment")
            ca = st.slider("Number of Major Vessels", 0, 4, 0, help="Number of major vessels colored by fluoroscopy")
        
        with col2:
            thal = st.selectbox("Thalassemia", 
                ["Normal", "Fixed Defect", "Reversable Defect"], help="Thalassemia type")
        
        # Submit button
        submitted = st.form_submit_button("🔍 Get Risk Assessment", type="primary")
    
    # Process the form data when submitted
    if submitted:
        # Process the form data
        with st.spinner("🤖 AI is analyzing your data..."):
            try:
                # Convert form data to prediction format
                input_data = {
                    'age': age,
                    'sex': 1 if sex == "Male" else 0,
                    'cp': ["Typical Angina", "Atypical Angina", "Non-anginal Pain", "Asymptomatic"].index(chest_pain),
                    'trestbps': resting_bp,
                    'chol': cholesterol,
                    'fbs': 1 if fasting_bs == "Yes" else 0,
                    'restecg': ["Normal", "ST-T Wave Abnormality", "Left Ventricular Hypertrophy"].index(resting_ecg),
                    'thalach': max_hr,
                    'exang': 1 if exercise_angina == "Yes" else 0,
                    'oldpeak': st_depression,
                    'slope': ["Upsloping", "Flat", "Downsloping"].index(slope),
                    'ca': ca,
                    'thal': ["Normal", "Fixed Defect", "Reversable Defect"].index(thal)
                }
                
                # Get prediction using the correct method name
                prediction, probability = predictor.predict_heart_disease(input_data)
                
                if prediction is None:
                    st.error("❌ Error during prediction. Please check your input data.")
                    return
                
                # Get risk level and explanation
                risk_level = predictor.get_risk_level(probability)
                explanation = predictor.get_prediction_explanation(input_data)
                
                # Display results
                st.markdown("## 📊 Assessment Results")
                
                # Risk level display
                if "Low" in risk_level:
                    st.success(f"🟢 **Risk Level: {risk_level}**")
                elif "Moderate" in risk_level:
                    st.warning(f"🟡 **Risk Level: {risk_level}**")
                elif "High" in risk_level:
                    st.error(f"🔴 **Risk Level: {risk_level}**")
                else:
                    st.error(f"🔴 **Risk Level: {risk_level}**")
                
                # Probability gauge
                st.markdown(f"**Risk Probability: {probability:.1%}**")
                st.progress(probability)
                
                # Prediction result
                if prediction == 1:
                    st.error("🔴 **Result: Heart Disease Risk Detected**")
                else:
                    st.success("🟢 **Result: No Heart Disease Risk Detected**")
                
                # Detailed explanation
                with st.expander("📋 Detailed Analysis", expanded=True):
                    st.markdown(f"""
                    **Prediction Details:**
                    - **Prediction**: {'Heart Disease Detected' if prediction == 1 else 'No Heart Disease Detected'}
                    - **Probability**: {probability:.1%}
                    - **Risk Level**: {risk_level}
                    - **Interpretation**: {explanation.get('interpretation', 'N/A')}
                    """)
                    
                    # Show top features if available
                    if 'top_features' in explanation:
                        st.markdown("**Most Important Factors:**")
                        for feature, importance in explanation['top_features'].items():
                            st.markdown(f"- {feature}: {importance:.3f}")
                
                # Recommendations
                st.markdown("## 💡 Recommendations")
                if "Low" in risk_level:
                    st.info("""
                    **Keep up the good work!** 
                    - Continue maintaining a healthy lifestyle
                    - Regular check-ups with your doctor
                    - Monitor your health metrics regularly
                    """)
                elif "Moderate" in risk_level:
                    st.warning("""
                    **Moderate risk detected. Consider:**
                    - Consulting with a healthcare provider
                    - Lifestyle modifications (diet, exercise)
                    - Regular monitoring of heart health
                    - Stress management techniques
                    """)
                else:
                    st.error("""
                    **High risk detected. Please:**
                    - **Immediately consult a healthcare provider**
                    - Consider lifestyle changes
                    - Regular medical monitoring
                    - Follow medical advice strictly
                    """)
                
                # Save to session state
                st.session_state.last_prediction = {
                    'input_data': input_data,
                    'prediction': prediction,
                    'probability': probability,
                    'risk_level': risk_level,
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                st.error(f"❌ Error during prediction: {str(e)}")
                st.error("Please ensure all required fields are filled correctly.")
    
    # Action buttons (show only when there's a prediction result)
    if 'last_prediction' in st.session_state:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📄 Generate Report", type="primary"):
                if PDF_GENERATOR_AVAILABLE:
                    st.session_state.current_page = "pdf_generator"
                    st.rerun()
                else:
                    st.error("PDF generator not available")
        with col2:
            if st.button("👨‍⚕️ Find Doctors"):
                if DOCTOR_REGISTRY_AVAILABLE:
                    st.session_state.current_page = "doctor_search"
                    st.rerun()
                else:
                    st.error("Doctor registry not available")
        with col3:
            if st.button("🔄 New Assessment"):
                st.rerun()

def render_patient_consultations():
    """Render patient's consultation history"""
    st.markdown("### 📅 My Consultations")
    
    if 'user_data' not in st.session_state:
        st.error("Please log in to view your consultations.")
        return
    
    if DOCTOR_REGISTRY_AVAILABLE:
        from components.doctor_registry import DoctorRegistry
        registry = DoctorRegistry()
        
        # Get patient consultations
        consultations = registry.get_patient_consultations(st.session_state.user_data['user_id'])
        
        if consultations:
            for consultation in consultations:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        # consultation[9] is doctor_name, consultation[10] is specialization
                        doctor_name = consultation[9] if len(consultation) > 9 else "Unknown Doctor"
                        specialization = consultation[10] if len(consultation) > 10 else "Unknown"
                        st.markdown(f"**Doctor:** Dr. {doctor_name}")
                        st.markdown(f"**Specialization:** {specialization}")
                        st.markdown(f"**Type:** {consultation[3]}")
                        st.markdown(f"**Date:** {consultation[4]} at {consultation[5]}")
                        if len(consultation) > 8 and consultation[8]:  # video_call_link
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
                            st.info("Waiting for doctor confirmation")
                        elif consultation[6] == 'confirmed':
                            st.success("✅ Confirmed")
                        elif consultation[6] == 'completed':
                            st.info("✅ Completed")
                    
                    with col4:
                        if st.button("💬 Chat", key=f"chat_{consultation[0]}"):
                            st.session_state.chat_consultation = consultation[0]
                            st.rerun()
                    
                    st.divider()
        else:
            st.info("No consultations yet. Book your first consultation!")
    else:
        st.error("Doctor registry feature not available")

def render_doctor_page():
    """Render the doctor dashboard"""
    from components.login_auth import is_doctor
    
    if not is_doctor():
        st.error("❌ Access Denied: Only doctors can access this page.")
        return
    
    st.markdown("## 👨‍⚕️ Doctor Dashboard")
    
    # Check if user is a registered doctor
    is_registered = False
    if DOCTOR_REGISTRY_AVAILABLE and 'user_data' in st.session_state:
        from components.doctor_registry import DoctorRegistry
        registry = DoctorRegistry()
        conn = sqlite3.connect(str(registry.db_path))
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM doctors WHERE user_id = ?', (st.session_state.user_data['user_id'],))
        doctor = cursor.fetchone()
        conn.close()
        is_registered = doctor is not None
    
    if is_registered:
        # Doctor is registered, show full dashboard
        tab1, tab2, tab3, tab4 = st.tabs(["👤 My Profile", "📊 Patient Consultations", "👨‍⚕️ Doctor Directory", "🔬 Batch Analysis"])
        
        with tab1:
            render_doctor_profile()
        
        with tab2:
            render_doctor_consultations()
        
        with tab3:
            if DOCTOR_REGISTRY_AVAILABLE:
                render_doctor_directory()
            else:
                st.error("Doctor registry feature not available")
        
        with tab4:
            render_batch_analysis()
    else:
        # Doctor is not registered, show registration tab
        tab1, tab2 = st.tabs(["📝 Register Profile", "🔬 Batch Analysis"])
        
        with tab1:
            if DOCTOR_REGISTRY_AVAILABLE:
                render_doctor_registration()
            else:
                st.error("Doctor registry feature not available")
        
        with tab2:
            render_batch_analysis()

def render_doctor_profile():
    """Render doctor's own profile information"""
    st.markdown("### 👤 My Doctor Profile")
    
    if 'user_data' not in st.session_state:
        st.error("Please log in to view your profile.")
        return
    
    if DOCTOR_REGISTRY_AVAILABLE:
        from components.doctor_registry import DoctorRegistry
        registry = DoctorRegistry()
        
        # Check if user is a registered doctor
        conn = sqlite3.connect(str(registry.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM doctors WHERE user_id = ?', (st.session_state.user_data['user_id'],))
        doctor = cursor.fetchone()
        
        if not doctor:
            st.info("You are not registered as a doctor. Please register your profile first.")
            if st.button("📝 Register as Doctor"):
                st.session_state.current_page = "doctor_registration"
                st.rerun()
            return
        
        # Doctor is registered, show profile
        doctor_data = dict(zip([col[0] for col in cursor.description], doctor))
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### Dr. {doctor_data['name']}")
            st.markdown(f"**Specialization:** {doctor_data['specialization']}")
            st.markdown(f"**Experience:** {doctor_data['years_experience']} years")
            st.markdown(f"**Location:** {doctor_data['location']}")
            st.markdown(f"**Address:** {doctor_data['city']}, {doctor_data['state']}, {doctor_data['country']}")
            
            if doctor_data['bio']:
                st.markdown(f"**Bio:** {doctor_data['bio']}")
            
            if doctor_data['qualifications']:
                st.markdown(f"**Qualifications:** {doctor_data['qualifications']}")
            
            if doctor_data['languages']:
                st.markdown(f"**Languages:** {doctor_data['languages']}")
            
            if doctor_data['consultation_hours']:
                st.markdown(f"**Consultation Hours:** {doctor_data['consultation_hours']}")
        
        with col2:
            st.markdown(f"**Consultation Fee:** ₹{doctor_data['consultation_fee']}")
            st.markdown(f"**Rating:** ⭐ {doctor_data['rating']:.1f} ({doctor_data['total_reviews']} reviews)")
            
            # Contact options
            st.markdown("### Contact Options")
            if doctor_data['video_consultation']:
                st.success("✅ Video Consultation")
            if doctor_data['chat_consultation']:
                st.success("✅ Chat Consultation")
            if doctor_data['emergency_contact']:
                st.warning("🚨 Emergency Contact")
            
            st.markdown(f"**Phone:** {doctor_data['phone']}")
            st.markdown(f"**Email:** {doctor_data['email']}")
            
            if st.button("✏️ Edit Profile"):
                st.session_state.current_page = "doctor_registration"
                st.rerun()
        
        # Get consultations for this doctor
        consultations = registry.get_doctor_consultations(doctor_data['id'])
        
        st.markdown("### 📊 Profile Statistics")
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
            st.metric("Rating", f"{doctor_data['rating']:.1f} ⭐")
        
        conn.close()
    else:
        st.error("Doctor registry feature not available")

def render_doctor_consultations():
    """Render doctor's consultation management"""
    st.markdown("### 📊 Patient Consultations")
    
    if 'user_data' not in st.session_state:
        st.error("Please log in to view consultations.")
        return
    
    if DOCTOR_REGISTRY_AVAILABLE:
        from components.doctor_registry import DoctorRegistry
        registry = DoctorRegistry()
        
        # Check if user is a registered doctor
        conn = sqlite3.connect(str(registry.db_path))
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM doctors WHERE user_id = ?', (st.session_state.user_data['user_id'],))
        doctor_result = cursor.fetchone()
        
        if not doctor_result:
            st.info("You are not registered as a doctor. Please register your profile first.")
            return
        
        doctor_id = doctor_result[0]
        
        # Get consultations
        consultations = registry.get_doctor_consultations(doctor_id)
        
        if consultations:
            for consultation in consultations:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        # consultation[9] is patient_name, consultation[10] is patient_email
                        patient_name = consultation[9] if len(consultation) > 9 else "Unknown Patient"
                        st.markdown(f"**Patient:** {patient_name}")
                        st.markdown(f"**Type:** {consultation[3]}")
                        st.markdown(f"**Date:** {consultation[4]} at {consultation[5]}")
                        if len(consultation) > 8 and consultation[8]:  # video_call_link
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
        
        conn.close()
    else:
        st.error("Doctor registry feature not available")

def render_batch_analysis():
    """Render batch analysis for doctors"""
    st.markdown("### 🔬 Batch Patient Analysis")
    st.markdown("Upload CSV file with patient data for batch analysis.")
    
    uploaded_file = st.file_uploader("Upload CSV file with patient data", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(df)} patient records")
            st.dataframe(df.head())
            
            if st.button("🔍 Analyze All Patients", type="primary"):
                if PREDICTOR_AVAILABLE:
                    predictor = HeartDiseasePredictor()
                    with st.spinner("Processing patient data..."):
                        # Process batch predictions
                        results = []
                        for idx, row in df.iterrows():
                            try:
                                prediction, probability = predictor.predict_heart_disease(row.to_dict())
                                if prediction is not None:
                                    risk_level = predictor.get_risk_level(probability)
                                    results.append({
                                        'Patient_ID': idx + 1,
                                        'Prediction': prediction,
                                        'Probability': probability,
                                        'Risk_Level': risk_level
                                    })
                                else:
                                    results.append({
                                        'Patient_ID': idx + 1,
                                        'Prediction': 'Error',
                                        'Probability': 0,
                                        'Risk_Level': 'Error'
                                    })
                            except Exception as e:
                                results.append({
                                    'Patient_ID': idx + 1,
                                    'Prediction': 'Error',
                                    'Probability': 0,
                                    'Risk_Level': 'Error'
                                })
                        
                        results_df = pd.DataFrame(results)
                        st.markdown("### 📈 Batch Analysis Results")
                        st.dataframe(results_df)
                        
                        # Download results
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results",
                            data=csv,
                            file_name="heart_disease_batch_results.csv",
                            mime="text/csv"
                        )
                else:
                    st.error("❌ Prediction model not available")
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")

def render_about_page():
    """Render the about page"""
    st.markdown("## ℹ️ About Heart Disease Detector")
    
    st.markdown("""
    ### 🎯 Our Mission
    We are committed to providing accessible, AI-powered cardiovascular health assessment tools 
    to help individuals and healthcare professionals make informed decisions about heart health.
    
    ### 🤖 Technology
    - **Machine Learning**: Advanced algorithms trained on extensive medical datasets
    - **Data Science**: Rigorous analysis and validation of prediction models
    - **User Experience**: Intuitive interface designed for both patients and professionals
    
    ### 📊 Model Information
    - **Dataset**: UCI Heart Disease Dataset
    - **Algorithm**: Random Forest Classifier
    - **Accuracy**: High-performance model with comprehensive validation
    - **Features**: 13 clinical parameters for comprehensive assessment
    
    ### 🔒 Privacy & Security
    - Your health data is processed locally
    - No personal information is stored permanently
    - Industry-standard security practices
    - HIPAA-compliant data handling
    
    ### ⚠️ Important Notice
    This application is designed for educational and screening purposes only. 
    It is not a substitute for professional medical advice, diagnosis, or treatment. 
    Always consult with qualified healthcare professionals for medical decisions.
    """)
    
    # Contact information
    st.markdown("### 📞 Contact & Support")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Technical Support**  
        Email: chanddeblina@gmail.com  
        Phone: +1-800-HEART-HELP
        """)
    with col2:
        st.markdown("""
        **Medical Inquiries**  
        Please consult with your healthcare provider  
        for medical questions and concerns.
        """)

def render_footer():
    """Render the modern footer"""
    st.markdown("""
        <div class="footer">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>Heart Disease Detector</h3>
                    <p>AI-powered cardiovascular health assessment platform designed to help individuals and healthcare professionals make informed decisions about heart health.</p>
                </div>
                <div class="footer-section">
                    <h3>Quick Links</h3>
                    <p><a href="#">Home</a></p>
                    <p><a href="#">Patient Assessment</a></p>
                    <p><a href="#">Doctor Mode</a></p>
                    <p><a href="#">Find Doctors</a></p>
                    <p><a href="#">Generate Reports</a></p>
                    <p><a href="#">About</a></p>
                </div>
                <div class="footer-section">
                    <h3>Resources</h3>
                    <p><a href="#">Health Guidelines</a></p>
                    <p><a href="#">Research Papers</a></p>
                    <p><a href="#">Medical References</a></p>
                    <p><a href="#">FAQ</a></p>
                </div>
                <div class="footer-section">
                    <h3>Legal</h3>
                    <p><a href="#">Privacy Policy</a></p>
                    <p><a href="#">Terms of Service</a></p>
                    <p><a href="#">Medical Disclaimer</a></p>
                    <p><a href="#">Cookie Policy</a></p>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2024 Heart Disease Detector. All rights reserved. | Made with ❤️ for better heart health</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_doctor_directory():
    """Render doctor directory for doctors to see other doctors"""
    st.markdown("### 👨‍⚕️ Doctor Directory")
    st.markdown("View other healthcare professionals in the network.")
    
    if DOCTOR_REGISTRY_AVAILABLE:
        from components.doctor_registry import DoctorRegistry
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
        
        # Get doctors (exclude current doctor)
        all_doctors = registry.get_doctors(filters)
        if 'user_data' in st.session_state:
            current_user_id = st.session_state.user_data['user_id']
            doctors = [d for d in all_doctors if d.get('user_id') != current_user_id]
        else:
            doctors = all_doctors
        
        if doctors:
            st.markdown(f"### Found {len(doctors)} Other Doctors")
            
            for i, doctor in enumerate(doctors):
                with st.container():
                    # Create a unique key for each doctor
                    doctor_key = f"doctor_{doctor['id']}"
                    
                    # Show basic info initially
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"**Dr. {doctor['name']}**")
                        st.markdown(f"*{doctor['specialization']}*")
                    
                    with col2:
                        st.markdown(f"👨‍⚕️ {doctor['years_experience']} years")
                    
                    with col3:
                        st.markdown(f"📍 {doctor['city']}")
                    
                    with col4:
                        if st.button("👁️ Details", key=f"details_{doctor_key}"):
                            if 'expanded_doctor' in st.session_state and st.session_state.expanded_doctor == doctor['id']:
                                st.session_state.expanded_doctor = None
                            else:
                                st.session_state.expanded_doctor = doctor['id']
                            st.rerun()
                    
                    # Show expanded details if this doctor is selected
                    if 'expanded_doctor' in st.session_state and st.session_state.expanded_doctor == doctor['id']:
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📋 Professional Details**")
                            st.markdown(f"🏥 **Hospital/Clinic:** {doctor['location']}")
                            st.markdown(f"📞 **Phone:** {doctor['phone']}")
                            st.markdown(f"📧 **Email:** {doctor['email']}")
                            st.markdown(f"💰 **Consultation Fee:** ₹{doctor['consultation_fee']}")
                            st.markdown(f"🌍 **Location:** {doctor['city']}, {doctor['state']}, {doctor['country']}")
                        
                        with col2:
                            st.markdown("**⭐ Ratings & Reviews**")
                            rating = doctor.get('avg_rating', doctor.get('rating', 0))
                            if rating is None:
                                rating = 0.0
                            review_count = doctor.get('review_count', doctor.get('total_reviews', 0))
                            if review_count is None:
                                review_count = 0
                            st.markdown(f"⭐ **Rating:** {float(rating):.1f}/5.0")
                            st.markdown(f"📝 **Reviews:** {int(review_count)}")
                            
                            if doctor.get('bio'):
                                st.markdown("**📖 Bio:**")
                                st.markdown(f"_{doctor['bio']}_")
                        
                        # Additional details
                        if doctor.get('qualifications') or doctor.get('languages'):
                            st.markdown("**🎓 Additional Information**")
                            if doctor.get('qualifications'):
                                st.markdown(f"**Qualifications:** {doctor['qualifications']}")
                            if doctor.get('languages'):
                                st.markdown(f"**Languages:** {doctor['languages']}")
                        
                        # Contact button
                        if st.button("💬 Contact Doctor", key=f"contact_{doctor_key}"):
                            st.info(f"Contact Dr. {doctor['name']} at {doctor['phone']} or {doctor['email']}")
                        
                        st.markdown("---")
                    
                    st.divider()
        else:
            st.info("No other doctors found matching your criteria. Try adjusting your filters.")
    else:
        st.error("Doctor registry feature not available")

def render_profile_page():
    """Render the user profile page"""
    st.markdown("## 👤 My Profile")
    if 'user_data' not in st.session_state:
        st.error("Please log in to view your profile.")
        return
    user = st.session_state.user_data
    st.markdown(f"### Welcome, {user['username']}")
    st.markdown(f"**Email:** {user['email']}")
    st.markdown(f"**Role:** {user['role'].capitalize()}")
    st.markdown(f"**Verified:** {'✅' if user.get('is_verified', False) else '❌'}")
    # Add more details as needed
    st.markdown("---")
    if st.button("🔒 Logout"):
        from components.login_auth import logout_user
        logout_user()
        st.success("Logged out successfully!")
        st.session_state.clear()
        st.rerun()

if __name__ == "__main__":
    main()
