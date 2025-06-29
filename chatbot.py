import streamlit as st
import random
from datetime import datetime
from pathlib import Path
import sys
import uuid
import sqlite3

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class HealthChatbot:
    def __init__(self):
        # Enhanced health knowledge base
        self.health_knowledge = {
            "oldpeak": "ST Depression (oldpeak) measures the depression of the ST segment on an ECG during exercise compared to rest. Normal values are 0-1mm. Values >2mm may indicate heart disease.",
            "cp": "Chest Pain (cp) types: 0=None, 1=Typical angina, 2=Atypical angina, 3=Non-anginal pain. Higher values indicate more severe chest pain.",
            "trestbps": "Resting Blood Pressure (trestbps) is systolic blood pressure at rest. Normal range: 90-140 mmHg. Values >140 indicate hypertension.",
            "chol": "Cholesterol (chol) is total blood cholesterol. Normal: <200 mg/dL, Borderline: 200-239 mg/dL, High: ≥240 mg/dL.",
            "thalach": "Maximum Heart Rate (thalach) is the highest heart rate achieved during exercise. Normal: 120-200 bpm. Lower values may indicate reduced exercise capacity.",
            "exang": "Exercise Angina (exang): 0=No, 1=Yes. Indicates chest pain during physical activity, a key symptom of coronary artery disease."
        }
        
        # Comprehensive health responses
        self.health_responses = {
            "heart_symptoms": """**Heart Disease Warning Signs:**

🚨 **Emergency Symptoms (Call 911 immediately):**
- Chest pain or pressure
- Shortness of breath
- Pain spreading to arms, neck, jaw
- Cold sweats, nausea, lightheadedness

⚠️ **Other Symptoms:**
- Fatigue
- Swelling in legs/ankles
- Irregular heartbeat
- Dizziness

**Risk Factors:**
- High blood pressure
- High cholesterol
- Diabetes
- Smoking
- Obesity
- Family history
- Age (45+ for men, 55+ for women)

**Prevention Tips:**
- Regular exercise (150 min/week)
- Healthy diet (DASH or Mediterranean)
- No smoking
- Limit alcohol
- Manage stress
- Regular check-ups""",

            "heart_diet": """**Heart-Healthy Diet Guidelines:**

🥗 **Foods to Include:**
- Fruits and vegetables (5+ servings/day)
- Whole grains (oats, brown rice, quinoa)
- Lean proteins (fish, chicken, legumes)
- Healthy fats (olive oil, nuts, avocados)
- Low-fat dairy

❌ **Foods to Limit:**
- Saturated fats (red meat, butter)
- Trans fats (processed foods)
- Sodium (salt) - aim for <2,300mg/day
- Added sugars
- Processed foods

💡 **Tips:**
- Use herbs/spices instead of salt
- Choose lean cuts of meat
- Eat fish 2-3 times/week
- Include fiber-rich foods
- Stay hydrated with water""",

            "heart_exercise": """**Heart-Healthy Exercise Plan:**

🏃‍♂️ **Aerobic Exercise (150 min/week):**
- Walking (brisk pace)
- Jogging/running
- Cycling
- Swimming
- Dancing
- Tennis

💪 **Strength Training (2-3 days/week):**
- Weight lifting
- Resistance bands
- Bodyweight exercises
- Yoga/Pilates

🎯 **Target Heart Rate:**
- Moderate intensity: 50-70% of max HR
- Vigorous intensity: 70-85% of max HR
- Max HR = 220 - your age

⚠️ **Safety Tips:**
- Start slowly and gradually increase
- Warm up and cool down
- Stay hydrated
- Listen to your body
- Consult doctor before starting""",

            "blood_pressure": """**Blood Pressure Guidelines:**

📊 **Normal:** <120/80 mmHg
📈 **Elevated:** 120-129/<80 mmHg
⚠️ **High Stage 1:** 130-139/80-89 mmHg
🚨 **High Stage 2:** ≥140/≥90 mmHg

**Risk Factors:**
- Age
- Family history
- Obesity
- High salt intake
- Stress
- Lack of exercise

**Management:**
- Regular monitoring
- Medication if prescribed
- Lifestyle changes
- Stress reduction
- Regular doctor visits""",

            "cholesterol": """**Cholesterol Guidelines:**

📊 **Total Cholesterol:** <200 mg/dL
✅ **HDL (Good):** >60 mg/dL
❌ **LDL (Bad):** <100 mg/dL
⚠️ **Triglycerides:** <150 mg/dL

**To Lower Cholesterol:**
- Reduce saturated fats
- Increase fiber intake
- Exercise regularly
- Maintain healthy weight
- Consider medication if needed

**Foods that Help:**
- Oats and whole grains
- Fatty fish
- Nuts and seeds
- Olive oil
- Fruits and vegetables""",

            "stress": """**Stress and Heart Health:**

🧠 **Stress affects your heart by:**
- Increasing blood pressure
- Raising heart rate
- Causing inflammation
- Leading to unhealthy habits

**Stress Management Techniques:**
- Deep breathing exercises
- Meditation/mindfulness
- Regular exercise
- Adequate sleep (7-9 hours)
- Social connections
- Hobbies and relaxation
- Professional counseling if needed

**Warning Signs of Stress:**
- Irritability
- Sleep problems
- Fatigue
- Headaches
- Digestive issues

**Remember:** Chronic stress is a risk factor for heart disease. Managing stress is crucial for heart health.""",

            "general_heart": """**Heart Health Overview:**

❤️ **Your heart is a vital muscle that pumps blood throughout your body.**

**Key Functions:**
- Delivers oxygen and nutrients
- Removes waste products
- Maintains blood pressure
- Regulates body temperature

**Heart Disease Types:**
- Coronary artery disease
- Heart failure
- Arrhythmias
- Heart valve problems
- Congenital heart defects

**Prevention is Key:**
- Regular check-ups
- Healthy lifestyle
- Early detection
- Medical treatment when needed

Would you like to know more about specific topics like symptoms, diet, exercise, or risk factors?"""
        }
        
        # Enhanced lifestyle tips
        self.lifestyle_tips = [
            "🏃‍♂️ **Exercise:** Aim for 150 minutes of moderate exercise weekly",
            "🥗 **Diet:** Follow a heart-healthy diet rich in fruits, vegetables, and whole grains",
            "🚭 **Smoking:** Quit smoking to reduce heart disease risk significantly",
            "🍷 **Alcohol:** Limit alcohol intake to moderate levels",
            "😴 **Sleep:** Get 7-9 hours of quality sleep nightly",
            "🧘‍♀️ **Stress:** Practice stress management techniques like meditation",
            "⚖️ **Weight:** Maintain a healthy weight through diet and exercise",
            "🩺 **Checkups:** Regular health checkups and blood pressure monitoring",
            "💧 **Hydration:** Drink plenty of water throughout the day",
            "🧂 **Salt:** Reduce sodium intake to less than 2,300mg per day",
            "🐟 **Omega-3:** Include fatty fish in your diet 2-3 times per week",
            "🌰 **Nuts:** Eat a handful of nuts daily for heart health",
            "🫀 **Blood Pressure:** Monitor your blood pressure regularly",
            "🩸 **Cholesterol:** Get your cholesterol checked annually",
            "🍎 **Fiber:** Include high-fiber foods to lower cholesterol",
            "☕ **Caffeine:** Limit caffeine if you have heart rhythm issues",
            "🌞 **Vitamin D:** Get adequate sunlight or supplements for heart health"
        ]
        
        # Enhanced greetings
        self.greetings = [
            "👋 Hello! I'm your heart health assistant. How can I help you today?",
            "💙 Hi there! I'm here to help with your heart health questions.",
            "🫀 Welcome! I can explain medical terms, interpret results, or share lifestyle tips.",
            "❤️ Hello! I'm your AI heart health companion. Ask me anything about heart health!",
            "🩺 Hi! I can help you understand heart disease, lifestyle tips, and medical terms.",
            "💪 Welcome! I'm your personal heart health advisor. What would you like to know?",
            "🫀 Hello! I can help with heart disease prevention, symptoms, and healthy living tips.",
            "❤️ Hi there! I'm here to support your heart health journey. How can I assist you?"
        ]

    def get_personalized_recommendations(self, user_data=None):
        """Generate personalized recommendations based on user data."""
        if not user_data:
            return "I can provide personalized recommendations once you complete a risk assessment."
        
        recommendations = []
        
        if user_data.get('age', 0) > 65:
            recommendations.append("🕐 **Age Factor:** As you're over 65, consider more frequent health checkups.")
        elif user_data.get('age', 0) > 45:
            recommendations.append("🕐 **Age Factor:** Middle age is crucial for heart health.")
        
        if user_data.get('trestbps', 0) > 140:
            recommendations.append("🩺 **Blood Pressure:** Your elevated blood pressure requires attention.")
        
        if user_data.get('chol', 0) > 240:
            recommendations.append("🩸 **Cholesterol:** High cholesterol detected. Focus on heart-healthy diet.")
        
        if user_data.get('cp', 0) > 1:
            recommendations.append("💔 **Chest Pain:** Significant chest pain requires immediate medical attention.")
        
        if not recommendations:
            recommendations.append("✅ **Good News:** Your current parameters look healthy!")
        
        return "\n\n".join(recommendations)

    def get_response(self, user_input):
        """Generate enhanced chatbot response based on user input."""
        user_input_lower = user_input.lower().strip()
        
        # Check for health term explanations
        for term in self.health_knowledge:
            if term in user_input_lower:
                return self.health_knowledge[term]
        
        # Check for comprehensive health responses
        if any(word in user_input_lower for word in ['symptom', 'sign', 'warning', 'emergency']):
            if any(word in user_input_lower for word in ['heart', 'cardiac', 'chest']):
                return """**Heart Disease Warning Signs:**

🚨 **Emergency Symptoms (Call 911 immediately):**
- Chest pain or pressure
- Shortness of breath
- Pain spreading to arms, neck, jaw
- Cold sweats, nausea, lightheadedness

⚠️ **Other Symptoms:**
- Fatigue
- Swelling in legs/ankles
- Irregular heartbeat
- Dizziness

**Risk Factors:**
- High blood pressure
- High cholesterol
- Diabetes
- Smoking
- Obesity
- Family history
- Age (45+ for men, 55+ for women)

**Prevention Tips:**
- Regular exercise (150 min/week)
- Healthy diet (DASH or Mediterranean)
- No smoking
- Limit alcohol
- Manage stress
- Regular check-ups"""
        
        if any(word in user_input_lower for word in ['diet', 'food', 'nutrition', 'eat', 'meal']):
            if any(word in user_input_lower for word in ['heart', 'healthy']):
                return """**Heart-Healthy Diet Guidelines:**

🥗 **Foods to Include:**
- Fruits and vegetables (5+ servings/day)
- Whole grains (oats, brown rice, quinoa)
- Lean proteins (fish, chicken, legumes)
- Healthy fats (olive oil, nuts, avocados)
- Low-fat dairy

❌ **Foods to Limit:**
- Saturated fats (red meat, butter)
- Trans fats (processed foods)
- Sodium (salt) - aim for <2,300mg/day
- Added sugars
- Processed foods

💡 **Tips:**
- Use herbs/spices instead of salt
- Choose lean cuts of meat
- Eat fish 2-3 times/week
- Include fiber-rich foods
- Stay hydrated with water"""
        
        if any(word in user_input_lower for word in ['exercise', 'workout', 'fitness', 'activity', 'sport']):
            if any(word in user_input_lower for word in ['heart', 'cardio']):
                return """**Heart-Healthy Exercise Plan:**

🏃‍♂️ **Aerobic Exercise (150 min/week):**
- Walking (brisk pace)
- Jogging/running
- Cycling
- Swimming
- Dancing
- Tennis

💪 **Strength Training (2-3 days/week):**
- Weight lifting
- Resistance bands
- Bodyweight exercises
- Yoga/Pilates

🎯 **Target Heart Rate:**
- Moderate intensity: 50-70% of max HR
- Vigorous intensity: 70-85% of max HR
- Max HR = 220 - your age

⚠️ **Safety Tips:**
- Start slowly and gradually increase
- Warm up and cool down
- Stay hydrated
- Listen to your body
- Consult doctor before starting"""
        
        if any(word in user_input_lower for word in ['blood pressure', 'hypertension', 'bp']):
            return """**Blood Pressure Guidelines:**

📊 **Normal:** <120/80 mmHg
📈 **Elevated:** 120-129/<80 mmHg
⚠️ **High Stage 1:** 130-139/80-89 mmHg
🚨 **High Stage 2:** ≥140/≥90 mmHg

**Risk Factors:**
- Age
- Family history
- Obesity
- High salt intake
- Stress
- Lack of exercise

**Management:**
- Regular monitoring
- Medication if prescribed
- Lifestyle changes
- Stress reduction
- Regular doctor visits"""
        
        if any(word in user_input_lower for word in ['cholesterol', 'lipid', 'hdl', 'ldl']):
            return """**Cholesterol Guidelines:**

📊 **Total Cholesterol:** <200 mg/dL
✅ **HDL (Good):** >60 mg/dL
❌ **LDL (Bad):** <100 mg/dL
⚠️ **Triglycerides:** <150 mg/dL

**To Lower Cholesterol:**
- Reduce saturated fats
- Increase fiber intake
- Exercise regularly
- Maintain healthy weight
- Consider medication if needed

**Foods that Help:**
- Oats and whole grains
- Fatty fish
- Nuts and seeds
- Olive oil
- Fruits and vegetables"""
        
        if any(word in user_input_lower for word in ['stress', 'anxiety', 'mental', 'relax']):
            return """**Stress and Heart Health:**

🧠 **Stress affects your heart by:**
- Increasing blood pressure
- Raising heart rate
- Causing inflammation
- Leading to unhealthy habits

**Stress Management Techniques:**
- Deep breathing exercises
- Meditation/mindfulness
- Regular exercise
- Adequate sleep (7-9 hours)
- Social connections
- Hobbies and relaxation
- Professional counseling if needed

**Warning Signs of Stress:**
- Irritability
- Sleep problems
- Fatigue
- Headaches
- Digestive issues

**Remember:** Chronic stress is a risk factor for heart disease. Managing stress is crucial for heart health."""
        
        if any(word in user_input_lower for word in ['heart', 'cardiac', 'cardiovascular']):
            return """**Heart Health Overview:**

❤️ **Your heart is a vital muscle that pumps blood throughout your body.**

**Key Functions:**
- Delivers oxygen and nutrients
- Removes waste products
- Maintains blood pressure
- Regulates body temperature

**Heart Disease Types:**
- Coronary artery disease
- Heart failure
- Arrhythmias
- Heart valve problems
- Congenital heart defects

**Prevention is Key:**
- Regular check-ups
- Healthy lifestyle
- Early detection
- Medical treatment when needed

Would you like to know more about specific topics like symptoms, diet, exercise, or risk factors?"""
        
        # Check for lifestyle tips
        if any(keyword in user_input_lower for keyword in ["lifestyle", "tips", "advice", "healthy", "prevention"]):
            return random.choice(self.lifestyle_tips)
        
        # Check for result interpretation
        if "result" in user_input_lower or "prediction" in user_input_lower or "assessment" in user_input_lower:
            if "last_result" in st.session_state:
                result = st.session_state.last_result
                if result:
                    pred = result['prediction']
                    prob = result['probability']
                    if pred == 1:
                        return f"Your last assessment showed **HIGH RISK** ({prob:.1%}). Please consult a healthcare professional immediately."
                    else:
                        return f"Your last assessment showed **LOW RISK** ({prob:.1%}). Continue maintaining a healthy lifestyle!"
            return "I don't see any recent assessment results. Please complete a risk assessment first."
        
        # Check for greetings
        if any(keyword in user_input_lower for keyword in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            return random.choice(self.greetings)
        
        # Check for help requests
        if any(keyword in user_input_lower for keyword in ["help", "what can you do", "capabilities", "features"]):
            return """I'm your AI heart health assistant! Here's what I can help you with:

💡 **Medical Terms:** Explain terms like 'oldpeak', 'cp', 'trestbps', 'chol', etc.
🏥 **Symptoms:** Heart disease warning signs and emergency symptoms
🥗 **Diet:** Heart-healthy nutrition guidelines
🏃‍♂️ **Exercise:** Fitness plans for heart health
🩺 **Health Topics:** Blood pressure, cholesterol, stress management
📊 **Results:** Interpret your risk assessment results
💬 **Lifestyle:** Personalized tips and recommendations

Just ask me anything about heart health!"""
        
        # Default response with suggestions
        return """I'm here to help with heart health questions! 

You can ask me about:
- Heart disease symptoms and warning signs
- Heart-healthy diet and nutrition
- Exercise and fitness for heart health
- Blood pressure management
- Cholesterol levels
- Stress and mental health
- Medical terms (oldpeak, cp, trestbps, etc.)
- Your assessment results
- Lifestyle tips and advice

What would you like to know more about?"""

def initialize_chatbot():
    """Initialize chatbot session state."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chatbot_initialized" not in st.session_state:
        st.session_state.chatbot_initialized = False

def render_simple_chatbot():
    """Render a simple expandable chatbot."""
    
    # Initialize chatbot
    initialize_chatbot()
    chatbot = HealthChatbot()
    
    # Generate unique keys for this instance
    unique_id = str(uuid.uuid4())[:8]
    
    # Add initial greeting if not already done
    if not st.session_state.chatbot_initialized:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": random.choice(chatbot.greetings),
            "timestamp": datetime.now()
        })
        st.session_state.chatbot_initialized = True
    
    # Create expander for chatbot
    with st.expander("🫀 Heart Health Assistant", expanded=False):
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; color: white; margin-bottom: 15px;'>
            <h4 style='margin: 0;'>💬 Chat with your Heart Health Assistant</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div style='background: #e3f2fd; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: right;'>
                        <strong>You:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='background: #f5f5f5; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                        <strong>Assistant:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Quick action buttons with unique keys
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💡 Tips", key=f"tips_btn_{unique_id}"):
                tip = random.choice(chatbot.lifestyle_tips)
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": "Give me lifestyle tips",
                    "timestamp": datetime.now()
                })
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": tip,
                    "timestamp": datetime.now()
                })
                st.rerun()
        
        with col2:
            if st.button("📊 Results", key=f"results_btn_{unique_id}"):
                response = chatbot.get_response("result")
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": "Explain my results",
                    "timestamp": datetime.now()
                })
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now()
                })
                st.rerun()
        
        with col3:
            if st.button("🎯 Advice", key=f"advice_btn_{unique_id}"):
                # Get user data from session state if available
                user_data = st.session_state.get('user_inputs', {})
                advice = chatbot.get_personalized_recommendations(user_data)
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": "Give me personalized advice",
                    "timestamp": datetime.now()
                })
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": advice,
                    "timestamp": datetime.now()
                })
                st.rerun()
        
        # Additional quick action buttons
        col4, col5, col6 = st.columns(3)
        with col4:
            if st.button("🏥 Symptoms", key=f"symptoms_btn_{unique_id}"):
                response = chatbot.get_response("heart symptoms")
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": "What are heart disease symptoms?",
                    "timestamp": datetime.now()
                })
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now()
                })
                st.rerun()
        
        with col5:
            if st.button("🥗 Diet", key=f"diet_btn_{unique_id}"):
                response = chatbot.get_response("heart diet")
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": "What is a heart-healthy diet?",
                    "timestamp": datetime.now()
                })
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now()
                })
                st.rerun()
        
        with col6:
            if st.button("🏃‍♂️ Exercise", key=f"exercise_btn_{unique_id}"):
                response = chatbot.get_response("heart exercise")
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": "What exercises are good for heart health?",
                    "timestamp": datetime.now()
                })
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now()
                })
                st.rerun()
        
        # Chat input with unique key
        user_input = st.text_input("Type your message:", key=f"chat_input_{unique_id}", placeholder="Ask about heart health...")
        
        # Send button and help button in same row
        col_send, col_help = st.columns([3, 1])
        with col_send:
            if st.button("💬 Send", key=f"send_btn_{unique_id}"):
                if user_input.strip():
                    # Add user message to chat history
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": user_input,
                        "timestamp": datetime.now()
                    })
                    
                    # Get chatbot response
                    response = chatbot.get_response(user_input)
                    
                    # Add chatbot response to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now()
                    })
                    
                    st.rerun()
        
        with col_help:
            if st.button("❓ Help", key=f"help_btn_{unique_id}"):
                help_response = chatbot.get_response("help")
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": "What can you help me with?",
                    "timestamp": datetime.now()
                })
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": help_response,
                    "timestamp": datetime.now()
                })
                st.rerun()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", key=f"clear_btn_{unique_id}"):
            st.session_state.chat_history = []
            st.rerun()

def add_chatbot_to_page():
    """Add the chatbot to the current page."""
    render_simple_chatbot()

def render_chat_interface(consultation_id: int):
    """Redirect to dedicated chat page"""
    # Store consultation ID in session state
    st.session_state.chat_consultation = consultation_id
    
    # Redirect to dedicated chat page
    st.switch_page("pages/chat_page.py")

def render_ai_chatbot():
    """Render AI chatbot for general health questions"""
    # Removed heading to avoid duplicate
    # st.markdown("## 🤖 AI Health Assistant")
    # st.markdown("Ask me general questions about heart health and lifestyle.")
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about heart health..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            response = generate_ai_response(prompt)
            st.markdown(response)
        
        # Add AI response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

def generate_ai_response(prompt: str) -> str:
    """Generate AI response based on user prompt"""
    prompt_lower = prompt.lower()
    
    # Heart health related responses
    if any(word in prompt_lower for word in ['heart', 'cardiac', 'cardiovascular']):
        if any(word in prompt_lower for word in ['symptoms', 'signs', 'warning']):
            return """**Heart Disease Warning Signs:**
            
🚨 **Emergency Symptoms (Call 911 immediately):**
- Chest pain or pressure
- Shortness of breath
- Pain spreading to arms, neck, jaw
- Cold sweats, nausea, lightheadedness

⚠️ **Other Symptoms:**
- Fatigue
- Swelling in legs/ankles
- Irregular heartbeat
- Dizziness

**Risk Factors:**
- High blood pressure
- High cholesterol
- Diabetes
- Smoking
- Obesity
- Family history
- Age (45+ for men, 55+ for women)

**Prevention Tips:**
- Regular exercise (150 min/week)
- Healthy diet (DASH or Mediterranean)
- No smoking
- Limit alcohol
- Manage stress
- Regular check-ups"""
        
        elif any(word in prompt_lower for word in ['diet', 'food', 'nutrition', 'eat']):
            return """**Heart-Healthy Diet Guidelines:**

🥗 **Foods to Include:**
- Fruits and vegetables (5+ servings/day)
- Whole grains (oats, brown rice, quinoa)
- Lean proteins (fish, chicken, legumes)
- Healthy fats (olive oil, nuts, avocados)
- Low-fat dairy

❌ **Foods to Limit:**
- Saturated fats (red meat, butter)
- Trans fats (processed foods)
- Sodium (salt) - aim for <2,300mg/day
- Added sugars
- Processed foods

💡 **Tips:**
- Use herbs/spices instead of salt
- Choose lean cuts of meat
- Eat fish 2-3 times/week
- Include fiber-rich foods
- Stay hydrated with water"""
        
        elif any(word in prompt_lower for word in ['exercise', 'workout', 'fitness', 'activity']):
            return """**Heart-Healthy Exercise Plan:**

🏃‍♂️ **Aerobic Exercise (150 min/week):**
- Walking (brisk pace)
- Jogging/running
- Cycling
- Swimming
- Dancing
- Tennis

💪 **Strength Training (2-3 days/week):**
- Weight lifting
- Resistance bands
- Bodyweight exercises
- Yoga/Pilates

🎯 **Target Heart Rate:**
- Moderate intensity: 50-70% of max HR
- Vigorous intensity: 70-85% of max HR
- Max HR = 220 - your age

⚠️ **Safety Tips:**
- Start slowly and gradually increase
- Warm up and cool down
- Stay hydrated
- Listen to your body
- Consult doctor before starting"""
        
        else:
            return """**Heart Health Overview:**

❤️ **Your heart is a vital muscle that pumps blood throughout your body.**

**Key Functions:**
- Delivers oxygen and nutrients
- Removes waste products
- Maintains blood pressure
- Regulates body temperature

**Heart Disease Types:**
- Coronary artery disease
- Heart failure
- Arrhythmias
- Heart valve problems
- Congenital heart defects

**Prevention is Key:**
- Regular check-ups
- Healthy lifestyle
- Early detection
- Medical treatment when needed

Would you like to know more about specific topics like symptoms, diet, exercise, or risk factors?"""
    
    # General health responses
    elif any(word in prompt_lower for word in ['blood pressure', 'hypertension']):
        return """**Blood Pressure Guidelines:**

📊 **Normal:** <120/80 mmHg
📈 **Elevated:** 120-129/<80 mmHg
⚠️ **High Stage 1:** 130-139/80-89 mmHg
🚨 **High Stage 2:** ≥140/≥90 mmHg

**Risk Factors:**
- Age
- Family history
- Obesity
- High salt intake
- Stress
- Lack of exercise

**Management:**
- Regular monitoring
- Medication if prescribed
- Lifestyle changes
- Stress reduction
- Regular doctor visits"""
    
    elif any(word in prompt_lower for word in ['cholesterol', 'lipid']):
        return """**Cholesterol Guidelines:**

📊 **Total Cholesterol:** <200 mg/dL
✅ **HDL (Good):** >60 mg/dL
❌ **LDL (Bad):** <100 mg/dL
⚠️ **Triglycerides:** <150 mg/dL

**To Lower Cholesterol:**
- Reduce saturated fats
- Increase fiber intake
- Exercise regularly
- Maintain healthy weight
- Consider medication if needed

**Foods that Help:**
- Oats and whole grains
- Fatty fish
- Nuts and seeds
- Olive oil
- Fruits and vegetables"""
    
    elif any(word in prompt_lower for word in ['stress', 'anxiety', 'mental']):
        return """**Stress and Heart Health:**

🧠 **Stress affects your heart by:**
- Increasing blood pressure
- Raising heart rate
- Causing inflammation
- Leading to unhealthy habits

**Stress Management Techniques:**
- Deep breathing exercises
- Meditation/mindfulness
- Regular exercise
- Adequate sleep (7-9 hours)
- Social connections
- Hobbies and relaxation
- Professional counseling if needed

**Warning Signs of Stress:**
- Irritability
- Sleep problems
- Fatigue
- Headaches
- Digestive issues

**Remember:** Chronic stress is a risk factor for heart disease. Managing stress is crucial for heart health."""
    
    else:
        return """I'm here to help with heart health questions! 

You can ask me about:
- Heart disease symptoms and warning signs
- Heart-healthy diet and nutrition
- Exercise and fitness for heart health
- Blood pressure management
- Cholesterol levels
- Stress and mental health
- Risk factors and prevention

What would you like to know more about?"""
