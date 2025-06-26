import streamlit as st
import numpy as np
import joblib

# Load the model
model = joblib.load('heart_rf_model.pkl')

st.title("💓 Heart Disease Prediction App")

# Collect user inputs
age = st.slider("Age", 18, 100)
sex = st.radio("Sex", ["Male", "Female"])
cp = st.selectbox("Chest Pain Type", [0, 1, 2, 3])
trestbps = st.number_input("Resting Blood Pressure")
chol = st.number_input("Cholesterol")
fbs = st.radio("Fasting Blood Sugar > 120 mg/dl", [0, 1])
restecg = st.selectbox("Resting ECG", [0, 1, 2])
thalach = st.number_input("Max Heart Rate Achieved")
exang = st.radio("Exercise Induced Angina", [0, 1])
oldpeak = st.number_input("ST Depression")
slope = st.selectbox("Slope of Peak Exercise ST", [0, 1, 2])
ca = st.selectbox("Number of Major Vessels", [0, 1, 2, 3])
thal = st.selectbox("Thalassemia", [0, 1, 2, 3])

# Format inputs for model
input_data = np.array([[age, 1 if sex == "Male" else 0, cp, trestbps, chol, fbs,
                        restecg, thalach, exang, oldpeak, slope, ca, thal]])

# Prediction
if st.button("Predict"):
    prediction = model.predict(input_data)
    st.success("🔴 You may have heart disease." if prediction[0] == 1 else "🟢 You are unlikely to have heart disease.")
