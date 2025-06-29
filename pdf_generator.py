import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
import base64
from pathlib import Path
import sys
import streamlit as st

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class HeartDiseaseReportGenerator:
    """Generate professional PDF reports for heart disease assessments."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_LEFT,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_LEFT,
            fontName='Helvetica'
        )
        
        # Risk level styles
        self.low_risk_style = ParagraphStyle(
            'LowRisk',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=12,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            textColor=colors.green
        )
        
        self.medium_risk_style = ParagraphStyle(
            'MediumRisk',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=12,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            textColor=colors.orange
        )
        
        self.high_risk_style = ParagraphStyle(
            'HighRisk',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=12,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            textColor=colors.red
        )
    
    def generate_report(self, patient_data: dict, prediction_data: dict, output_path: str = None) -> str:
        """Generate a comprehensive heart disease assessment report"""
        
        if output_path is None:
            output_path = f"reports/heart_disease_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Ensure reports directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        
        # Build story (content)
        story = []
        
        # Add header
        story.extend(self.create_header())
        
        # Add patient information
        story.extend(self.create_patient_section(patient_data))
        
        # Add assessment results
        story.extend(self.create_results_section(prediction_data))
        
        # Add detailed analysis
        story.extend(self.create_analysis_section(prediction_data))
        
        # Add recommendations
        story.extend(self.create_recommendations_section(prediction_data))
        
        # Add medical disclaimer
        story.extend(self.create_disclaimer_section())
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def create_header(self):
        """Create the report header"""
        elements = []
        
        # Title
        title = Paragraph("Heart Disease Risk Assessment Report", self.title_style)
        elements.append(title)
        
        # Subtitle
        subtitle = Paragraph("AI-Powered Cardiovascular Health Analysis", self.subtitle_style)
        elements.append(subtitle)
        
        # Date
        date_text = f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        date_para = Paragraph(date_text, self.normal_style)
        elements.append(date_para)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def create_patient_section(self, patient_data: dict):
        """Create patient information section"""
        elements = []
        
        # Section title
        section_title = Paragraph("Patient Information", self.subtitle_style)
        elements.append(section_title)
        
        # Patient details table
        patient_info = [
            ["Field", "Value"],
            ["Age", str(patient_data.get('age', 'N/A'))],
            ["Sex", "Male" if patient_data.get('sex') == 1 else "Female"],
            ["Chest Pain Type", self.get_chest_pain_description(patient_data.get('cp', 0))],
            ["Resting Blood Pressure", f"{patient_data.get('trestbps', 'N/A')} mm Hg"],
            ["Cholesterol", f"{patient_data.get('chol', 'N/A')} mg/dl"],
            ["Fasting Blood Sugar", "High (>120 mg/dl)" if patient_data.get('fbs') == 1 else "Normal"],
            ["Resting ECG", self.get_ecg_description(patient_data.get('restecg', 0))],
            ["Max Heart Rate", f"{patient_data.get('thalach', 'N/A')} bpm"],
            ["Exercise Angina", "Yes" if patient_data.get('exang') == 1 else "No"],
            ["ST Depression", f"{patient_data.get('oldpeak', 'N/A')} mm"],
            ["Slope", self.get_slope_description(patient_data.get('slope', 0))],
            ["Major Vessels", str(patient_data.get('ca', 'N/A'))],
            ["Thalassemia", self.get_thal_description(patient_data.get('thal', 0))]
        ]
        
        patient_table = Table(patient_info, colWidths=[2*inch, 3*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(patient_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def create_results_section(self, prediction_data: dict):
        """Create assessment results section"""
        elements = []
        
        # Section title
        section_title = Paragraph("Assessment Results", self.subtitle_style)
        elements.append(section_title)
        
        # Risk level
        risk_level = prediction_data.get('risk_level', 'Unknown')
        probability = prediction_data.get('probability', 0)
        
        # Choose style based on risk level
        if 'Low' in risk_level:
            risk_style = self.low_risk_style
            risk_icon = "🟢"
        elif 'Moderate' in risk_level:
            risk_style = self.medium_risk_style
            risk_icon = "🟡"
        else:
            risk_style = self.high_risk_style
            risk_icon = "🔴"
        
        risk_text = f"{risk_icon} Risk Level: {risk_level}"
        risk_para = Paragraph(risk_text, risk_style)
        elements.append(risk_para)
        
        # Probability
        prob_text = f"Risk Probability: {probability:.1%}"
        prob_para = Paragraph(prob_text, self.normal_style)
        elements.append(prob_para)
        
        # Prediction result
        prediction = prediction_data.get('prediction', 0)
        if prediction == 1:
            result_text = "🔴 Heart Disease Risk Detected"
            result_style = self.high_risk_style
        else:
            result_text = "🟢 No Heart Disease Risk Detected"
            result_style = self.low_risk_style
        
        result_para = Paragraph(result_text, result_style)
        elements.append(result_para)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def create_analysis_section(self, prediction_data: dict):
        """Create detailed analysis section"""
        elements = []
        
        # Section title
        section_title = Paragraph("Detailed Analysis", self.subtitle_style)
        elements.append(section_title)
        
        # Analysis text
        analysis_text = prediction_data.get('explanation', 'Detailed analysis not available.')
        analysis_para = Paragraph(analysis_text, self.normal_style)
        elements.append(analysis_para)
        
        # Feature importance if available
        if 'top_features' in prediction_data:
            elements.append(Spacer(1, 12))
            features_title = Paragraph("Key Contributing Factors:", self.normal_style)
            elements.append(features_title)
            
            for feature, importance in prediction_data['top_features'].items():
                feature_text = f"• {feature}: {importance:.3f}"
                feature_para = Paragraph(feature_text, self.normal_style)
                elements.append(feature_para)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def create_recommendations_section(self, prediction_data: dict):
        """Create recommendations section"""
        elements = []
        
        # Section title
        section_title = Paragraph("Recommendations", self.subtitle_style)
        elements.append(section_title)
        
        risk_level = prediction_data.get('risk_level', 'Unknown')
        
        if 'Low' in risk_level:
            recommendations = [
                "Continue maintaining a healthy lifestyle",
                "Regular check-ups with your doctor",
                "Monitor your health metrics regularly",
                "Maintain a balanced diet and exercise routine",
                "Avoid smoking and excessive alcohol consumption"
            ]
        elif 'Moderate' in risk_level:
            recommendations = [
                "Consult with a healthcare provider",
                "Consider lifestyle modifications (diet, exercise)",
                "Regular monitoring of heart health",
                "Stress management techniques",
                "Consider preventive medications if prescribed"
            ]
        else:
            recommendations = [
                "Immediately consult a healthcare provider",
                "Consider lifestyle changes",
                "Regular medical monitoring",
                "Follow medical advice strictly",
                "Consider cardiac rehabilitation programs"
            ]
        
        for rec in recommendations:
            rec_text = f"• {rec}"
            rec_para = Paragraph(rec_text, self.normal_style)
            elements.append(rec_para)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def create_disclaimer_section(self):
        """Create medical disclaimer section"""
        elements = []
        
        # Section title
        section_title = Paragraph("Important Medical Disclaimer", self.subtitle_style)
        elements.append(section_title)
        
        disclaimer_text = """
        This report is generated by an AI-powered system for educational and screening purposes only. 
        It is not a substitute for professional medical advice, diagnosis, or treatment. 
        Always consult with qualified healthcare professionals for medical decisions.
        
        The accuracy of this assessment depends on the quality and completeness of the provided data. 
        This system should be used as a supplementary tool alongside professional medical evaluation.
        
        For medical emergencies, please contact emergency services immediately.
        """
        
        disclaimer_para = Paragraph(disclaimer_text, self.normal_style)
        elements.append(disclaimer_para)
        
        return elements
    
    def get_chest_pain_description(self, cp_value):
        """Get chest pain type description"""
        descriptions = {
            0: "Typical Angina",
            1: "Atypical Angina", 
            2: "Non-anginal Pain",
            3: "Asymptomatic"
        }
        return descriptions.get(cp_value, "Unknown")
    
    def get_ecg_description(self, ecg_value):
        """Get ECG description"""
        descriptions = {
            0: "Normal",
            1: "ST-T Wave Abnormality",
            2: "Left Ventricular Hypertrophy"
        }
        return descriptions.get(ecg_value, "Unknown")
    
    def get_slope_description(self, slope_value):
        """Get slope description"""
        descriptions = {
            0: "Upsloping",
            1: "Flat",
            2: "Downsloping"
        }
        return descriptions.get(slope_value, "Unknown")
    
    def get_thal_description(self, thal_value):
        """Get thalassemia description"""
        descriptions = {
            0: "Normal",
            1: "Fixed Defect",
            2: "Reversable Defect"
        }
        return descriptions.get(thal_value, "Unknown")

def generate_heart_disease_report(patient_data: dict, prediction_data: dict) -> str:
    """Generate a heart disease assessment report"""
    generator = HeartDiseaseReportGenerator()
    return generator.generate_report(patient_data, prediction_data)

def render_pdf_generator():
    """Render PDF generator interface"""
    st.markdown("## 📄 Generate Report")
    st.markdown("Create a professional PDF report of your heart disease assessment.")
    
    # Check if user has a recent prediction
    if 'last_prediction' in st.session_state:
        prediction_data = st.session_state.last_prediction
        
        st.success("✅ Recent assessment data found!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Assessment Summary:**")
            st.markdown(f"- Risk Level: {prediction_data.get('risk_level', 'Unknown')}")
            st.markdown(f"- Probability: {prediction_data.get('probability', 0):.1%}")
            st.markdown(f"- Prediction: {'Heart Disease Risk' if prediction_data.get('prediction') == 1 else 'No Risk'}")
        
        with col2:
            if st.button("📄 Generate PDF Report", type="primary"):
                with st.spinner("Generating PDF report..."):
                    try:
                        # Generate report
                        report_path = generate_heart_disease_report(
                            prediction_data.get('input_data', {}),
                            prediction_data
                        )
                        
                        # Read the generated PDF
                        with open(report_path, "rb") as pdf_file:
                            pdf_bytes = pdf_file.read()
                        
                        # Provide download button
                        st.success("✅ PDF report generated successfully!")
                        st.download_button(
                            label="📥 Download Report",
                            data=pdf_bytes,
                            file_name=f"heart_disease_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )
                        
                        # Show preview info
                        st.info("📋 Report includes: Patient information, assessment results, detailed analysis, recommendations, and medical disclaimer.")
                        
                    except Exception as e:
                        st.error(f"❌ Error generating report: {str(e)}")
    else:
        st.info("📋 No recent assessment data found. Please complete a heart disease assessment first.")
        if st.button("🔍 Go to Assessment"):
            st.session_state.current_page = "patient"
            st.rerun()
