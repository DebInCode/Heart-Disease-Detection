import streamlit as st
import json
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys
import traceback
import time
import os

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.predict import HeartDiseasePredictor
from reports.pdf_generator import generate_pdf_report

# Import chatbot component
try:
    from components.chatbot import add_chatbot_to_page
    CHATBOT_AVAILABLE = True
except ImportError:
    CHATBOT_AVAILABLE = False

def initialize_session_state():
    """Initialize session state variables."""
    if "patient_inputs" not in st.session_state:
        st.session_state.patient_inputs = {}
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "last_input" not in st.session_state:
        st.session_state.last_input = None
    if "prediction_history" not in st.session_state:
        st.session_state.prediction_history = []
    if "show_animation" not in st.session_state:
        st.session_state.show_animation = False

def get_medical_defaults(age, sex, chest_pain_type, breathlessness, fatigue):
    """
    Generate intelligent medical defaults based on patient inputs.
    Uses medical knowledge to set realistic clinical values.
    """
    defaults = {}
    
    # Resting Blood Pressure (trestbps) - varies by age and sex
    if age < 30:
        defaults['trestbps'] = 110 + np.random.randint(-10, 15)
    elif age < 50:
        defaults['trestbps'] = 120 + np.random.randint(-15, 20)
    elif age < 70:
        defaults['trestbps'] = 130 + np.random.randint(-20, 25)
    else:
        defaults['trestbps'] = 140 + np.random.randint(-25, 30)
    
    # Cholesterol (chol) - varies by age and sex
    if sex == 1:  # Male
        if age < 40:
            defaults['chol'] = 180 + np.random.randint(-30, 40)
        else:
            defaults['chol'] = 200 + np.random.randint(-40, 50)
    else:  # Female
        if age < 50:
            defaults['chol'] = 190 + np.random.randint(-30, 40)
        else:
            defaults['chol'] = 210 + np.random.randint(-40, 50)
    
    # Fasting Blood Sugar (fbs) - higher with age
    if age > 50:
        defaults['fbs'] = 1 if np.random.random() < 0.3 else 0
    else:
        defaults['fbs'] = 1 if np.random.random() < 0.1 else 0
    
    # Resting ECG (restecg) - varies by age
    if age > 60:
        defaults['restecg'] = np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1])
    else:
        defaults['restecg'] = np.random.choice([0, 1, 2], p=[0.8, 0.15, 0.05])
    
    # Maximum Heart Rate (thalach) - affected by age and fatigue
    max_hr = 220 - age  # Standard formula
    if fatigue == "Yes":
        max_hr *= 0.85  # Reduce if fatigued
    defaults['thalach'] = int(max_hr * (0.7 + np.random.random() * 0.3))
    
    # ST Depression (oldpeak) - already provided by user
    
    # Slope of ST segment (slope)
    if chest_pain_type in ["Moderate", "Severe"]:
        defaults['slope'] = np.random.choice([1, 2, 3], p=[0.3, 0.4, 0.3])
    else:
        defaults['slope'] = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1])
    
    # Number of vessels (ca) - affected by chest pain severity
    if chest_pain_type == "Severe":
        defaults['ca'] = np.random.choice([0, 1, 2, 3], p=[0.2, 0.3, 0.3, 0.2])
    elif chest_pain_type == "Moderate":
        defaults['ca'] = np.random.choice([0, 1, 2, 3], p=[0.4, 0.3, 0.2, 0.1])
    else:
        defaults['ca'] = np.random.choice([0, 1, 2, 3], p=[0.7, 0.2, 0.08, 0.02])
    
    # Thalassemia (thal) - genetic factor
    defaults['thal'] = np.random.choice([3, 6, 7], p=[0.6, 0.2, 0.2])
    
    return defaults

def create_input_form():
    """Create the patient input form with advanced features."""
    
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .section-header {
        color: #2E86AB;
        font-size: 1.3rem;
        font-weight: bold;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #2E86AB;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main title
    st.markdown('<h1 class="main-header">👤 Patient Mode - Heart Disease Risk Checker</h1>', unsafe_allow_html=True)
    
    # Information section
    with st.expander("ℹ️ How to use this tool", expanded=False):
        st.markdown("""
        **Instructions:**
        1. Fill in your basic information and symptoms
        2. The system will use medical knowledge to estimate other clinical values
        3. Get your personalized heart disease risk assessment
        4. Review detailed explanations and recommendations
        
        **Note:** This tool provides risk assessment only. Always consult healthcare professionals for medical decisions.
        """)
    
    # Personal Information Section
    st.markdown('<h3 class="section-header">📋 Personal Information</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.slider(
            "**Age** (years)",
            min_value=18,
            max_value=100,
            value=45,
            help="Your current age in years"
        )
        
        sex = st.radio(
            "**Sex**",
            options=["Male", "Female"],
            help="Your biological sex"
        )
    
    with col2:
        # Display age-related risk info
        if age > 65:
            st.warning("⚠️ **Age Risk Factor:** Advanced age increases heart disease risk")
        elif age > 45:
            st.info("ℹ️ **Age Risk Factor:** Middle age - monitor heart health regularly")
        else:
            st.success("✅ **Age Risk Factor:** Younger age - lower baseline risk")
        
        # Display sex-related info
        if sex == "Male":
            st.info("ℹ️ **Sex Risk Factor:** Males have higher baseline heart disease risk")
        else:
            st.success("✅ **Sex Risk Factor:** Females generally have lower baseline risk until menopause")
    
    # Symptoms Section
    st.markdown('<h3 class="section-header">🏥 Symptoms & Clinical Information</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        chest_pain_type = st.selectbox(
            "**Chest Pain Type**",
            options=["None", "Mild", "Moderate", "Severe"],
            help="Type and severity of chest pain you experience"
        )
        
        breathlessness = st.radio(
            "**Exercise-Induced Breathlessness**",
            options=["No", "Yes"],
            help="Do you experience shortness of breath during physical activity?"
        )
    
    with col2:
        fatigue = st.radio(
            "**Fatigue**",
            options=["No", "Yes"],
            help="Do you experience unusual tiredness or fatigue?"
        )
        
        st_depression = st.slider(
            "**ST Depression** (mm)",
            min_value=0.0,
            max_value=6.0,
            value=0.0,
            step=0.1,
            help="ST segment depression on ECG (if known, otherwise leave at 0)"
        )
    
    # Clinical Values Section (Auto-generated)
    st.markdown('<h3 class="section-header">🔬 Clinical Values (Auto-estimated)</h3>', unsafe_allow_html=True)
    
    # Get intelligent defaults
    defaults = get_medical_defaults(age, sex, chest_pain_type, breathlessness, fatigue)
    
    # Display clinical values with explanations
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Resting BP", f"{defaults['trestbps']} mmHg", 
                 help="Systolic blood pressure at rest")
        st.metric("Cholesterol", f"{defaults['chol']} mg/dL",
                 help="Total cholesterol level")
        st.metric("Max Heart Rate", f"{defaults['thalach']} bpm",
                 help="Maximum heart rate achieved during exercise")
    
    with col2:
        fbs_status = "High" if defaults['fbs'] == 1 else "Normal"
        st.metric("Blood Sugar", fbs_status,
                 help="Fasting blood sugar > 120 mg/dL")
        
        restecg_map = {0: "Normal", 1: "ST-T Abnormal", 2: "LVH"}
        st.metric("Resting ECG", restecg_map[defaults['restecg']],
                 help="Resting electrocardiographic results")
        
        slope_map = {1: "Upsloping", 2: "Flat", 3: "Downsloping"}
        st.metric("ST Slope", slope_map[defaults['slope']],
                 help="Slope of peak exercise ST segment")
    
    with col3:
        st.metric("Vessels", f"{defaults['ca']} vessels",
                 help="Number of major vessels colored by fluoroscopy")
        
        thal_map = {3: "Normal", 6: "Fixed Defect", 7: "Reversible Defect"}
        st.metric("Thalassemia", thal_map[defaults['thal']],
                 help="Thalassemia type")
        
        st.metric("ST Depression", f"{st_depression} mm",
                 help="ST depression induced by exercise")
    
    return {
        'age': age,
        'sex': 1 if sex == "Male" else 0,
        'cp': ["None", "Mild", "Moderate", "Severe"].index(chest_pain_type),
        'trestbps': defaults['trestbps'],
        'chol': defaults['chol'],
        'fbs': defaults['fbs'],
        'restecg': defaults['restecg'],
        'thalach': defaults['thalach'],
        'exang': 1 if breathlessness == "Yes" else 0,
        'oldpeak': st_depression,
        'slope': defaults['slope'],
        'ca': defaults['ca'],
        'thal': defaults['thal']
    }

def display_prediction_result(prediction, probability, input_data):
    """Display prediction results with advanced formatting and explanations."""
    
    st.markdown('<h3 class="section-header">📊 Risk Assessment Results</h3>', unsafe_allow_html=True)
    
    # Main result display
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if prediction == 1:
            if probability > 0.8:
                st.error(f"🚨 **HIGH RISK DETECTED**\n\n"
                        f"**Risk Level:** Very High ({probability:.1%})\n"
                        f"**Recommendation:** Immediate medical consultation recommended")
            elif probability > 0.6:
                st.warning(f"⚠️ **ELEVATED RISK DETECTED**\n\n"
                          f"**Risk Level:** High ({probability:.1%})\n"
                          f"**Recommendation:** Schedule medical evaluation soon")
            else:
                st.warning(f"⚠️ **MODERATE RISK DETECTED**\n\n"
                          f"**Risk Level:** Moderate ({probability:.1%})\n"
                          f"**Recommendation:** Monitor symptoms and consult doctor")
        else:
            if probability < 0.2:
                st.success(f"✅ **LOW RISK**\n\n"
                          f"**Risk Level:** Low ({probability:.1%})\n"
                          f"**Recommendation:** Continue healthy lifestyle")
            else:
                st.info(f"ℹ️ **LOW-MODERATE RISK**\n\n"
                       f"**Risk Level:** Low-Moderate ({probability:.1%})\n"
                       f"**Recommendation:** Regular health monitoring recommended")
    
    with col2:
        # Risk gauge
        st.markdown("**Risk Gauge:**")
        if probability < 0.2:
            st.markdown("🟢 Low Risk")
        elif probability < 0.4:
            st.markdown("🟡 Low-Moderate")
        elif probability < 0.6:
            st.markdown("🟠 Moderate")
        elif probability < 0.8:
            st.markdown("🔴 High")
        else:
            st.markdown("🔴 Very High")
    
    # Detailed analysis
    st.markdown('<h4 class="section-header">🔍 Detailed Analysis</h4>', unsafe_allow_html=True)
    
    # Risk factors analysis
    risk_factors = []
    protective_factors = []
    
    if input_data['age'] > 65:
        risk_factors.append("Advanced age")
    elif input_data['age'] > 45:
        risk_factors.append("Middle age")
    
    if input_data['sex'] == 1:
        risk_factors.append("Male sex")
    
    if input_data['cp'] > 1:
        risk_factors.append(f"Chest pain ({['None', 'Mild', 'Moderate', 'Severe'][input_data['cp']]})")
    
    if input_data['exang'] == 1:
        risk_factors.append("Exercise-induced breathlessness")
    
    if input_data['trestbps'] > 140:
        risk_factors.append("Elevated blood pressure")
    
    if input_data['chol'] > 240:
        risk_factors.append("High cholesterol")
    
    if input_data['fbs'] == 1:
        risk_factors.append("Elevated blood sugar")
    
    if input_data['oldpeak'] > 2.0:
        risk_factors.append("ST depression on ECG")
    
    # Display risk factors
    col1, col2 = st.columns(2)
    
    with col1:
        if risk_factors:
            st.markdown("**🚨 Risk Factors Identified:**")
            for factor in risk_factors:
                st.markdown(f"• {factor}")
        else:
            st.success("**✅ No major risk factors identified**")
    
    with col2:
        if input_data['age'] < 45:
            protective_factors.append("Young age")
        if input_data['sex'] == 0:
            protective_factors.append("Female sex")
        if input_data['trestbps'] < 120:
            protective_factors.append("Normal blood pressure")
        if input_data['chol'] < 200:
            protective_factors.append("Normal cholesterol")
        
        if protective_factors:
            st.markdown("**✅ Protective Factors:**")
            for factor in protective_factors:
                st.markdown(f"• {factor}")
    
    # Recommendations
    st.markdown('<h4 class="section-header">💡 Recommendations</h4>', unsafe_allow_html=True)
    
    if prediction == 1:
        st.markdown("""
        **Immediate Actions:**
        • Schedule appointment with cardiologist
        • Monitor symptoms closely
        • Avoid strenuous activities
        • Keep emergency contacts ready
        
        **Lifestyle Changes:**
        • Adopt heart-healthy diet
        • Regular moderate exercise
        • Stress management
        • Smoking cessation (if applicable)
        """)
    else:
        st.markdown("""
        **Preventive Measures:**
        • Regular health checkups
        • Maintain healthy lifestyle
        • Monitor blood pressure and cholesterol
        • Regular exercise routine
        
        **Risk Reduction:**
        • Heart-healthy diet
        • Stress management
        • Adequate sleep
        • Regular medical follow-ups
        """)

    # Add PDF download button
    if st.button("📄 Download PDF Report", type="primary"):
        try:
            # Prepare tips for the PDF
            tips = {
                "food": [
                    "Increase omega-3 rich foods (salmon, walnuts)",
                    "Eat more fiber-rich foods (oats, whole grains)",
                    "Reduce sodium intake to less than 2,300mg per day",
                    "Limit saturated and trans fats",
                    "Include antioxidant-rich foods (berries, dark chocolate)"
                ],
                "exercise": [
                    "Aerobic exercise: 150 minutes moderate per week",
                    "Strength training: 2-3 sessions per week",
                    "Start with walking 30 minutes daily",
                    "Gradually increase intensity under medical supervision"
                ],
                "lifestyle": [
                    "Quit smoking to reduce heart disease risk",
                    "Maintain healthy weight through diet and exercise",
                    "Get 7-9 hours of quality sleep nightly",
                    "Practice stress management techniques"
                ]
            }
            
            # Generate PDF report
            pdf_bytes = generate_pdf_report(
                user_data=input_data,
                prediction=prediction,
                tips=tips,
                lang="en"
            )
            
            if pdf_bytes:
                st.success("✅ PDF report generated successfully!")
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"Heart_Disease_Risk_Assessment_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("❌ Failed to generate PDF report")
        except Exception as e:
            st.error(f"❌ Error generating PDF report: {str(e)}")
            st.error("Please ensure reportlab is installed: pip install reportlab")

def save_prediction_to_log(input_data, prediction, probability):
    """Save prediction result to patient logs."""
    try:
        log_file = project_root / "data" / "patient_logs.json"
        
        # Create data directory if it doesn't exist
        log_file.parent.mkdir(exist_ok=True)
        
        # Load existing logs or create new
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "input_data": input_data,
            "prediction": int(prediction),
            "probability": float(probability),
            "risk_level": "High" if prediction == 1 else "Low"
        }
        
        logs.append(log_entry)
        
        # Save updated logs
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return True
    except Exception as e:
        st.error(f"Error saving log: {str(e)}")
        return False

def create_risk_gauge_chart(probability):
    """Create an interactive risk gauge chart using Plotly."""
    fig = go.Figure()
    
    # Define colors based on risk level
    if probability < 0.2:
        color = "#28a745"  # Green
        risk_text = "Low Risk"
    elif probability < 0.4:
        color = "#ffc107"  # Yellow
        risk_text = "Low-Moderate"
    elif probability < 0.6:
        color = "#fd7e14"  # Orange
        risk_text = "Moderate"
    elif probability < 0.8:
        color = "#dc3545"  # Red
        risk_text = "High"
    else:
        color = "#6f42c1"  # Purple
        risk_text = "Very High"
    
    # Create gauge chart
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=probability * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Heart Disease Risk: {risk_text}"},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 20], 'color': "#28a745"},
                {'range': [20, 40], 'color': "#ffc107"},
                {'range': [40, 60], 'color': "#fd7e14"},
                {'range': [60, 80], 'color': "#dc3545"},
                {'range': [80, 100], 'color': "#6f42c1"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 60
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        font={'size': 14}
    )
    
    return fig

def create_risk_factors_chart(input_data):
    """Create a radar chart showing risk factors."""
    # Calculate risk scores for different factors
    factors = {
        'Age': min(input_data['age'] / 100, 1.0),
        'Blood Pressure': min(input_data['trestbps'] / 200, 1.0),
        'Cholesterol': min(input_data['chol'] / 300, 1.0),
        'ST Depression': min(input_data['oldpeak'] / 4, 1.0),
        'Chest Pain': input_data['cp'] / 3,
        'Exercise Angina': input_data['exang']
    }
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=list(factors.values()),
        theta=list(factors.keys()),
        fill='toself',
        name='Risk Factors',
        line_color='red',
        fillcolor='rgba(255, 0, 0, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=False,
        height=400,
        title="Risk Factor Analysis"
    )
    
    return fig

def create_vital_signs_chart(input_data):
    """Create a bar chart showing vital signs."""
    vitals = {
        'Age': input_data['age'],
        'Blood Pressure': input_data['trestbps'],
        'Cholesterol': input_data['chol'],
        'Max Heart Rate': input_data['thalach']
    }
    
    # Define normal ranges for color coding
    colors = []
    for key, value in vitals.items():
        if key == 'Age':
            colors.append('#28a745' if value < 65 else '#ffc107' if value < 80 else '#dc3545')
        elif key == 'Blood Pressure':
            colors.append('#28a745' if value < 120 else '#ffc107' if value < 140 else '#dc3545')
        elif key == 'Cholesterol':
            colors.append('#28a745' if value < 200 else '#ffc107' if value < 240 else '#dc3545')
        elif key == 'Max Heart Rate':
            colors.append('#28a745' if value > 150 else '#ffc107' if value > 120 else '#dc3545')
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(vitals.keys()),
            y=list(vitals.values()),
            marker_color=colors,
            text=[f"{v:.0f}" for v in vitals.values()],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Vital Signs Overview",
        xaxis_title="Vital Signs",
        yaxis_title="Values",
        height=300,
        showlegend=False
    )
    
    return fig

def create_trend_chart(history):
    """Create a trend chart from prediction history."""
    if len(history) < 2:
        return None
    
    dates = [h['timestamp'] for h in history]
    probabilities = [h['probability'] * 100 for h in history]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=probabilities,
        mode='lines+markers',
        name='Risk Trend',
        line=dict(color='red', width=3),
        marker=dict(size=8)
    ))
    
    # Add threshold lines
    fig.add_hline(y=20, line_dash="dash", line_color="green", annotation_text="Low Risk")
    fig.add_hline(y=60, line_dash="dash", line_color="red", annotation_text="High Risk")
    
    fig.update_layout(
        title="Risk Trend Over Time",
        xaxis_title="Date",
        yaxis_title="Risk Percentage (%)",
        height=300
    )
    
    return fig

def animate_loading():
    """Show loading animation."""
    st.markdown("""
    <style>
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="loading"></div> Analyzing your data...', unsafe_allow_html=True)

def main():
    """Main function for patient mode."""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Initialize predictor
        try:
            predictor = HeartDiseasePredictor()
        except Exception as e:
            st.error(f"❌ Error loading prediction model: {str(e)}")
            st.info("Please ensure the model files are available in the models/ directory.")
            return
        
        # Create input form
        input_data = create_input_form()
        
        # Prediction button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 **Analyze Heart Disease Risk**", type="primary", use_container_width=True):
                with st.spinner("Analyzing your risk factors..."):
                    try:
                        # Make prediction
                        prediction, probability = predictor.predict_heart_disease(input_data)
                        
                        if prediction is not None:
                            # Store results in session state
                            st.session_state.last_result = {
                                'prediction': prediction,
                                'probability': probability
                            }
                            st.session_state.last_input = input_data
                            
                            # Add to history
                            st.session_state.prediction_history.append({
                                'timestamp': datetime.datetime.now(),
                                'prediction': prediction,
                                'probability': probability
                            })
                            
                            # Display results
                            display_prediction_result(prediction, probability, input_data)
                            
                            # Save report button
                            if st.button("💾 Save Report", type="secondary"):
                                if save_prediction_to_log(input_data, prediction, probability):
                                    st.success("✅ Report saved successfully!")
                                else:
                                    st.error("❌ Failed to save report")
                        else:
                            st.error("❌ Prediction failed. Please check your inputs.")
                    
                    except Exception as e:
                        st.error(f"❌ Error during prediction: {str(e)}")
                        st.error("Please try again or contact support.")
        
        # Display last result if available
        if st.session_state.last_result:
            st.markdown("---")
            st.markdown("**📋 Last Assessment:**")
            last_pred = st.session_state.last_result['prediction']
            last_prob = st.session_state.last_result['probability']
            
            if last_pred == 1:
                st.warning(f"Risk Level: {'High' if last_prob > 0.6 else 'Moderate'} ({last_prob:.1%})")
            else:
                st.success(f"Risk Level: Low ({last_prob:.1%})")
        
        # Prediction history
        if st.session_state.prediction_history:
            with st.expander("📈 Prediction History", expanded=False):
                for i, hist in enumerate(reversed(st.session_state.prediction_history[-5:]), 1):
                    pred_text = "High Risk" if hist['prediction'] == 1 else "Low Risk"
                    st.markdown(f"**{i}.** {hist['timestamp'].strftime('%Y-%m-%d %H:%M')} - {pred_text} ({hist['probability']:.1%})")
        
        # Medical disclaimer
        st.markdown("---")
        st.markdown("""
        <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 10px; border-left: 4px solid #dc3545;'>
        <strong>⚠️ Medical Disclaimer:</strong><br>
        This tool provides risk assessment only and is not a substitute for professional medical advice, 
        diagnosis, or treatment. Always consult qualified healthcare professionals for medical decisions. 
        In case of emergency, call emergency services immediately.
        </div>
        """, unsafe_allow_html=True)
        
        # Add global chatbot
        if CHATBOT_AVAILABLE:
            add_chatbot_to_page()
        
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)}")
        st.error("Please refresh the page and try again.")

if __name__ == "__main__":
    main()
