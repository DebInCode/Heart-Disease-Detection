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
    """Initialize session state variables for doctor mode."""
    if "doctor_inputs" not in st.session_state:
        st.session_state.doctor_inputs = {}
    if "doctor_result" not in st.session_state:
        st.session_state.doctor_result = None
    if "doctor_history" not in st.session_state:
        st.session_state.doctor_history = []
    if "show_advanced_charts" not in st.session_state:
        st.session_state.show_advanced_charts = False

def create_medical_gauge_chart(probability):
    """Create a professional medical gauge chart."""
    fig = go.Figure()
    
    # Medical color coding
    if probability < 0.2:
        color = "#28a745"  # Green - Low Risk
        risk_text = "Low Risk"
        risk_level = "Normal"
    elif probability < 0.4:
        color = "#ffc107"  # Yellow - Borderline
        risk_text = "Borderline"
        risk_level = "Monitor"
    elif probability < 0.6:
        color = "#fd7e14"  # Orange - Moderate
        risk_text = "Moderate Risk"
        risk_level = "Follow-up"
    elif probability < 0.8:
        color = "#dc3545"  # Red - High
        risk_text = "High Risk"
        risk_level = "Intervention"
    else:
        color = "#6f42c1"  # Purple - Very High
        risk_text = "Very High Risk"
        risk_level = "Immediate"
    
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=probability * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Cardiovascular Risk Assessment<br><span style='font-size:0.8em;color:gray'>{risk_level}</span>"},
        delta={'reference': 50, 'increasing': {'color': "red"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
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
        height=350,
        margin=dict(l=20, r=20, t=60, b=20),
        font={'size': 14, 'color': "darkblue"},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_clinical_radar_chart(input_data):
    """Create a radar chart showing clinical parameters."""
    # Normalize clinical values for radar chart
    clinical_params = {
        'Age': min(input_data['age'] / 100, 1.0),
        'Blood Pressure': min(input_data['trestbps'] / 200, 1.0),
        'Cholesterol': min(input_data['chol'] / 300, 1.0),
        'ST Depression': min(input_data['oldpeak'] / 4, 1.0),
        'Max HR': 1 - min(input_data['thalach'] / 200, 1.0),  # Inverted for risk
        'Chest Pain': input_data['cp'] / 3
    }
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=list(clinical_params.values()),
        theta=list(clinical_params.keys()),
        fill='toself',
        name='Clinical Parameters',
        line_color='darkblue',
        fillcolor='rgba(0, 0, 255, 0.2)',
        line_width=3
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickfont={'size': 10}
            ),
            angularaxis=dict(
                tickfont={'size': 12, 'color': 'darkblue'}
            )
        ),
        showlegend=False,
        height=400,
        title="Clinical Parameters Overview",
        font={'color': 'darkblue'}
    )
    
    return fig

def create_vital_signs_comparison(input_data):
    """Create a comparison chart of vital signs with normal ranges."""
    vitals = {
        'Age': input_data['age'],
        'Systolic BP': input_data['trestbps'],
        'Cholesterol': input_data['chol'],
        'Max HR': input_data['thalach']
    }
    
    # Define normal ranges
    normal_ranges = {
        'Age': (18, 100),
        'Systolic BP': (90, 140),
        'Cholesterol': (100, 200),
        'Max HR': (120, 200)
    }
    
    # Color coding based on normal ranges
    colors = []
    for key, value in vitals.items():
        low, high = normal_ranges[key]
        if key == 'Max HR':
            # For heart rate, higher is better (inverted logic)
            if value >= high:
                colors.append('#28a745')  # Green
            elif value >= low:
                colors.append('#ffc107')  # Yellow
            else:
                colors.append('#dc3545')  # Red
        else:
            if low <= value <= high:
                colors.append('#28a745')  # Green
            elif value < low * 0.8 or value > high * 1.2:
                colors.append('#dc3545')  # Red
            else:
                colors.append('#ffc107')  # Yellow
    
    fig = go.Figure()
    
    # Add bars for current values
    fig.add_trace(go.Bar(
        x=list(vitals.keys()),
        y=list(vitals.values()),
        marker_color=colors,
        text=[f"{v:.0f}" for v in vitals.values()],
        textposition='auto',
        name='Current Values',
        hovertemplate='<b>%{x}</b><br>Value: %{y}<extra></extra>'
    ))
    
    # Add normal range indicators
    for i, (key, (low, high)) in enumerate(normal_ranges.items()):
        fig.add_shape(
            type="rect",
            x0=i-0.3, x1=i+0.3,
            y0=low, y1=high,
            fillcolor="lightgreen",
            opacity=0.3,
            layer="below",
            line_width=0
        )
    
    fig.update_layout(
        title="Vital Signs vs Normal Ranges",
        xaxis_title="Clinical Parameters",
        yaxis_title="Values",
        height=350,
        showlegend=False,
        hovermode='closest'
    )
    
    return fig

def create_risk_factor_breakdown(input_data):
    """Create a detailed risk factor breakdown chart."""
    risk_factors = []
    risk_scores = []
    
    # Age risk
    if input_data['age'] > 65:
        risk_factors.append("Advanced Age")
        risk_scores.append(0.8)
    elif input_data['age'] > 45:
        risk_factors.append("Middle Age")
        risk_scores.append(0.5)
    else:
        risk_factors.append("Young Age")
        risk_scores.append(0.2)
    
    # Blood pressure risk
    if input_data['trestbps'] > 160:
        risk_factors.append("Severe Hypertension")
        risk_scores.append(0.9)
    elif input_data['trestbps'] > 140:
        risk_factors.append("Hypertension")
        risk_scores.append(0.7)
    elif input_data['trestbps'] > 120:
        risk_factors.append("Pre-hypertension")
        risk_scores.append(0.4)
    else:
        risk_factors.append("Normal BP")
        risk_scores.append(0.1)
    
    # Cholesterol risk
    if input_data['chol'] > 240:
        risk_factors.append("High Cholesterol")
        risk_scores.append(0.8)
    elif input_data['chol'] > 200:
        risk_factors.append("Borderline Cholesterol")
        risk_scores.append(0.5)
    else:
        risk_factors.append("Normal Cholesterol")
        risk_scores.append(0.2)
    
    # Chest pain risk
    chest_pain_levels = ["None", "Mild", "Moderate", "Severe"]
    risk_factors.append(f"Chest Pain ({chest_pain_levels[input_data['cp']]})")
    risk_scores.append(input_data['cp'] / 3)
    
    # ST depression risk
    if input_data['oldpeak'] > 2.0:
        risk_factors.append("ST Depression")
        risk_scores.append(0.8)
    elif input_data['oldpeak'] > 1.0:
        risk_factors.append("Mild ST Changes")
        risk_scores.append(0.5)
    else:
        risk_factors.append("Normal ST")
        risk_scores.append(0.1)
    
    # Exercise angina
    if input_data['exang'] == 1:
        risk_factors.append("Exercise Angina")
        risk_scores.append(0.7)
    else:
        risk_factors.append("No Exercise Angina")
        risk_scores.append(0.1)
    
    # Color coding
    colors = ['#dc3545' if score > 0.6 else '#ffc107' if score > 0.3 else '#28a745' for score in risk_scores]
    
    fig = go.Figure(data=[
        go.Bar(
            x=risk_factors,
            y=risk_scores,
            marker_color=colors,
            text=[f"{score:.1%}" for score in risk_scores],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Risk Score: %{y:.1%}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="Risk Factor Breakdown",
        xaxis_title="Risk Factors",
        yaxis_title="Risk Score",
        height=400,
        showlegend=False,
        xaxis_tickangle=-45
    )
    
    return fig

def create_input_form():
    """Create the comprehensive doctor input form."""
    
    st.markdown("""
    <style>
    .doctor-header {
        text-align: center;
        color: #1e3a8a;
        font-size: 2.2rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .section-header {
        color: #1e3a8a;
        font-size: 1.4rem;
        font-weight: bold;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #1e3a8a;
        padding-bottom: 0.5rem;
    }
    .medical-box {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #1e3a8a;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .warning-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main title
    st.markdown('<h1 class="doctor-header">🧑‍⚕️ Doctor Mode - Advanced Risk Assessment</h1>', unsafe_allow_html=True)
    
    # Professional disclaimer
    with st.expander("ℹ️ Medical Professional Guidelines", expanded=False):
        st.markdown("""
        **Clinical Assessment Protocol:**
        - This tool assists in cardiovascular risk assessment
        - All inputs should be based on actual clinical measurements
        - Results should be interpreted in clinical context
        - Always correlate with patient history and physical examination
        
        **Data Validation:**
        - Ensure all measurements are recent and accurate
        - Cross-reference with patient's medical history
        - Consider additional diagnostic tests if indicated
        """)
    
    # Patient Demographics Section
    st.markdown('<h3 class="section-header">📋 Patient Demographics</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.slider(
            "**Patient Age** (years)",
            min_value=18,
            max_value=100,
            value=50,
            help="Patient's current age in years"
        )
        
        sex = st.radio(
            "**Patient Sex**",
            options=["Male", "Female"],
            help="Patient's biological sex"
        )
    
    with col2:
        # Age risk indicator
        if age > 65:
            st.markdown('<div class="warning-box">⚠️ **Age Risk Factor:** Advanced age increases cardiovascular risk</div>', unsafe_allow_html=True)
        elif age > 45:
            st.markdown('<div class="medical-box">ℹ️ **Age Risk Factor:** Middle age - regular monitoring recommended</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="medical-box">✅ **Age Risk Factor:** Younger age - lower baseline risk</div>', unsafe_allow_html=True)
        
        # Sex risk indicator
        if sex == "Male":
            st.markdown('<div class="medical-box">ℹ️ **Sex Risk Factor:** Males have higher baseline cardiovascular risk</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="medical-box">✅ **Sex Risk Factor:** Females generally have lower baseline risk until menopause</div>', unsafe_allow_html=True)
    
    # Clinical Parameters Section
    st.markdown('<h3 class="section-header">🏥 Clinical Parameters</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        cp = st.selectbox(
            "**Chest Pain Type**",
            options=["None", "Typical Angina", "Atypical Angina", "Non-anginal Pain"],
            help="Type of chest pain experienced by patient"
        )
        
        trestbps = st.number_input(
            "**Resting Blood Pressure** (mmHg)",
            min_value=80,
            max_value=250,
            value=120,
            help="Systolic blood pressure at rest"
        )
        
        chol = st.number_input(
            "**Serum Cholesterol** (mg/dL)",
            min_value=100,
            max_value=600,
            value=200,
            help="Total cholesterol level"
        )
        
        fbs = st.radio(
            "**Fasting Blood Sugar**",
            options=["Normal (< 120 mg/dL)", "High (≥ 120 mg/dL)"],
            help="Fasting blood sugar level"
        )
    
    with col2:
        restecg = st.selectbox(
            "**Resting ECG Results**",
            options=["Normal", "ST-T Wave Abnormality", "Left Ventricular Hypertrophy"],
            help="Resting electrocardiographic results"
        )
        
        thalach = st.number_input(
            "**Maximum Heart Rate** (bpm)",
            min_value=60,
            max_value=220,
            value=150,
            help="Maximum heart rate achieved during exercise"
        )
        
        exang = st.radio(
            "**Exercise-Induced Angina**",
            options=["No", "Yes"],
            help="Exercise-induced chest pain"
        )
        
        oldpeak = st.number_input(
            "**ST Depression** (mm)",
            min_value=0.0,
            max_value=6.0,
            value=0.0,
            step=0.1,
            help="ST depression induced by exercise relative to rest"
        )
    
    # Advanced Clinical Parameters
    st.markdown('<h3 class="section-header">🔬 Advanced Clinical Parameters</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        slope = st.selectbox(
            "**ST Segment Slope**",
            options=["Upsloping", "Flat", "Downsloping"],
            help="Slope of peak exercise ST segment"
        )
    
    with col2:
        ca = st.selectbox(
            "**Number of Major Vessels**",
            options=["0 vessels", "1 vessel", "2 vessels", "3 vessels"],
            help="Number of major vessels colored by fluoroscopy"
        )
    
    with col3:
        thal = st.selectbox(
            "**Thalassemia Type**",
            options=["Normal", "Fixed Defect", "Reversible Defect"],
            help="Thalassemia type from nuclear imaging"
        )
    
    # Clinical Values Summary
    st.markdown('<h3 class="section-header">📊 Clinical Values Summary</h3>', unsafe_allow_html=True)
    
    # Create summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
        <h4>Age</h4>
        <h3>{age} years</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        bp_status = "Normal" if 90 <= trestbps <= 140 else "Elevated" if trestbps > 140 else "Low"
        bp_color = "#28a745" if bp_status == "Normal" else "#dc3545"
        st.markdown(f"""
        <div class="metric-card">
        <h4>Blood Pressure</h4>
        <h3 style="color: {bp_color}">{trestbps} mmHg</h3>
        <small>{bp_status}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        chol_status = "Normal" if chol <= 200 else "Elevated"
        chol_color = "#28a745" if chol_status == "Normal" else "#dc3545"
        st.markdown(f"""
        <div class="metric-card">
        <h4>Cholesterol</h4>
        <h3 style="color: {chol_color}">{chol} mg/dL</h3>
        <small>{chol_status}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        hr_status = "Normal" if thalach >= 120 else "Low"
        hr_color = "#28a745" if hr_status == "Normal" else "#dc3545"
        st.markdown(f"""
        <div class="metric-card">
        <h4>Max Heart Rate</h4>
        <h3 style="color: {hr_color}">{thalach} bpm</h3>
        <small>{hr_status}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Convert inputs to model format
    input_data = {
        'age': age,
        'sex': 1 if sex == "Male" else 0,
        'cp': ["None", "Typical Angina", "Atypical Angina", "Non-anginal Pain"].index(cp),
        'trestbps': trestbps,
        'chol': chol,
        'fbs': 1 if fbs == "High (≥ 120 mg/dL)" else 0,
        'restecg': ["Normal", "ST-T Wave Abnormality", "Left Ventricular Hypertrophy"].index(restecg),
        'thalach': thalach,
        'exang': 1 if exang == "Yes" else 0,
        'oldpeak': oldpeak,
        'slope': ["Upsloping", "Flat", "Downsloping"].index(slope) + 1,
        'ca': ["0 vessels", "1 vessel", "2 vessels", "3 vessels"].index(ca),
        'thal': ["Normal", "Fixed Defect", "Reversible Defect"].index(thal) + 3
    }
    
    return input_data

def display_advanced_results(prediction, probability, input_data):
    """Display comprehensive results with advanced visualizations."""
    
    st.markdown('<h3 class="section-header">📊 Advanced Risk Assessment Results</h3>', unsafe_allow_html=True)
    
    # Main result with gauge chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display gauge chart
        gauge_fig = create_medical_gauge_chart(probability)
        st.plotly_chart(gauge_fig, use_container_width=True)
    
    with col2:
        # Risk level indicator
        if prediction == 1:
            if probability > 0.8:
                st.error(f"🚨 **VERY HIGH RISK**\n\n"
                        f"**Confidence:** {probability:.1%}\n"
                        f"**Clinical Action:** Immediate intervention required")
            elif probability > 0.6:
                st.error(f"⚠️ **HIGH RISK**\n\n"
                        f"**Confidence:** {probability:.1%}\n"
                        f"**Clinical Action:** Urgent evaluation needed")
            else:
                st.warning(f"⚠️ **MODERATE RISK**\n\n"
                          f"**Confidence:** {probability:.1%}\n"
                          f"**Clinical Action:** Close monitoring required")
        else:
            if probability < 0.2:
                st.success(f"✅ **LOW RISK**\n\n"
                          f"**Confidence:** {probability:.1%}\n"
                          f"**Clinical Action:** Routine follow-up")
            else:
                st.info(f"ℹ️ **LOW-MODERATE RISK**\n\n"
                       f"**Confidence:** {probability:.1%}\n"
                       f"**Clinical Action:** Regular monitoring")
    
    # Advanced visualizations
    st.markdown('<h4 class="section-header">📈 Clinical Analysis</h4>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Vital Signs", "Risk Factors", "Clinical Insights"])
    
    with tab1:
        vital_fig = create_vital_signs_comparison(input_data)
        st.plotly_chart(vital_fig, use_container_width=True)
        
        # Vital signs interpretation
        st.markdown("**Clinical Interpretation:**")
        if input_data['trestbps'] > 140:
            st.warning("⚠️ **Hypertension detected** - Consider antihypertensive therapy")
        if input_data['chol'] > 240:
            st.warning("⚠️ **Hypercholesterolemia detected** - Consider lipid-lowering therapy")
        if input_data['thalach'] < 120:
            st.warning("⚠️ **Reduced exercise capacity** - May indicate underlying cardiac disease")
    
    with tab2:
        risk_fig = create_risk_factor_breakdown(input_data)
        st.plotly_chart(risk_fig, use_container_width=True)
        
        # Risk factor analysis
        high_risk_factors = []
        if input_data['age'] > 65:
            high_risk_factors.append("Advanced age")
        if input_data['trestbps'] > 160:
            high_risk_factors.append("Severe hypertension")
        if input_data['chol'] > 240:
            high_risk_factors.append("High cholesterol")
        if input_data['cp'] > 1:
            high_risk_factors.append("Significant chest pain")
        if input_data['oldpeak'] > 2.0:
            high_risk_factors.append("ST depression")
        
        if high_risk_factors:
            st.markdown("**🚨 High-Risk Factors Identified:**")
            for factor in high_risk_factors:
                st.markdown(f"• {factor}")
    
    with tab3:
        st.markdown("**Clinical Insights:**")
        if input_data['exang'] == 1:
            st.warning("• Exercise-induced angina suggests coronary artery disease")
        if input_data['restecg'] > 0:
            st.warning("• ECG abnormalities detected - consider further cardiac evaluation")
        if input_data['slope'] == 3:
            st.warning("• Downsloping ST segment may indicate ischemia")
        
        # Clinical recommendations
        st.markdown("**💡 Clinical Recommendations:**")
        if prediction == 1:
            st.markdown("""
            **Immediate Clinical Actions:**
            • **Cardiology consultation** - Schedule urgent appointment
            • **Stress testing** - Consider exercise or pharmacological stress test
            • **Coronary angiography** - Evaluate for coronary artery disease
            • **Medical therapy** - Consider antiplatelet, statin, beta-blocker therapy
            """)
        else:
            st.markdown("""
            **Preventive Measures:**
            • **Regular follow-up** - Schedule routine cardiovascular assessment
            • **Risk factor management** - Optimize blood pressure, cholesterol, diabetes control
            • **Lifestyle counseling** - Diet, exercise, smoking cessation
            • **Screening** - Regular cardiovascular risk assessment
            """)

def save_to_feedback(input_data, prediction, probability):
    """Save assessment data to feedback CSV for model monitoring."""
    try:
        feedback_file = project_root / "data" / "feedbacks.csv"
        
        # Create data directory if it doesn't exist
        feedback_file.parent.mkdir(exist_ok=True)
        
        # Prepare feedback data
        feedback_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'age': input_data['age'],
            'sex': input_data['sex'],
            'cp': input_data['cp'],
            'trestbps': input_data['trestbps'],
            'chol': input_data['chol'],
            'fbs': input_data['fbs'],
            'restecg': input_data['restecg'],
            'thalach': input_data['thalach'],
            'exang': input_data['exang'],
            'oldpeak': input_data['oldpeak'],
            'slope': input_data['slope'],
            'ca': input_data['ca'],
            'thal': input_data['thal'],
            'prediction': prediction,
            'probability': probability,
            'doctor_confidence': 'high'  # Placeholder for future doctor confidence rating
        }
        
        # Convert to DataFrame and save
        df = pd.DataFrame([feedback_data])
        
        if feedback_file.exists():
            df.to_csv(feedback_file, mode='a', header=False, index=False)
        else:
            df.to_csv(feedback_file, index=False)
        
        return True
    except Exception as e:
        st.error(f"Error saving feedback: {str(e)}")
        return False

def main():
    """Main function for doctor mode."""
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
        
        # Assessment button with loading animation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔬 **Perform Advanced Risk Assessment**", type="primary", use_container_width=True):
                with st.spinner("Analyzing clinical parameters..."):
                    try:
                        # Make prediction
                        prediction, probability = predictor.predict_heart_disease(input_data)
                        
                        if prediction is not None:
                            # Store results in session state
                            st.session_state.doctor_result = {
                                'prediction': prediction,
                                'probability': probability,
                                'input_data': input_data
                            }
                            
                            # Add to history
                            st.session_state.doctor_history.append({
                                'timestamp': datetime.datetime.now(),
                                'prediction': prediction,
                                'probability': probability,
                                'input_data': input_data
                            })
                            
                            # Display results
                            display_advanced_results(prediction, probability, input_data)
                            
                            # PDF Download Section
                            st.markdown("---")
                            st.markdown("### 📄 Clinical Report Generation")
                            
                            if st.button("📄 Generate Clinical PDF Report", type="primary"):
                                try:
                                    # Prepare comprehensive tips for the PDF
                                    tips = {
                                        "food": [
                                            "Heart-healthy Mediterranean diet recommended",
                                            "Increase omega-3 fatty acids (fish, nuts)",
                                            "Reduce sodium intake to <2,300mg/day",
                                            "Limit saturated fats and trans fats",
                                            "Increase fiber intake (25-30g/day)"
                                        ],
                                        "exercise": [
                                            "Cardiac rehabilitation program if indicated",
                                            "Aerobic exercise: 150 min/week moderate intensity",
                                            "Resistance training: 2-3 sessions/week",
                                            "Start with supervised exercise program",
                                            "Monitor symptoms during activity"
                                        ],
                                        "lifestyle": [
                                            "Smoking cessation counseling and support",
                                            "Blood pressure monitoring and management",
                                            "Diabetes management if applicable",
                                            "Stress management and mental health support",
                                            "Regular follow-up with cardiologist"
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
                                        st.success("✅ Clinical PDF report generated successfully!")
                                        st.download_button(
                                            label="📄 Download Clinical Report",
                                            data=pdf_bytes,
                                            file_name=f"Clinical_Heart_Assessment_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf",
                                            mime="application/pdf"
                                        )
                                    else:
                                        st.error("❌ Failed to generate clinical PDF report")
                                except Exception as e:
                                    st.error(f"❌ Error generating clinical PDF report: {str(e)}")
                                    st.error("Please ensure reportlab is installed: pip install reportlab")
                            
                            # Save options
                            st.markdown("---")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.button("💾 Save Assessment Report", type="secondary"):
                                    # Save to session state for PDF generation
                                    st.session_state.doctor_inputs = input_data
                                    st.success("✅ Assessment saved to session for PDF generation")
                            
                            with col2:
                                save_feedback = st.checkbox("📊 Save to Model Feedback Database")
                                if save_feedback:
                                    if save_to_feedback(input_data, prediction, probability):
                                        st.success("✅ Data saved to feedback database")
                                    else:
                                        st.error("❌ Failed to save to feedback database")
                        else:
                            st.error("❌ Assessment failed. Please check clinical parameters.")
                    
                    except Exception as e:
                        st.error(f"❌ Error during assessment: {str(e)}")
                        st.error("Please verify all clinical parameters and try again.")
        
        # Display last assessment if available
        if st.session_state.doctor_result:
            st.markdown("---")
            st.markdown("**📋 Last Clinical Assessment:**")
            last_pred = st.session_state.doctor_result['prediction']
            last_prob = st.session_state.doctor_result['probability']
            
            if last_pred == 1:
                st.warning(f"Risk Level: {'Very High' if last_prob > 0.8 else 'High' if last_prob > 0.6 else 'Moderate'} ({last_prob:.1%})")
            else:
                st.success(f"Risk Level: Low ({last_prob:.1%})")
        
        # Assessment history
        if st.session_state.doctor_history:
            with st.expander("📈 Assessment History", expanded=False):
                for i, hist in enumerate(reversed(st.session_state.doctor_history[-5:]), 1):
                    pred_text = "High Risk" if hist['prediction'] == 1 else "Low Risk"
                    st.markdown(f"**{i}.** {hist['timestamp'].strftime('%Y-%m-%d %H:%M')} - {pred_text} ({hist['probability']:.1%})")
        
        # SHAP explanation placeholder
        st.markdown("---")
        st.markdown("""
        <div style='background: linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%); padding: 1.5rem; border-radius: 15px; border-left: 5px solid #0288d1;'>
        <h4>🧠 AI Explanation Module</h4>
        <p><strong>Feature Importance Breakdown:</strong> Advanced SHAP (SHapley Additive exPlanations) analysis will be available in the next update to provide detailed insights into how each clinical parameter contributes to the risk assessment.</p>
        <p><em>This will include:</em></p>
        <ul>
        <li>Individual feature importance scores</li>
        <li>Parameter interaction analysis</li>
        <li>Clinical interpretation guidelines</li>
        <li>Personalized risk factor explanations</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Medical disclaimer
        st.markdown("---")
        st.markdown("""
        <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 10px; border-left: 4px solid #dc3545;'>
        <strong>⚠️ Medical Professional Disclaimer:</strong><br>
        This tool is designed to assist medical professionals in cardiovascular risk assessment. 
        All clinical decisions must be based on comprehensive patient evaluation, including history, 
        physical examination, and appropriate diagnostic testing. This tool should not replace 
        clinical judgment or professional medical practice.
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
