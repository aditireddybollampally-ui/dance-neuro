import streamlit as st
import pandas as pd
import os
import json
import random
import time
import threading
import schedule
import smtplib
import requests
import pydeck as pdk
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from streamlit_calendar import calendar
from streamlit_js_eval import get_geolocation

# ==========================================
# PAGE CONF & GLOBAL AESTHETICS
# ==========================================
st.set_page_config(
    page_title="DanceVault | Modular NeuroDance Vault", 
    page_icon="🩰", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Define the "Berry Calming" Palette
PALETTE = {
    "bg": "#FDFBFB",       # Main background
    "card": "#FFFFFF",     # Content cards
    "border": "#EBEDEE",   # Subtle borders
    "text": "#4A3E3D",     # Dark brown text
    "caption": "#7A6A68",  # Muted brown captions
    "accent_1": "#CE8127", # Gold/Tan accent
    "accent_2": "#D893A4", # Rose accent
    "accent_3": "#E5A38F", # Peach accent
    "accent_4": "#D8BFCE"  # Lavender accent
}

# Apply Global CSS for fonts, backgrounds, buttons, and inputs
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Great+Vibes&display=swap');

    /* Global aesthetic setup */
    .stApp {{
        background-color: {PALETTE["bg"]};
        color: {PALETTE["text"]};
        font-family: 'Playfair Display', serif;
    }}

    /* Elegant Titles */
    .main-title {{
        font-family: 'Cinzel', serif;
        color: {PALETTE["accent_1"]} !important;
        text-align: center;
        font-weight: 600;
        letter-spacing: 2px;
        font-size: 3.5rem;
        margin-bottom: 0rem;
        padding-top: 1rem;
    }}

    .script-subtitle {{
        font-family: 'Great Vibes', cursive;
        font-size: 2rem !important;
        color: {PALETTE["accent_2"]};
        text-align: center;
        margin-top: -1.2rem;
        margin-bottom: 3rem;
    }}

    h1, h2, h3, h4 {{
        font-family: 'Cinzel', serif !important;
        font-weight: 400;
        color: {PALETTE["accent_2"]} !important;
        margin-top: 2rem;
    }}

    /* Container Aesthetic */
    div[data-testid="stVerticalBlock"] > div:has(div.stExpander),
    div[data-testid="stVerticalBlock"] > div:has(div.stTabs),
    div.login-card {{
        background-color: {PALETTE["card"]};
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.03);
        border: 1px solid {PALETTE["border"]};
    }}

    /* Buttons aesthetic */
    .stButton>button {{
        background: linear-gradient(135deg, {PALETTE["accent_3"]} 0%, {PALETTE["accent_2"]} 100%) !important;
        color: white !important;
        border-radius: 25px !important;
        border: none !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 1px;
        padding: 0.7rem 2.5rem !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(216, 147, 164, 0.3);
        width: 100%;
        margin-top: 1rem;
    }}

    .stButton>button:hover {{
        background: linear-gradient(135deg, {PALETTE["accent_2"]} 0%, {PALETTE["accent_3"]} 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(216, 147, 164, 0.4);
        color: white !important;
    }}
    
    /* Input & Select styling */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {{
        border-radius: 12px !important;
        border: 1px solid {PALETTE["border"]} !important;
        font-family: 'Playfair Display', serif;
        background-color: #f8f9fa !important;
    }}
    
    .stTextInput label, .stTextArea label, .stSelectbox label, .stSlider label {{
        color: {PALETTE["caption"]} !important;
        font-size: 0.9rem !important;
        font-style: italic;
    }}

    /* Navi container aesthetic */
    div[data-testid="stHorizontalBlock"] {{
        background-color: {PALETTE["card"]};
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
        margin-bottom: 2rem;
        border: 1px solid {PALETTE["border"]};
    }}

    /* Calendar aesthetic corrections */
    .fc-theme-standard .fc-scrollgrid {{ border: 1px solid {PALETTE["border"]} !important; }}
    .fc-daygrid-day.fc-day-today {{ background-color: rgba(216, 147, 164, 0.04) !important; }}
    .fc-event {{ border-radius: 6px; padding: 3px; border: none; font-family: 'Cinzel', serif; font-size: 0.8rem; }}

    /* Breathing GUI layout */
    .breathing-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background-color: {PALETTE["card"]};
        padding: 3rem;
        border-radius: 25px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid {PALETTE["border"]};
        margin-top: 2rem;
    }}

    /* Clinic detail card */
    .clinic-card {{
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid {PALETTE["accent_2"]};
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-top: 1.5rem;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# LOCAL DATA & DIRECTORY SETUP
# ==========================================
VAULT_DIR = "./local_dance_vault"
DB_FILE = "./vault_database.json"
USER_DB_FILE = "./users_database.json"
os.makedirs(VAULT_DIR, exist_ok=True)

def load_json(filename, default_type):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return default_type

def save_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def delete_local_entry(entry_id, db_items):
    updated_items = []
    for item in db_items:
        if item.get("id") == entry_id:
            if "path" in item and os.path.exists(item["path"]):
                try:
                    os.remove(item["path"])
                except Exception:
                    pass
        else:
            updated_items.append(item)
    return updated_items

def delete_user_account_completely(target_user_email):
    vault_db = load_json(DB_FILE, [])
    retained_vault_items = []
    for item in vault_db:
        if item.get("user") == target_user_email:
            if "path" in item and os.path.exists(item["path"]):
                try:
                    os.remove(item["path"])
                except Exception:
                    pass
        else:
            retained_vault_items.append(item)
    save_json(retained_vault_items, DB_FILE)

    users_db = load_json(USER_DB_FILE, {})
    if target_user_email in users_db:
        del users_db[target_user_email]
        save_json(users_db, USER_DB_FILE)

def generate_code(): return str(random.randint(100000, 999999))

def geocode_zipcode(zipcode):
    try:
        headers = {"User-Agent": "DanceVault/1.0"}
        url = f"https://nominatim.openstreetmap.org/search?postalcode={zipcode}&country=USA&format=json"
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200 and len(resp.json()) > 0:
            res = resp.json()[0]
            return float(res["lat"]), float(res["lon"])
    except Exception:
        pass
    return None, None

# REAL EMAIL SENDER FUNCTION VIA SMTP
def send_real_email(to_email, code_or_name, purpose="verification"):
    try:
        smtp_email = st.secrets["smtp"]["email"]
        smtp_password = st.secrets["smtp"]["password"]
        
        if purpose in ["verification", "password reset"]:
            subject = f"DanceVault - Your {purpose.capitalize()} Code"
            body = f"""Hello,

Your security code for {purpose} is: {code_or_name}

If you did not request this code, please ignore this email.

Best regards,
DanceVault Team
"""
        elif purpose == "welcome":
            subject = "Welcome to DanceVault! ✨ Your Account is Active"
            body = f"""Hello {code_or_name},

Welcome to DanceVault! Your account has been successfully verified and created.

You can now log in anytime to track your rehearsals, log your daily neuro-reflections, practice guided breathing, and explore somatic recovery protocols.

Dance. Track. Breathe. Stretch. Repeat.

Best regards,
DanceVault Team
"""
        elif purpose == "journal_reminder":
            subject = "DanceVault - Time for your daily journal reflection ✨"
            body = f"""Hello Dancer,

This is your gentle reminder from DanceVault to take a moment today to center yourself, log your neuro-reflections, and check your recovery routine!

Dance. Track. Breathe. Stretch. Repeat.

Best regards,
DanceVault Team
"""
        else:
            subject = f"DanceVault Notification"
            body = str(code_or_name)

        msg = MIMEMultipart()
        msg['From'] = f"DanceVault <{smtp_email}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False

# ==========================================
# BACKGROUND SCHEDULER FOR JOURNAL REMINDERS
# ==========================================
def dispatch_daily_reminders():
    users = load_json(USER_DB_FILE, {})
    for email, profile in users.items():
        if profile.get("email_reminders", True) and profile.get("verified", False):
            send_real_email(email, "", purpose="journal_reminder")

def run_scheduler():
    schedule.every().day.at("20:00").do(dispatch_daily_reminders)
    while True:
        schedule.run_pending()
        time.sleep(60)

if "scheduler_started" not in st.session_state:
    st.session_state.scheduler_started = True
    threading.Thread(target=run_scheduler, daemon=True).start()

# ==========================================
# TOP 50 DANCE STYLES LIST
# ==========================================
DANCE_STYLES = [
    "Afrobeat", "Acro Dance", "Bachata", "Ballet", "Ballroom", 
    "Belly Dance", "Bharatanatyam", "Bhangra", "Breakdancing (B-Boying)", "Capoeira", 
    "Cha-Cha", "Clogging", "Contemporary", "Dancehall", "Flamenco", 
    "Folk Dance", "Fox Trot", "Garba", "Giddha", "Hip Hop", 
    "House Dance", "Irish Stepdance", "Jazz", "Jazz Funk", "Kathak", 
    "Kathakali", "Kizomba", "K-Pop", "Krumping", "Latin Dance", 
    "Locking", "Lindy Hop", "Merengue", "Modern", "Mohiniyattam", 
    "Odissi", "Popping", "Polka", "Reggaeton", "Rumba", 
    "Salsa", "Samba", "Swing", "Tango", "Tap", 
    "Tribal Fusion", "Tutting", "Vogue / Voguing", "Waltz", "Waacking", "Other"
]

AVATAR_OPTIONS = ["🩰", "💃", "🕺", "🧘", "🧠", "🎭", "✨"]

# ==========================================
# INITIALIZE SESSION STATE
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "auth_page" not in st.session_state: st.session_state.auth_page = "login"
if "verification_code" not in st.session_state: st.session_state.verification_code = ""
if "pending_user" not in st.session_state: st.session_state.pending_user = {}
if "active_section" not in st.session_state: st.session_state.active_section = "studio"
if 'breathing_active' not in st.session_state: st.session_state.breathing_active = False
if 'selected_clinic' not in st.session_state: st.session_state.selected_clinic = None

# ==========================================
# GATEWAY (Sign In / Sign Up)
# ==========================================
if not st.session_state.logged_in:
    st.markdown('<h1 class="main-title">DanceVault</h1>', unsafe_allow_html=True)
    st.markdown('<div class="script-subtitle">Dance. Track. Breathe. Stretch. Repeat.</div>', unsafe_allow_html=True)
    
    col_l, col_center, col_r = st.columns([1, 1.3, 1])
    users = load_json(USER_DB_FILE, {})
    
    with col_center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        if st.session_state.auth_page == "login":
            st.markdown("<h2 style='text-align: center; margin-top:0;'>Welcome Back</h2>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            email_input = st.text_input("Vault ID (Email)", placeholder="your.email@dance.com", key="si_email")
            pass_input = st.text_input("Access Key (Password)", type="password", placeholder="••••••••", key="si_pass")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("OPEN VAULT 🚀", key="btn_login_submit"):
                if email_input in users:
                    if not users[email_input].get("verified", True):
                        st.error("Please verify email first.")
                    elif users[email_input]["password"] == pass_input:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email_input
                        st.success("Vault Opened.")
                        st.rerun()
                    else:
                        st.error("Invalid key.")
                else:
                    st.error("ID not recognized.")
            
            if st.button("Forgot Key?", key="btn_to_fp"):
                st.session_state.auth_page = "forgot_request"
                st.rerun()
                    
            st.markdown(f"<p style='text-align: center; color: {PALETTE['caption']}; font-size: 0.95rem; margin-top: 2rem;'>New to the Vault?</p>", unsafe_allow_html=True)
            if st.button("INITIALIZE ACCOUNT ✨", key="btn_to_signup"):
                st.session_state.auth_page = "signup"
                st.rerun()

        elif st.session_state.auth_page == "signup":
            st.markdown("<h2 style='text-align: center; margin-top:0;'>Initialize Vault</h2>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            new_email = st.text_input("Email", placeholder="your.email@dance.com", key="su_email")
            new_pass = st.text_input("Set Key", type="password", placeholder="Choose wisely", key="su_pass")
            pref_name = st.text_input("Preferred Name", placeholder="e.g., Mia Rao", key="su_prefname")
            primary_style = st.selectbox("Core Dance Style:", DANCE_STYLES, key="su_style")
            want_reminders = st.checkbox("Receive daily email reminders to log my journal", value=True, key="su_reminders")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("REQUEST ACCESS CODE 📩", key="btn_signup_submit"):
                if new_email and new_pass and pref_name:
                    if new_email in users:
                        st.error("ID already exists.")
                    else:
                        code = generate_code()
                        st.session_state.verification_code = code
                        st.session_state.pending_user = {
                            "email": new_email, "password": new_pass, "preferred_name": pref_name,
                            "dance_style": primary_style, "verified": False, "avatar": "🩰",
                            "email_reminders": want_reminders
                        }
                        with st.spinner("Sending verification email..."):
                            if send_real_email(new_email, code, "verification"):
                                st.session_state.auth_page = "verify_signup"
                                st.rerun()
                else:
                    st.error("Please fill all fields.")
                    
            if st.button("Back to Login", key="btn_back_login"):
                st.session_state.auth_page = "login"
                st.rerun()

        elif st.session_state.auth_page == "verify_signup":
            st.markdown("<h3 style='text-align: center;'>Verify Access</h3>", unsafe_allow_html=True)
            st.caption(f"Verification code sent to {st.session_state.pending_user.get('email')}.")
            st.markdown("<br>", unsafe_allow_html=True)
            code_input = st.text_input("6-Digit Code", key="v_code")
            
            if st.button("OPEN YOUR VAULT ✨", key="btn_complete_signup"):
                if code_input.strip() == st.session_state.verification_code:
                    pending = st.session_state.pending_user
                    pending["verified"] = True
                    users[pending["email"]] = pending
                    save_json(users, USER_DB_FILE)
                    
                    send_real_email(pending["email"], pending.get("preferred_name", "Dancer"), purpose="welcome")
                    
                    st.session_state.logged_in = True
                    st.session_state.user_email = pending["email"]
                    st.rerun()
                else:
                    st.error("Invalid code.")

        elif st.session_state.auth_page == "forgot_request":
            st.markdown("<h3 style='text-align: center;'>Reset Key</h3>", unsafe_allow_html=True)
            reset_email = st.text_input("Vault ID (Email)", key="fp_email")
            
            if st.button("SEND RESET CODE", key="btn_fp_submit"):
                if reset_email in users:
                    code = generate_code()
                    st.session_state.verification_code = code
                    st.session_state.user_email = reset_email
                    with st.spinner("Sending reset code..."):
                        if send_real_email(reset_email, code, "password reset"):
                            st.session_state.auth_page = "forgot_verify"
                            st.rerun()
                else:
                    st.error("ID not found.")
            if st.button("Back", key="btn_back_login_fp"):
                st.session_state.auth_page = "login"
                st.rerun()

        elif st.session_state.auth_page == "forgot_verify":
            st.markdown("<h3 style='text-align: center;'>Set New Key</h3>", unsafe_allow_html=True)
            code_input = st.text_input("Reset Code", key="reset_code")
            new_password_input = st.text_input("New Access Key", type="password", key="new_fp_pass")
            
            if st.button("UPDATE KEY", key="btn_update_pass"):
                if code_input.strip() == st.session_state.verification_code:
                    if new_password_input:
                        users[st.session_state.user_email]["password"] = new_password_input
                        save_json(users, USER_DB_FILE)
                        st.success("Updated! Please sign in.")
                        st.session_state.auth_page = "login"
                        st.rerun()
                else:
                    st.error("Invalid code.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# LOAD PROFILE & VAULT DATA
# ==========================================
users_db = load_json(USER_DB_FILE, {})
user_profile = users_db.get(st.session_state.user_email, {})
vault_db_items = load_json(DB_FILE, [])

st.markdown('<h1 class="main-title">DanceVault</h1>', unsafe_allow_html=True)
st.markdown(
    f"<div class='script-subtitle'>Dancehub for {user_profile.get('preferred_name', 'Dancer')} {user_profile.get('avatar', '🩰')}</div>", 
    unsafe_allow_html=True
)

with st.sidebar:
    st.markdown(f"<h2>{user_profile.get('avatar', '🩰')} Vault Access</h2>", unsafe_allow_html=True)
    st.caption(f"ID: {st.session_state.user_email}")
    
    with st.expander("👤 Customize Profile"):
        new_avatar = st.selectbox("Avatar:", AVATAR_OPTIONS, index=AVATAR_OPTIONS.index(user_profile.get("avatar", "🩰")) if user_profile.get("avatar") in AVATAR_OPTIONS else 0)
        new_pref_name = st.text_input("Preferred Name:", value=user_profile.get("preferred_name", ""))
        new_style = st.selectbox("Primary Dance Style:", DANCE_STYLES, index=DANCE_STYLES.index(user_profile.get("dance_style", "Other")) if user_profile.get("dance_style") in DANCE_STYLES else DANCE_STYLES.index("Other"))
        new_reminders = st.checkbox("Receive daily email reminders to log journal", value=user_profile.get("email_reminders", True))
        
        if st.button("SAVE PROFILE CHANGES"):
            user_profile.update({
                "avatar": new_avatar, 
                "preferred_name": new_pref_name, 
                "dance_style": new_style,
                "email_reminders": new_reminders
            })
            users_db[st.session_state.user_email] = user_profile
            save_json(users_db, USER_DB_FILE)
            st.toast("Profile updated aesthetically.", icon="✨")
            st.rerun()
            
    st.divider()
    if st.button("🚪 CLOSE VAULT (Sign Out)"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.auth_page = "login"
        st.rerun()
        
    if st.button("🔴 PERMANENTLY DELETE ACCOUNT", key="btn
