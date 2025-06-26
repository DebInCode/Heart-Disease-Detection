import streamlit as st
import numpy as np
import joblib
from fpdf import FPDF

# Load model and scaler
model = joblib.load('heart_rf_model.pkl')
scaler = joblib.load('scaler.pkl')

st.set_page_config(page_title="Heart Risk Predictor", layout="centered")
st.title("💓 Heart Disease Risk Predictor")

# Tabs
tab1, tab2, tab3 = st.tabs(["🩺 Symptom Checker", "📋 Clinical Form", "📄 Lifestyle & PDF Report"])

# ------------------ TAB 1 ------------------
with tab1:
    st.subheader("🩺 Patient-Friendly Symptom Checker")

    # Initialize session state
    if "step" not in st.session_state:
        st.session_state.step = 0
        st.session_state.symptoms = {}

    step = st.session_state.step
    user_symptoms = st.session_state.symptoms

    # Step-by-step questions
    if step == 0:
        user_symptoms["chest_pain"] = st.radio("Do you experience chest pain?", ["No", "Yes"], key="cp_q")
        next_clicked = st.button("Next")
        if next_clicked:
            st.session_state.step += 1

    elif step == 1:
        user_symptoms["breathless"] = st.radio("Do you get breathless during mild activity?", ["No", "Yes"], key="br_q")
        next_clicked = st.button("Next")
        if next_clicked:
            st.session_state.step += 1

    elif step == 2:
        user_symptoms["fatigue"] = st.radio("Do you feel tired often?", ["No", "Yes"], key="fat_q")
        next_clicked = st.button("Next")
        if next_clicked:
            st.session_state.step += 1

    elif step == 3:
        user_symptoms["age"] = st.slider("What is your age?", 18, 100, 30, key="age_q")
        submit_clicked = st.button("Submit")

        if submit_clicked:
            # Map to model input format
            age = user_symptoms["age"]
            sex = 1  # Default to male
            cp = 2 if user_symptoms["chest_pain"] == "Yes" else 0
            trestbps = 150 if user_symptoms["breathless"] == "Yes" else 120
            chol = 270 if user_symptoms["fatigue"] == "Yes" else 190
            fbs = 1 if age > 50 else 0
            restecg = 1
            thalach = 110 if user_symptoms["fatigue"] == "Yes" else 160
            exang = 1 if user_symptoms["breathless"] == "Yes" else 0
            oldpeak = 3.0 if user_symptoms["chest_pain"] == "Yes" else 0.5
            slope = 1
            ca = 0
            thal = 2

            input_symptom = np.array([[age, sex, cp, trestbps, chol, fbs,
                                       restecg, thalach, exang, oldpeak, slope, ca, thal]])
            scaled = scaler.transform(input_symptom)
            prediction = model.predict(scaled)[0]
            confidence = round(model.predict_proba(scaled)[0][1] * 100, 2)

            # Save results
            st.session_state["last_result"] = prediction
            st.session_state["last_input"] = {
                "Age": age,
                "Chest Pain": user_symptoms["chest_pain"],
                "Breathless": user_symptoms["breathless"],
                "Fatigue": user_symptoms["fatigue"]
            }

            # Display result
            if prediction == 1:
                if confidence >= 75:
                    st.error(f"🔴 High Risk of Heart Disease (Confidence: {confidence}%)")
                else:
                    st.warning(f"🟠 Possible High Risk (Confidence: {confidence}%)")
            else:
                if confidence >= 75:
                    st.success(f"🟢 Low Risk (Confidence: {100 - confidence:.2f}%)")
                else:
                    st.info(f"🟡 Possibly Low Risk (Confidence: {100 - confidence:.2f}%)")

            # Restart form
            if st.button("🔁 Restart Questionnaire"):
                st.session_state.step = 0
                st.session_state.symptoms = {}

# ------------------ TAB 2 ------------------
with tab2:
    st.subheader("📋 Advanced Clinical Input Form")

    # Input fields
    age = st.slider("Age", 18, 100)
    sex = st.radio("Sex", ["Male", "Female"])
    cp = st.selectbox("Chest Pain Type (0–3)", [0, 1, 2, 3])
    trestbps = st.number_input("Resting Blood Pressure", min_value=80, max_value=200)
    chol = st.number_input("Cholesterol", min_value=100, max_value=600)
    fbs = st.radio("Fasting Blood Sugar > 120 mg/dl", [0, 1])
    restecg = st.selectbox("Resting ECG (0–2)", [0, 1, 2])
    thalach = st.number_input("Max Heart Rate Achieved", min_value=60, max_value=250)
    exang = st.radio("Exercise Induced Angina", [0, 1])
    oldpeak = st.number_input("ST Depression", min_value=0.0, max_value=10.0, step=0.1)
    slope = st.selectbox("Slope of Peak Exercise ST", [0, 1, 2])
    ca = st.selectbox("Number of Major Vessels (0–3)", [0, 1, 2, 3])
    thal = st.selectbox("Thalassemia (0–3)", [0, 1, 2, 3])

    if st.button("🧪 Predict from Medical Data", key="clinical_predict"):
        # Convert input into numpy array
        input_clinical = np.array([[
            age,
            1 if sex == "Male" else 0,
            cp,
            trestbps,
            chol,
            fbs,
            restecg,
            thalach,
            exang,
            oldpeak,
            slope,
            ca,
            thal
        ]])

        # Scale input
        scaled_clinical = scaler.transform(input_clinical)

        # Step 1: Predict using model
        prediction = model.predict(scaled_clinical)[0]
        proba = model.predict_proba(scaled_clinical)[0]
        confidence = round(max(proba) * 100, 2)

        # Step 2: Rule-based override for clearly high-risk
        if oldpeak > 6 or thalach < 80:
            prediction = 1
            confidence = 95.0

        # Step 3: Rule-based override for clearly healthy low-risk cases
        elif (
            prediction == 1 and
            age < 35 and
            oldpeak < 1.5 and
            thalach > 150 and
            chol < 220 and
            trestbps < 130 and
            ca == 0 and
            cp == 0
        ):
            prediction = 0
            confidence = 70.0

        # Save to session
        st.session_state["last_result"] = prediction
        st.session_state["last_input"] = {
            "Age": age,
            "Sex": sex,
            "BP": trestbps,
            "Cholesterol": chol,
            "Heart Rate": thalach,
            "ST Depression": oldpeak
        }

        # Display result
        if prediction == 1:
            if confidence >= 85:
                st.error(f"🔴 High Risk (Confidence: {confidence}%)")
            else:
                st.warning(f"🟠 Possible High Risk (Confidence: {confidence}%).\n⚠️ Please consult a doctor.")
        else:
            if confidence >= 65:
                st.success(f"🟢 Low Risk (Confidence: {confidence}%)")
            else:
                st.info(f"🟡 Possibly Low Risk (Confidence: {confidence}%).\n⚠️ Monitor health and consider testing.")

# ------------------ TAB 3 ------------------
import io  # make sure this is at top of your script

with tab3:
    st.subheader("📄 Your Lifestyle Report")

    if "last_result" not in st.session_state:
        st.info("⚠️ Please make a prediction first in Tab 1 or Tab 2.")
    else:
        result = st.session_state["last_result"]
        user_info = st.session_state["last_input"]

        risk_msg = "High Risk" if result == 1 else "Low Risk"
        st.write("### 👤 Summary of Your Inputs")
        for k, v in user_info.items():
            st.write(f"- **{k}**: {v}")

        st.write("### 📊 Prediction Outcome")
        st.write(f"**Risk Level**: `{risk_msg}`")

        # Tips
        food_tips = [
            "Eat leafy greens, berries, oats, and salmon.",
            "Avoid fried foods, red meat, and sugar."
        ]
        yoga_tips = [
            "Practice Anulom Vilom and Bhramari daily.",
            "Do Ardha Matsyendrasana, Vajrasana, and Shavasana."
        ]
        mandatory_tips = [
            "Walk at least 30 mins/day.",
            "Sleep 7-8 hours regularly.",
            "Reduce salt & stress."
        ]

        # Display on screen
        for section, tips in [("Food Recommendations", food_tips), ("Yoga Asanas", yoga_tips), ("Daily Habits", mandatory_tips)]:
            st.write(f"### {section}")
            for tip in tips:
                st.write(f"- {tip}")

        # ⬇️ Download PDF
        if st.button("📅 Generate PDF Report", key="pdf_generate"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Heart Health Risk Report", ln=True, align='C')
            pdf.ln(10)

            pdf.set_font("Arial", size=10)
            pdf.cell(200, 10, txt=f"Prediction Result: {risk_msg}", ln=True)
            pdf.ln(5)
            pdf.cell(200, 10, txt="User Inputs:", ln=True)
            for k, v in user_info.items():
                pdf.cell(200, 8, txt=f"- {k}: {v}", ln=True)

            pdf.ln(5)
            pdf.cell(200, 10, txt="Recommendations:", ln=True)
            for section, tips in [("Food", food_tips), ("Yoga", yoga_tips), ("Habits", mandatory_tips)]:
                pdf.cell(200, 8, txt=f"--- {section} ---", ln=True)
                for tip in tips:
                    # Remove emojis from PDF (optional)
                    clean_tip = tip.encode('ascii', 'ignore').decode('ascii')
                    pdf.cell(200, 8, txt=f"- {clean_tip}", ln=True)

            # ✅ Write PDF to in-memory buffer correctly
            buffer = io.BytesIO()
            buffer.write(pdf.output(dest='S').encode('latin1'))
            buffer.seek(0)

            st.download_button(
                label="⬇️ Download Report",
                data=buffer,
                file_name="Heart_Risk_Report.pdf",
                mime="application/pdf"
            )
