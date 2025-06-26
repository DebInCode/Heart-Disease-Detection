# 💓 Heart Disease Risk Prediction System

An intelligent web-based application that predicts a person’s risk of heart disease based on either **self-reported symptoms** or **advanced clinical inputs**. Built using **Python**, **Streamlit**, and **scikit-learn**, the app also generates personalized lifestyle recommendations and a downloadable PDF health report.

## 🔍 Project Overview

This system is designed to assist users and healthcare professionals in early heart disease detection. It combines **machine learning predictions** with a **user-friendly interface** and **health recommendations** based on input risk level.

### 🚀 Key Features

- **Symptom Checker (Tab 1):**  
  Step-by-step, non-clinical questions for laypersons to estimate heart disease risk.

- **Clinical Form (Tab 2):**  
  Accepts precise clinical data such as BP, cholesterol, ECG, heart rate, etc., for accurate prediction.

- **Risk Classification:**  
  Predicts **High Risk**, **Low Risk**, or **Possible Risk** with a model-backed confidence score.

- **PDF Report Generator (Tab 3):**  
  Generates a downloadable report including:
  - Summary of input data  
  - Diet and food suggestions  
  - Yoga practices  
  - Daily habits to improve heart health

- **Rule-Based Override Logic:**  
  Adds domain-knowledge-based checks to flag cases that the model may miss.

## 🧠 Model Details

- **Machine Learning Model:** Random Forest Classifier  
- **Trained Using:** Preprocessed UCI Heart Disease dataset  
- **Scaling Method:** StandardScaler (applied during training and prediction)  
- **Accuracy on Test Set:** ~99%  
- **Precision:** ~98%  
- **Recall:** ~100%  
- **F1 Score:** ~99%  

## 🛠️ Tech Stack

- **Frontend:** Streamlit  
- **ML Backend:** scikit-learn, NumPy, joblib  
- **PDF Generation:** fpdf  
- **Language:** Python 3.11
  
## ✨ Future Enhancements

- Mobile responsiveness and accessibility  
- Smartwatch or wearable data integration  
- Email-based report delivery  
- More advanced deep learning backend (e.g., XGBoost or DNN)

## 💡 Use Cases

- Preventive screening in rural or remote areas  
- Digital support tools in telemedicine platforms  
- Personal health tracking and wellness monitoring  
- Early detection during routine health checkups


 



