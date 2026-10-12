import streamlit as st
import pandas as pd
import os
import json
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from streamlit_calendar import calendar

# Page Configuration
st.set_page_config(page_title="DanceVault", page_icon="🩰", layout="wide")

VAULT_DIR = "./local_dance_vault"
DB_FILE = "./vault_database.json"
USER_DB_FILE = "./users_database.json"
os.makedirs(VAULT_DIR, exist_ok=True)

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            for item in data:
                if "id" not in item:
                    item["id"] = item.get("timestamp", str(datetime.now().timestamp()))
            return data
    return []

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_users():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

def delete_entry(entry_id):
    db = load_db()
    updated_db = []
    for item in db:
        item_id = item.get("id", item.get("timestamp"))
        if item_id == entry_id:
            if "path" in item and os.path.exists(item["path"]):
                try:
                    os.remove(item["path"])
                except Exception:
                    pass
        else:
            updated_db.append(item)
    save_db(updated_db)

# Helper function to generate a 6-digit verification code
def generate_code():
    return str(random.randint(100000, 999999))

# Helper function to simulate/send verification email
def send_verification_email(to_email, code, purpose="verification"):
    # In production, configure standard SMTP parameters or secrets
    # For local testing, code is displayed in an alert and simulated securely
    st.toast(f"📧 [Email Simulation] {purpose.capitalize()} code for {to_email}: {code}", icon="📩")

# ==========================================
# CUSTOM AESTHETIC STYLING (Berry Calming Palette)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Great+Vibes&family=Cinzel:wght@400..700&display=swap');

    .stApp {
        background: linear-gradient(135deg, #EDDFD9 0%, #D8BFCE 50%, #E5A38F 100%);
        color: #4A3E3D;
        font-family: 'Playfair Display', Georgia, serif;
    }

    h1 {
        font-family: 'Cinzel', serif !important;
        color: #CE8127 !important;
        text-align: center;
        font-weight: 600 !important;
        letter-spacing: 1px;
    }

    h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #D893A4 !important;
    }

    .script-subtitle {
        font-family: 'Great Vibes', cursive;
        font-size: 28px !important;
        color: #D893A4;
        text-align: center;
        margin-top: -15px;
        margin-bottom: 25px;
    }

    /* Form Labels & Underline Fields */
    .stTextInput label {
        font-family: 'Playfair Display', serif !important;
        color: #7A6A68 !important;
        font-size: 13px !important;
        text-align: left !important;
        display: block !important;
    }

    .stTextInput input {
        border: none !important;
        border-bottom: 2px solid #D8BFCE !important;
        border-radius: 0px !important;
        background-color: transparent !important;
        color: #4A3E3D !important;
        padding-left: 5px !important;
        font-family: 'Playfair Display', serif !important;
    }

    .stTextInput input:focus {
        border-bottom: 2px solid #CE8127 !important;
        box-shadow: none !important;
    }

    /* Berry Calming Pill Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #E5A38F 0%, #D893A4 100%) !important;
        color: #FFFFFF !important;
        border-radius: 25px !important;
        border: none !important;
        font-family: 'Cinzel', serif !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        padding: 10px 25px !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(216, 147, 164, 0.4);
        width: 100%;
        margin-top: 15px;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #CE8127 0%, #E5A38F 100%) !important;
        color: #FFFFFF !important;
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# AUTHENTICATION STATE MANAGEMENT
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"
if "verification_code" not in st.session_state:
    st.session_state.verification_code = ""
if "pending_user" not in st.session_state:
    st.session_state.pending_user = {}

DANCE_STYLES = ["Bharathanatyam", "Ballet", "Contemporary", "Hip Hop", "Kathak", "Jazz", "Tap", "Other"]
AVATAR_OPTIONS = ["🩰", "💃", "🕺", "🧘", "🧠", "🎭", "✨"]

# If not logged in, render Auth Gateway
if not st.session_state.logged_in:
    st.markdown("<h1>🩰 DanceVault</h1>", unsafe_allow_html=True)
    st.markdown("<div class='script-subtitle'>Dance. Track. Breathe. Stretch. Repeat.</div>", unsafe_allow_html=True)
    
    col_l, col_center, col_r = st.columns([1, 1.2, 1])
    users = load_users()
    
    with col_center:
        # LOGIN SCREEN
        if st.session_state.auth_page == "login":
            st.markdown("<h2 style='text-align: center; color: #4A3E3D;'>Login</h2>", unsafe_allow_html=True)
            
            email_input = st.text_input("Username / Email", placeholder="Type your email", key="si_email")
            pass_input = st.text_input("Password", type="password", placeholder="Type your password", key="si_pass")
            
            col_fp1, col_fp2 = st.columns([1, 1])
            with col_fp2:
                if st.button("Forgot password?", key="btn_to_fp"):
                    st.session_state.auth_page = "forgot_request"
                    st.rerun()
            
            if st.button("LOGIN", key="btn_login_submit"):
                if email_input in users:
                    if not users[email_input].get("verified", True):
                        st.error("Please verify your email address first.")
                    elif users[email_input]["password"] == pass_input:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email_input
                        st.success("Welcome back!")
                        st.rerun()
                    else:
                        st.error("Invalid password.")
                else:
                    st.error("Invalid email address.")
            
            st.markdown("<p style='text-align: center; color: #7A6A68; font-size: 12px; margin-top: 20px;'>Or Sign In Using</p>", unsafe_allow_html=True)
            if st.button("🔵 Google Sign-In", key="btn_google_login"):
                google_email = "dancer.google@gmail.com"
                if google_email not in users:
                    users[google_email] = {
                        "password": "google_oauth_user",
                        "full_name": "Google User",
                        "preferred_name": "Dancer",
                        "dance_style": "Bharathanatyam",
                        "daily_reminder": True,
                        "avatar": "🩰",
                        "verified": True
                    }
                    save_users(users)
                st.session_state.logged_in = True
                st.session_state.user_email = google_email
                st.success("Authenticated with Google!")
                st.rerun()
                    
            st.markdown("<p style='text-align: center; color: #7A6A68; font-size: 12px; margin-top: 25px;'>New to DanceVault?</p>", unsafe_allow_html=True)
            if st.button("SIGN UP", key="btn_to_signup"):
                st.session_state.auth_page = "signup"
                st.rerun()

        # SIGN UP SCREEN
        elif st.session_state.auth_page == "signup":
            st.markdown("<h2 style='text-align: center; color: #4A3E3D;'>Sign Up</h2>", unsafe_allow_html=True)
            
            new_email = st.text_input("Email Address", placeholder="Type your email", key="su_email")
            new_pass = st.text_input("Password", type="password", placeholder="Create password", key="su_pass")
            full_name = st.text_input("Full Name", placeholder="e.g., Maya Rao", key="su_fullname")
            pref_name = st.text_input("Preferred Name", placeholder="e.g., Maya", key="su_prefname")
            primary_style = st.selectbox("Primary Dance Style:", DANCE_STYLES, key="su_style")
            daily_reminder = st.checkbox("Enable daily log reminders", value=True, key="su_reminder")
            
            if st.button("SEND VERIFICATION CODE 📩", key="btn_signup_submit"):
                if new_email and new_pass and full_name and pref_name:
                    if new_email in users:
                        st.error("Account already exists. Please login.")
                    else:
                        code = generate_code()
                        st.session_state.verification_code = code
                        st.session_state.pending_user = {
                            "email": new_email,
                            "password": new_pass,
                            "full_name": full_name,
                            "preferred_name": pref_name,
                            "dance_style": primary_style,
                            "daily_reminder": daily_reminder,
                            "avatar": "🩰",
                            "verified": False
                        }
                        send_verification_email(new_email, code, "account verification")
                        st.session_state.auth_page = "verify_signup"
                        st.rerun()
                else:
                    st.error("Please fill out all fields.")
                    
            if st.button("Back to Login", key="btn_back_login"):
                st.session_state.auth_page = "login"
                st.rerun()

        # VERIFY SIGN UP CODE SCREEN
        elif st.session_state.auth_page == "verify_signup":
            st.markdown("<h2 style='text-align: center; color: #4A3E3D;'>Verify Your Email</h2>", unsafe_allow_html=True)
            st.info(f"A 6-digit verification code was sent to **{st.session_state.pending_user.get('email')}**.")
            
            code_input = st.text_input("Enter 6-Digit Code", placeholder="e.g. 123456", key="v_code")
            
            if st.button("VERIFY & COMPLETE SIGN UP ✨", key="btn_complete_signup"):
                if code_input.strip() == st.session_state.verification_code:
                    pending = st.session_state.pending_user
                    pending["verified"] = True
                    users[pending["email"]] = pending
                    save_users(users)
                    
                    st.session_state.logged_in = True
                    st.session_state.user_email = pending["email"]
                    st.success("Email verified successfully! Welcome to DanceVault.")
                    st.rerun()
                else:
                    st.error("Invalid verification code. Please check your inbox and try again.")
                    
            if st.button("Back", key="btn_back_su"):
                st.session_state.auth_page = "signup"
                st.rerun()

        # FORGOT PASSWORD - REQUEST CODE
        elif st.session_state.auth_page == "forgot_request":
            st.markdown("<h2 style='text-align: center; color: #4A3E3D;'>Reset Password</h2>", unsafe_allow_html=True)
            
            reset_email = st.text_input("Enter Registered Email", placeholder="Type your email", key="fp_email")
            if st.button("SEND RESET CODE 📩", key="btn_fp_submit"):
                if reset_email in users:
                    code = generate_code()
                    st.session_state.verification_code = code
                    st.session_state.user_email = reset_email
                    send_verification_email(reset_email, code, "password reset")
                    st.session_state.auth_page = "forgot_verify"
                    st.rerun()
                else:
                    st.error("Email not found in system.")
                    
            if st.button("Back to Login", key="btn_back_login_fp"):
                st.session_state.auth_page = "login"
                st.rerun()

        # FORGOT PASSWORD - VERIFY CODE & SET NEW PASSWORD
        elif st.session_state.auth_page == "forgot_verify":
            st.markdown("<h2 style='text-align: center; color: #4A3E3D;'>Set New Password</h2>", unsafe_allow_html=True)
            st.info(f"Enter the 6-digit reset code sent to **{st.session_state.user_email}**.")
            
            code_input = st.text_input("Enter 6-Digit Reset Code", placeholder="e.g. 123456", key="reset_code")
            new_password_input = st.text_input("Enter New Password", type="password", placeholder="Type new password", key="new_fp_pass")
            
            if st.button("UPDATE PASSWORD 🔑", key="btn_update_pass"):
                if code_input.strip() == st.session_state.verification_code:
                    if new_password_input:
                        users[st.session_state.user_email]["password"] = new_password_input
                        save_users(users)
                        st.success("Password updated successfully! Please sign in.")
                        st.session_state.auth_page = "login"
                        st.rerun()
                    else:
                        st.error("Please enter a new password.")
                else:
                    st.error("Invalid reset code.")
                    
            if st.button("Back", key="btn_back_fp_req"):
                st.session_state.auth_page = "forgot_request"
                st.rerun()

    st.stop()

# Load User Profile Data
users_db = load_users()
user_profile = users_db.get(st.session_state.user_email, {
    "full_name": "Dancer",
    "preferred_name": "Dancer",
    "dance_style": "Bharathanatyam",
    "daily_reminder": True,
    "avatar": "🩰"
})

# ==========================================
# MAIN DASHBOARD
# ==========================================
st.markdown("<h1>🩰 DanceVault</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='script-subtitle'>Welcome back, {user_profile.get('avatar', '🩰')} {user_profile.get('preferred_name', 'Dancer')} | Dance. Track. Breathe. Stretch. Repeat.</div>", unsafe_allow_html=True)

# SIDEBAR ACCOUNT SETTINGS
st.sidebar.markdown(f"### {user_profile.get('avatar', '🩰')} {user_profile.get('preferred_name', 'Dancer')}'s Vault")
st.sidebar.caption(f"Logged in as: {st.session_state.user_email}")

with st.sidebar.expander("⚙️ Account Settings"):
    new_avatar = st.selectbox("Choose Avatar:", AVATAR_OPTIONS, index=AVATAR_OPTIONS.index(user_profile.get("avatar", "🩰")) if user_profile.get("avatar") in AVATAR_OPTIONS else 0)
    new_pref_name = st.text_input("Preferred Name:", value=user_profile.get("preferred_name", ""))
    new_style = st.selectbox("Primary Dance Style:", DANCE_STYLES, index=DANCE_STYLES.index(user_profile.get("dance_style", "Bharathanatyam")) if user_profile.get("dance_style") in DANCE_STYLES else 0)
    new_reminder = st.checkbox("Daily Log Reminders", value=user_profile.get("daily_reminder", True))
    
    if st.button("Save Profile Settings 💾"):
        user_profile["avatar"] = new_avatar
        user_profile["preferred_name"] = new_pref_name
        user_profile["dance_style"] = new_style
        user_profile["daily_reminder"] = new_reminder
        users_db[st.session_state.user_email] = user_profile
        save_users(users_db)
        st.success("Settings updated!")
        st.rerun()
        
    st.divider()
    if st.button("🚪 Sign Out"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.auth_page = "login"
        st.rerun()
        
    if st.button("🔴 Delete Account", key="btn_del_acc"):
        if st.session_state.user_email in users_db:
            del users_db[st.session_state.user_email]
            save_users(users_db)
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.auth_page = "login"
        st.success("Account deleted.")
        st.rerun()

# Daily Reminder Alert
if user_profile.get("daily_reminder", True):
    st.info("🔔 **Daily Reminder:** Don't forget to log today's rehearsal footage and record your stress reflections!")

# Initialize Navigation State
if "active_section" not in st.session_state:
    st.session_state.active_section = "choreo"

# Section Navigation Buttons
nav_col1, nav_col2, nav_col3 = st.columns(3)
with nav_col1:
    if st.button("📹 Choreography & Calendar"):
        st.session_state.active_section = "choreo"
with nav_col2:
    if st.button("🧠 Stress Journal & Breathing"):
        st.session_state.active_section = "stress"
with nav_col3:
    if st.button("🧘 Pain & Visual AI Recovery"):
        st.session_state.active_section = "pain"

st.divider()

calendar_options = {
    "editable": False,
    "selectable": True,
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth"
    },
    "initialView": "dayGridMonth"
}

# ==========================================
# SECTION 1: CHOREOGRAPHY + CALENDAR
# ==========================================
if st.session_state.active_section == "choreo":
    st.header("Choreography & Media Vault")
    
    col1, col2 = st.columns(2)
    with col1:
        default_idx = DANCE_STYLES.index(user_profile.get("dance_style", "Bharathanatyam")) if user_profile.get("dance_style") in DANCE_STYLES else 0
        c_style = st.selectbox("Dance Style:", DANCE_STYLES, index=default_idx, key="c_style")
        c_piece = st.text_input("Song / Piece Title:", placeholder="e.g., Tillana, Swan Lake", key="c_piece")
        c_date = st.date_input("Practice Date:", datetime.now(), key="c_date")
    with col2:
        c_file = st.file_uploader("Upload Rehearsal Media (Saved Locally):", type=["mp4", "mov", "avi", "mp3"], key="c_file")
    
    if st.button("Save Choreography 💾", key="btn_choreo"):
        if c_piece and c_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = c_file.name.split(".")[-1]
            filename = f"{timestamp}_{c_piece.replace(' ', '_')}.{ext}"
            filepath = os.path.join(VAULT_DIR, filename)
            
            with open(filepath, "wb") as f:
                f.write(c_file.getbuffer())
                
            db = load_db()
            db.append({
                "id": timestamp,
                "timestamp": timestamp,
                "type": "choreo",
                "date": str(c_date),
                "style": c_style,
                "piece": c_piece.strip(),
                "path": filepath,
                "file_type": ext,
                "user": st.session_state.user_email
            })
            save_db(db)
            st.success(f"Successfully saved choreography for '{c_piece}'!")
            st.rerun()
        else:
            st.error("Please provide a piece title and upload a media file.")
            
    st.divider()
    st.subheader("📅 Rehearsal Calendar Grid")
    st.caption("Click directly on any calendar event to view the video or delete the choreography entry.")
    
    db = load_db()
    choreo_items = [x for x in db if x.get("type") == "choreo"]
    
    events = []
    for item in choreo_items:
        item_id = item.get("id", item.get("timestamp"))
        events.append({
            "id": item_id,
            "title": f"📹 {item['piece']}",
            "start": item["date"],
            "end": item["date"],
            "color": "#D893A4"
        })
        
    cal_response = calendar(events=events, options=calendar_options, key="choreo_visual_calendar")
    
    selected_event_id = None
    selected_date = None

    if cal_response.get("eventClick"):
        selected_event_id = cal_response["eventClick"]["event"]["id"]
    elif cal_response.get("dateClick"):
        selected_date = cal_response["dateClick"]["date"].split("T")[0]

    st.divider()
    st.subheader("📹 Rehearsal Viewer & Actions")

    if selected_event_id:
        target_items = [x for x in choreo_items if x.get("id", x.get("timestamp")) == selected_event_id]
        if target_items:
            item = target_items[0]
            item_id = item.get("id", item.get("timestamp"))
            st.markdown(f"### Selected Piece: **{item['piece']}** ({item['style']})")
            st.write(f"**Recorded Date:** {item['date']}")
            
            if item['file_type'] in ['mp4', 'mov', 'avi']:
                st.video(item['path'])
            else:
                st.audio(item['path'])
                
            if st.button(f"🗑️ Delete Choreography '{item['piece']}'", key=f"del_{item_id}"):
                delete_entry(item_id)
                st.success("Choreography entry successfully deleted.")
                st.rerun()

    elif selected_date:
        filtered = [x for x in choreo_items if x["date"] == selected_date]
        if filtered:
            for item in filtered:
                item_id = item.get("id", item.get("timestamp"))
                with st.expander(f"🎵 {item['piece']} - {item['style']} ({item['date']})"):
                    if item['file_type'] in ['mp4', 'mov', 'avi']:
                        st.video(item['path'])
                    else:
                        st.audio(item['path'])
                    if st.button("Delete Entry 🗑️", key=f"del_date_{item_id}"):
                        delete_entry(item_id)
                        st.success("Entry deleted.")
                        st.rerun()
        else:
            st.info("No choreography recorded on this date.")
    else:
        st.info("Click any event on the calendar above to view or delete.")

# ==========================================
# SECTION 2: STRESS JOURNAL + CALENDAR
# ==========================================
elif st.session_state.active_section == "stress":
    st.header("Mental Stress Journal & Neuro-Breathing Lounge")
    
    s_date = st.date_input("Log Date:", datetime.now(), key="s_date")
    s_level = st.slider("Mental Strain / Anxiety Level (1-10):", 1, 10, 5, key="s_level")
    s_notes = st.text_area("Mental State Reflection / Journal Entry:", placeholder="e.g., Felt pressured during complex footwork patterns...", key="s_notes")
    
    if st.button("Save Journal Entry 🧠", key="btn_stress"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        db = load_db()
        db.append({
            "id": timestamp,
            "timestamp": timestamp,
            "type": "stress",
            "date": str(s_date),
            "stress_level": s_level,
            "notes": s_notes,
            "user": st.session_state.user_email
        })
        save_db(db)
        st.success("Journal entry saved successfully!")
        st.rerun()
        
    st.divider()
    
    st.subheader("🌬️ Optional Neuro-Breathing & Calm Audio Lounge")
    breathing_html = """
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; background-color: #D8BFCE; padding: 25px; border-radius: 15px; color: #4A3E3D; text-align: center;">
        <h3 style="margin-bottom: 10px; color: #CE8127; font-family: Georgia, serif;">🧠 Synchronized Brain Breathing</h3>
        <p style="font-size: 14px; color: #4A3E3D;">Inhale as the brain expands. Exhale as it contracts.</p>
        
        <div id="brain-circle" style="width: 140px; height: 140px; background: linear-gradient(135deg, #E5A38F, #D893A4); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 40px; box-shadow: 0 0 25px rgba(229, 163, 143, 0.7); animation: breathe 8s infinite ease-in-out; margin: 20px 0;">
            🧠
        </div>
        
        <p id="breath-instruction" style="font-size: 16px; font-weight: bold; color: #CE8127; margin-top: 5px;">Get Ready...</p>

        <div style="margin-top: 15px; width: 100%;">
            <p style="font-size: 12px; color: #4A3E3D; margin-bottom: 5px;">Optional Calm Background Sound / Lo-Fi Audio:</p>
            <audio controls loop style="width: 100%; border-radius: 8px;">
                <source src="https://actions.google.com/sounds/v1/weather/rain_heavy_loud.ogg" type="audio/ogg">
                Your browser does not support the audio element.
            </audio>
        </div>
    </div>

    <style>
    @keyframes breathe {
        0% { transform: scale(1); background-color: #E5A38F; }
        40% { transform: scale(1.35); background-color: #D893A4; }
        50% { transform: scale(1.35); background-color: #D893A4; }
        100% { transform: scale(1); background-color: #E5A38F; }
    }
    </style>

    <script>
    const instruction = document.getElementById("breath-instruction");
    let phases = ["Inhale deeply (4s)...", "Hold breath (4s)...", "Exhale slowly (4s)...", "Rest (4s)..."];
    let i = 0;
    
    setInterval(() => {
        instruction.innerText = phases[i];
        i = (i + 1) % phases.length;
    }, 4000);
    </script>
    """
    st.components.v1.html(breathing_html, height=380)

    st.divider()
    st.subheader("📅 Journal Calendar Grid")
    st.caption("Click directly on any journal event on the calendar to view or delete entries.")
    
    db = load_db()
    stress_items = [x for x in db if x.get("type") == "stress"]
    
    stress_events = []
    for item in stress_items:
        item_id = item.get("id", item.get("timestamp"))
        stress_events.append({
            "id": item_id,
            "title": f"🧠 Stress: {item['stress_level']}/10",
            "start": item["date"],
            "end": item["date"],
            "color": "#CE8127"
        })
        
    cal_response_stress = calendar(events=stress_events, options=calendar_options, key="stress_visual_calendar")
    
    selected_stress_id = None
    selected_stress_date = None

    if cal_response_stress.get("eventClick"):
        selected_stress_id = cal_response_stress["eventClick"]["event"]["id"]
    elif cal_response_stress.get("dateClick"):
        selected_stress_date = cal_response_stress["dateClick"]["date"].split("T")[0]

    st.divider()
    st.subheader("🧠 Journal Review & Actions")

    if selected_stress_id:
        target_stress = [x for x in stress_items if x.get("id", x.get("timestamp")) == selected_stress_id]
        if target_stress:
            item = target_stress[0]
            item_id = item.get("id", item.get("timestamp"))
            st.markdown(f"**📅 Date:** {item['date']} | **Stress Index:** {item['stress_level']}/10")
            st.write(f"**Journal Entry:** {item['notes']}")
            
            if st.button("🗑️ Delete Journal Entry", key=f"del_st_{item_id}"):
                delete_entry(item_id)
                st.success("Journal entry deleted.")
                st.rerun()

    elif selected_stress_date:
        filtered = [x for x in stress_items if x["date"] == selected_stress_date]
        if filtered:
            for item in filtered:
                item_id = item.get("id", item.get("timestamp"))
                st.markdown(f"**📅 Date:** {item['date']} | **Stress Index:** {item['stress_level']}/10")
                st.write(f"*Journal Notes:* {item['notes']}")
                if st.button("Delete Entry 🗑️", key=f"del_st_date_{item_id}"):
                    delete_entry(item_id)
                    st.success("Entry deleted.")
                    st.rerun()
                st.divider()
        else:
            st.info("No journal entries recorded on this date.")
    else:
        st.info("Click any journal event on the calendar above to view or delete.")

# ==========================================
# SECTION 3: PAIN & VISUAL AI RECOVERY
# ==========================================
elif st.session_state.active_section == "pain":
    st.header("Physical Pain & AI Visual Recovery Protocols")
    st.write("Select a specific area of somatic tension to generate biomechanical explanations, video demonstrations, and step-by-step stretch routines.")
    
    ai_recommendations = {
        "Plantar Fascia / Arch": {
            "mechanism": "High impact shock absorption stress common in classical foot-stamping (e.g., Tatte Adavu).",
            "video_url": "https://www.w3schools.com/html/mov_bbb.mp4",
            "image": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=600&q=80",
            "steps": [
                "**Step 1:** Sit comfortably on a chair or floor and place a lacrosse or massage ball directly beneath the arch of your barefoot.",
                "**Step 2:** Roll the ball gently from the ball of your foot down to your heel, applying light to moderate downward pressure for 60 seconds per side.",
                "**Step 3:** Stand facing a wall and perform eccentric calf drops off the edge of a step, slowly lowering your heels below step level over 4 seconds."
            ]
        },
        "Achilles / Calf": {
            "mechanism": "Repetitive rebound acceleration and plantarflexion overload from quick jumps and releve holdings.",
            "video_url": "https://www.w3schools.com/html/mov_bbb.mp4",
            "image": "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=600&q=80",
            "steps": [
                "**Step 1:** Stand facing a wall with hands placed flat against it at shoulder height.",
                "**Step 2:** Step one leg back, keeping the back heel pinned flat on the floor and back knee bent slightly (targeting the soleus).",
                "**Step 3:** Lean gently into the wall until a deep stretch is felt in the lower calf/Achilles tendon. Hold for 30–45 seconds per side."
            ]
        },
        "Lumbar Spine (Lower Back)": {
            "mechanism": "Compensatory extension strain during upright postural holding (Aramandi/plié alignment) or core fatigue.",
            "video_url": "https://www.w3schools.com/html/mov_bbb.mp4",
            "image": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=600&q=80",
            "steps": [
                "**Step 1:** Start on hands and knees on a soft yoga mat (tabletop position).",
                "**Step 2:** Inhale deeply as you arch your back and tilt your head slightly upward (Cow Pose).",
                "**Step 3:** Exhale as you round your spine toward the ceiling, pulling your belly button toward your back (Cat Pose). Repeat dynamically for 10 breathing cycles."
            ]
        },
        "Hip Flexors / Hamstrings": {
            "mechanism": "Extreme range-of-motion holding under neuromuscular tension during splits and high extensions.",
            "video_url": "https://www.w3schools.com/html/mov_bbb.mp4",
            "image": "https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=600&q=80",
            "steps": [
                "**Step 1:** Begin in a 90/90 seated position on the floor with front and back knees bent at 90-degree angles.",
                "**Step 2:** Rotate your torso toward the front shin, keeping your spine tall, and hold for 30 seconds to open hip rotators.",
                "**Step 3:** Shift into a low lunge with back knee resting on the mat, tucking pelvis slightly forward to lengthen hip flexors."
            ]
        },
        "Cervical Spine / Neck & Shoulders": {
            "mechanism": "Sympathetic nervous system elevation translated into upper trapezius and levator scapulae strain.",
            "video_url": "https://www.w3schools.com/html/mov_bbb.mp4",
            "image": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=600&q=80",
            "steps": [
                "**Step 1:** Sit up tall on a stool or yoga block with shoulders relaxed away from your ears.",
                "**Step 2:** Gently drop your right ear toward your right shoulder while extending your left arm downward at a 45-degree angle.",
                "**Step 3:** Place your right hand gently on top of your head to apply light pressure (no pulling). Hold for 30 seconds per side."
            ]
        }
    }
    
    selected_pain = st.selectbox("Select Active Tension or Soreness Area:", list(ai_recommendations.keys()))
    
    if st.button("Generate Visual Recovery Protocol ⚙️", key="btn_pain"):
        data = ai_recommendations[selected_pain]
        st.markdown(f"### 🎯 Target System: {selected_pain}")
        st.info(f"**Biomechanical Analysis:** {data['mechanism']}")
        
        st.divider()
        col_vid, col_img = st.columns(2)
        
        with col_vid:
            st.subheader("📹 Demonstration Clip")
            st.video(data["video_url"])
            st.caption("AI-assisted movement reference for form execution.")
            
        with col_img:
            st.subheader("🖼️ Form Reference Frame")
            st.image(data["image"], caption=f"Anatomical Focus Alignment for {selected_pain}", use_container_width=True)
            
        st.divider()
        st.subheader("🧘 How To Do The Stretches (Step-by-Step Guide)")
        for step in data["steps"]:
            st.markdown(f"* {step}")
