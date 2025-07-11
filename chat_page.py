import streamlit as st
import sqlite3
import secrets
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from components.doctor_registry import DoctorRegistry
from components.login_auth import is_doctor

def create_modern_chat_page():
    """Create a modern chat page with all features"""
    
    # Page configuration
    st.set_page_config(
        page_title="HeartCare Chat",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for modern chat interface
    st.markdown("""
    <style>
    .chat-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .message-bubble {
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 70%;
        word-wrap: break-word;
    }
    
    .message-sent {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
        text-align: right;
    }
    
    .message-received {
        background: white;
        color: #333;
        border: 1px solid #e0e0e0;
    }
    
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px 15px 0 0;
        margin-bottom: 0;
    }
    
    .video-call-section {
        background: #e3f2fd;
        border: 2px solid #2196f3;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
    }
    
    .message-time {
        font-size: 10px;
        opacity: 0.7;
        margin-top: 5px;
    }
    
    .message-sender {
        font-weight: bold;
        font-size: 12px;
        margin-bottom: 3px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check if user is logged in
    if 'user_data' not in st.session_state:
        st.error("Please log in to access the chat.")
        st.button("Go to Login", on_click=lambda: st.switch_page("app.py"))
        return
    
    # Get consultation ID from session state
    consultation_id = st.session_state.get('chat_consultation')
    if not consultation_id:
        st.error("No consultation selected for chat.")
        st.button("Back to Dashboard", on_click=lambda: st.switch_page("app.py"))
        return
    
    # Initialize registry
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
    
    if not consultation:
        st.error("Consultation not found.")
        return
    
    # Extract consultation data
    consultation_data = {
        'id': consultation[0],
        'doctor_id': consultation[1],
        'patient_id': consultation[2],
        'consultation_type': consultation[3],
        'consultation_date': consultation[4],
        'consultation_time': consultation[5],
        'duration_minutes': consultation[6] if len(consultation) > 6 else 15,
        'status': consultation[7] if len(consultation) > 7 else 'pending',
        'notes': consultation[8] if len(consultation) > 8 else '',
        'video_call_link': consultation[9] if len(consultation) > 9 else None,
        'doctor_name': consultation[-2],
        'patient_id_from_join': consultation[-1]
    }
    
    # Get patient name
    patient_name = "Unknown Patient"
    users_conn = sqlite3.connect("data/users.db")
    users_cursor = users_conn.cursor()
    users_cursor.execute('SELECT username FROM users WHERE id = ?', (consultation_data['patient_id'],))
    user_result = users_cursor.fetchone()
    if user_result:
        patient_name = user_result[0]
    users_conn.close()
    
    # Chat header
    st.markdown(f"""
    <div class="chat-header">
        <h2>💬 {consultation_data['consultation_type']}</h2>
        <p><strong>Dr. {consultation_data['doctor_name']}</strong> ↔ <strong>{patient_name}</strong></p>
        <p style="font-size: 14px; opacity: 0.9;">Status: {consultation_data['status'].title()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("📋 Details", use_container_width=True):
            st.session_state.show_details = True
    
    with col3:
        if st.button("📞 Video Call", use_container_width=True, type="primary"):
            # Generate video call link if not exists
            if not consultation_data['video_call_link']:
                video_call_link = f"https://meet.jit.si/heartcare-{secrets.token_urlsafe(8)}"
                
                # Update database
                conn = sqlite3.connect(str(registry.db_path))
                cursor = conn.cursor()
                cursor.execute('UPDATE consultations SET video_call_link = ? WHERE id = ?', 
                             (video_call_link, consultation_id))
                conn.commit()
                conn.close()
                
                consultation_data['video_call_link'] = video_call_link
                st.success("Video call link generated!")
            
            # Show video call info
            st.session_state.show_video_call = True
    
    with col4:
        if st.button("😊 Emojis", use_container_width=True):
            st.session_state.show_emoji_picker = True
    
    with col5:
        if st.button("← Back", use_container_width=True):
            if 'chat_consultation' in st.session_state:
                del st.session_state.chat_consultation
            st.switch_page("app.py")
    
    # Show consultation details
    if st.session_state.get('show_details', False):
        st.markdown("### 📋 Consultation Details")
        st.markdown(f"""
        - **Date:** {consultation_data['consultation_date']}
        - **Time:** {consultation_data['consultation_time']}
        - **Duration:** {consultation_data['duration_minutes']} minutes
        - **Type:** {consultation_data['consultation_type']}
        - **Status:** {consultation_data['status'].title()}
        - **Notes:** {consultation_data['notes'] or 'No notes available'}
        """)
        
        if st.button("❌ Close Details"):
            st.session_state.show_details = False
            st.rerun()
        
        st.divider()
    
    # Show video call section
    if st.session_state.get('show_video_call', False) or consultation_data['video_call_link']:
        st.markdown("### 🎥 Video Call")
        if consultation_data['video_call_link']:
            st.markdown(f"""
            <div class="video-call-section">
                <h4>🎥 Join Video Call</h4>
                <p><strong>Link:</strong> <a href="{consultation_data['video_call_link']}" target="_blank">{consultation_data['video_call_link']}</a></p>
                <p style="font-size: 12px; color: #666;">Click the link to join the video call in a new tab</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🎥 Join Call Now"):
                st.markdown(f"""
                <script>
                    window.open('{consultation_data['video_call_link']}', '_blank');
                </script>
                """, unsafe_allow_html=True)
                st.success("Opening video call in new tab...")
        
        if st.button("❌ Close Video Call"):
            st.session_state.show_video_call = False
            st.rerun()
        
        st.divider()
    
    # Emoji picker
    if st.session_state.get('show_emoji_picker', False):
        st.markdown("### 😊 Emojis & Stickers")
        
        # Common emojis
        emojis = ["😊", "😂", "❤️", "👍", "👎", "😢", "😡", "🤔", "👏", "🙏", "💪", "🏥", "💊", "🩺", "❤️‍🩹", "💉"]
        
        cols = st.columns(8)
        for i, emoji in enumerate(emojis):
            with cols[i % 8]:
                if st.button(emoji, key=f"emoji_{i}", use_container_width=True):
                    st.session_state.selected_emoji = emoji
                    st.session_state.show_emoji_picker = False
                    st.rerun()
        
        if st.button("❌ Close Emoji Picker"):
            st.session_state.show_emoji_picker = False
            st.rerun()
        
        st.divider()
    
    # Chat messages container
    st.markdown("### 💬 Messages")
    
    # Get chat messages
    messages = registry.get_chat_messages(consultation_id)
    
    # Create chat container
    chat_container = st.container()
    
    with chat_container:
        if not messages:
            st.info("No messages yet. Start the conversation! 💬")
        else:
            # Display messages in modern chat format
            for i, message in enumerate(messages):
                sender_type = message[3]
                message_text = message[4]
                timestamp = message[5]
                
                # Format timestamp
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%H:%M")
                except:
                    formatted_time = timestamp
                
                # Determine if message is from current user
                current_user_type = 'doctor' if is_doctor() else 'patient'
                is_sent_by_me = sender_type == current_user_type
                
                if is_sent_by_me:
                    st.markdown(f"""
                    <div class="message-bubble message-sent">
                        <div class="message-sender">You</div>
                        <div>{message_text}</div>
                        <div class="message-time">{formatted_time}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    sender_name = consultation_data['doctor_name'] if sender_type == 'doctor' else patient_name
                    st.markdown(f"""
                    <div class="message-bubble message-received">
                        <div class="message-sender">{sender_name}</div>
                        <div>{message_text}</div>
                        <div class="message-time">{formatted_time}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Message input section
    st.markdown("### 📝 Send Message")
    
    # Show selected emoji if any
    if 'selected_emoji' in st.session_state:
        st.info(f"Selected emoji: {st.session_state.selected_emoji}")
        if st.button("Use this emoji"):
            st.session_state.message_with_emoji = st.session_state.selected_emoji
            del st.session_state.selected_emoji
            st.rerun()
    
    # Message input form
    with st.form("send_message_form", clear_on_submit=True):
        # Pre-fill message if emoji was selected
        initial_message = st.session_state.get('message_with_emoji', '')
        if initial_message:
            del st.session_state.message_with_emoji
        
        col_input, col_send = st.columns([4, 1])
        
        with col_input:
            message = st.text_area(
                "Type your message...", 
                height=80, 
                placeholder="Enter your message here...",
                value=initial_message
            )
        
        with col_send:
            send_button = st.form_submit_button("📤 Send", use_container_width=True, type="primary")
        
        if send_button and message.strip():
            sender_id = st.session_state.user_data['user_id']
            sender_type = 'doctor' if is_doctor() else 'patient'
            
            result = registry.send_chat_message(consultation_id, sender_id, sender_type, message)
            if result['success']:
                st.success("Message sent successfully! ✨")
                st.rerun()
            else:
                st.error(f"Failed to send message: {result['message']}")
    
    # Quick message templates
    st.markdown("### 💬 Quick Messages")
    quick_messages = [
        "Hello! How are you feeling today? 😊",
        "Can you describe your symptoms? 🤔",
        "Have you taken your medications? 💊",
        "Any changes in your condition? 📊",
        "I'll review your case and get back to you. 📋",
        "Please schedule a follow-up appointment. 📅",
        "Take care and stay healthy! ❤️",
        "Thank you for the consultation! 🙏"
    ]
    
    cols = st.columns(4)
    for i, quick_msg in enumerate(quick_messages):
        with cols[i % 4]:
            if st.button(quick_msg, key=f"quick_{i}", use_container_width=True):
                st.session_state.quick_message = quick_msg
                st.rerun()
    
    # Use quick message if selected
    if 'quick_message' in st.session_state:
        st.info(f"**Quick message selected:** {st.session_state.quick_message}")
        col_use, col_cancel = st.columns([1, 1])
        with col_use:
            if st.button("Use this message"):
                st.session_state.message_with_emoji = st.session_state.quick_message
                del st.session_state.quick_message
                st.rerun()
        with col_cancel:
            if st.button("Cancel"):
                del st.session_state.quick_message
                st.rerun()

if __name__ == "__main__":
    create_modern_chat_page()
