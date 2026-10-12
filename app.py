import streamlit as st
import pandas as pd
import os
import json
import random
import time
from datetime import datetime
from streamlit_calendar import calendar

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

def generate_code(): return str(random.randint(100000, 999999))
def simulate_email(to_email, code, purpose):
    st.toast(f"📧 Simulation for {to_email}: {purpose.capitalize()} code: {code}", icon="📩")

# ==========================================
# INITIALIZE SESSION STATE
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "auth_page" not in st.session_state: st.session_state.auth_page = "login"
if "verification_code" not in st.session_state: st.session_state.verification_code = ""
if "pending_user" not in st.session_state: st.session_state.pending_user = {}
if "active_section" not in st.session_state: st.session_state.active_section = "choreo"
if 'breathing_active' not in st.session_state: st.session_state.breathing_active = False

DANCE_STYLES = ["Bharathanatyam", "Ballet", "Contemporary", "Hip Hop", "Kathak", "Jazz", "Tap", "Other"]
AVATAR_OPTIONS = ["🩰", "💃", "🕺", "🧘", "🧠", "🎭", "✨"]

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
                    if not users[email_input].get("verified", True): st.error("Please verify email first.")
                    elif users[email_input]["password"] == pass_input:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email_input
                        st.success("Vault Opened.")
                        st.rerun()
                    else: st.error("Invalid key.")
                else: st.error("ID not recognized.")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🔵 Quick Google Access", key="btn_google_login"):
                    g_email = "dancer.google@gmail.com"
                    if g_email not in users:
                        users[g_email] = { "password": "google_oauth_user", "preferred_name": "Dancer", "dance_style": "Other", "verified": True, "avatar": "✨"}
                        save_json(users, USER_DB_FILE)
                    st.session_state.logged_in = True
                    st.session_state.user_email = g_email
                    st.rerun()
            with c2:
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
            primary_style = st.selectbox("Core Style:", DANCE_STYLES, key="su_style")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("REQUEST ACCESS CODE 📩", key="btn_signup_submit"):
                if new_email and new_pass and pref_name:
                    if new_email in users: st.error("ID already exists.")
                    else:
                        code = generate_code()
                        st.session_state.verification_code = code
                        st.session_state.pending_user = {
                            "email": new_email, "password": new_pass, "preferred_name": pref_name,
                            "dance_style": primary_style, "verified": False, "avatar": "🩰"
                        }
                        simulate_email(new_email, code, "verification")
                        st.session_state.auth_page = "verify_signup"
                        st.rerun()
                else: st.error("Please fill all fields.")
                    
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
                    st.session_state.logged_in = True
                    st.session_state.user_email = pending["email"]
                    st.rerun()
                else: st.error("Invalid code.")

        elif st.session_state.auth_page == "forgot_request":
            st.markdown("<h3 style='text-align: center;'>Reset Key</h3>", unsafe_allow_html=True)
            reset_email = st.text_input("Vault ID (Email)", key="fp_email")
            
            if st.button("SEND RESET CODE", key="btn_fp_submit"):
                if reset_email in users:
                    code = generate_code()
                    st.session_state.verification_code = code
                    st.session_state.user_email = reset_email
                    simulate_email(reset_email, code, "password reset")
                    st.session_state.auth_page = "forgot_verify"
                    st.rerun()
                else: st.error("ID not found.")
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
                else: st.error("Invalid code.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# LOAD PROFILE & VAULT DATA
# ==========================================
users_db = load_json(USER_DB_FILE, {})
user_profile = users_db.get(st.session_state.user_email, {})
vault_db_items = load_json(DB_FILE, [])

st.markdown('<h1 class="main-title">DanceVault</h1>', unsafe_allow_html=True)
st.markdown(f"<div class='script-subtitle'>DanceVault Hub for {user_profile.get('avatar', '🩰')} {user_profile.get('preferred_name', 'Dancer')}</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"<h2>{user_profile.get('avatar', '🩰')} Vault Access</h2>", unsafe_allow_html=True)
    st.caption(f"ID: {st.session_state.user_email}")
    
    with st.expander("👤 Customize Profile"):
        new_avatar = st.selectbox("Avatar:", AVATAR_OPTIONS, index=AVATAR_OPTIONS.index(user_profile.get("avatar", "🩰")) if user_profile.get("avatar") in AVATAR_OPTIONS else 0)
        new_pref_name = st.text_input("Preferred Name:", value=user_profile.get("preferred_name", ""))
        new_style = st.selectbox("Primary Style:", DANCE_STYLES, index=DANCE_STYLES.index(user_profile.get("dance_style", "Other")) if user_profile.get("dance_style") in DANCE_STYLES else 0)
        
        if st.button("SAVE PROFILE CHANGES"):
            user_profile.update({"avatar": new_avatar, "preferred_name": new_pref_name, "dance_style": new_style})
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
        
    if st.button("🔴 PERMANENTLY DELETE ACCOUNT", key="btn_del_acc"):
        updated_db = [x for x in vault_db_items if x.get("user") != st.session_state.user_email]
        save_json(updated_db, DB_FILE)
        if st.session_state.user_email in users_db: del users_db[st.session_state.user_email]
        save_json(users_db, USER_DB_FILE)
        st.session_state.logged_in = False
        st.session_state.auth_page = "login"
        st.rerun()

nav_col1, nav_col2, nav_col3 = st.columns(3)
with nav_col1:
    if st.button("📹 MEDIA VAULT", key="nav_choreo"): st.session_state.active_section = "choreo"
with nav_col2:
    if st.button("🧠 NEURO LOUNGE", key="nav_neuro"): st.session_state.active_section = "stress"
with nav_col3:
    if st.button("🧘 AI RECOVERY", key="nav_recovery"): st.session_state.active_section = "pain"

st.markdown("<br>", unsafe_allow_html=True)

calendar_options = {
    "editable": False, "selectable": True,
    "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"},
    "initialView": "dayGridMonth",
    "eventColor": PALETTE["accent_2"],
    "contentHeight": "auto",
}

# ==========================================
# SECTION 1: CHOREOGRAPHY VAULT
# ==========================================
if st.session_state.active_section == "choreo":
    st.markdown("<h2>📹 Media Vault</h2>", unsafe_allow_html=True)
    
    with st.expander("➕ Upload Rehearsal or Piece"):
        c1, c2 = st.columns(2)
        with c1:
            c_piece = st.text_input("Title:", placeholder=" Tillana Rehearsal")
            c_date = st.date_input("Date:", datetime.now())
        with c2:
            c_file = st.file_uploader("Choose Media:", type=["mp4", "mov", "mp3"])
        
        if st.button("SAVE TO VAULT 💾"):
            if c_piece and c_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                ext = c_file.name.split(".")[-1]
                filepath = os.path.join(VAULT_DIR, f"{timestamp}.{ext}")
                with open(filepath, "wb") as f: f.write(c_file.getbuffer())
                    
                vault_db_items.append({
                    "id": timestamp, "type": "choreo", "date": str(c_date),
                    "piece": c_piece.strip(), "path": filepath, "file_type": ext,
                    "user": st.session_state.user_email
                })
                save_json(vault_db_items, DB_FILE)
                st.toast("Media vaulted successfully.", icon="📹")
                st.rerun()

    st.divider()
    user_choreo_items = [x for x in vault_db_items if x.get("type") == "choreo" and x.get("user") == st.session_state.user_email]
    
    events = [{"id": i["id"], "title": f"📹 {i['piece']}", "start": i["date"]} for i in user_choreo_items]
    cal_response = calendar(events=events, options=calendar_options, key="choreo_cal")
    
    item_to_show = None
    if cal_response.get("eventClick"):
        eid = cal_response["eventClick"]["event"]["id"]
        item_to_show = next((x for x in user_choreo_items if x["id"] == eid), None)
    elif cal_response.get("dateClick"):
        d = cal_response["dateClick"]["date"].split("T")[0]
        item_to_show = next((x for x in user_choreo_items if x["date"] == d), None)

    if item_to_show:
        st.markdown(f"### Rehearsal: {item_to_show['piece']}")
        if item_to_show['file_type'] in ['mp4', 'mov']: st.video(item_to_show['path'])
        else: st.audio(item_to_show['path'])
        
        if st.button("🗑️ Delete Media"):
            updated_db = delete_local_entry(item_to_show['id'], vault_db_items)
            save_json(updated_db, DB_FILE)
            st.rerun()

# ==========================================
# SECTION 2: NEURO LOUNGE
# ==========================================
elif st.session_state.active_section == "stress":
    st.markdown("<h2>🧠 NeuroDance Lounge</h2>", unsafe_allow_html=True)
    
    with st.expander("📝 Log Neuro-Reflection"):
        s1, s2 = st.columns([1,3])
        with s1: s_level = st.slider("Mental Strain (1-10):", 1, 10, 5)
        with s2: s_notes = st.text_area("Reflections:", placeholder="Nervous about Footwork complexities...")
        
        if st.button("LOG TO VAULT 🧠"):
            vault_db_items.append({
                "id": str(datetime.now().timestamp()), "type": "stress", 
                "date": str(datetime.now().date()), "stress_level": s_level, 
                "notes": s_notes, "user": st.session_state.user_email
            })
            save_json(vault_db_items, DB_FILE)
            st.toast("Reflection vaulted.", icon="🧠")

    st.divider()
    
    st.subheader("🌬️ Aesthetic Breathing Guide (4-4-4-4)")
    st.write("Center yourself before practice. Focus only on the countdown and your breath.")

    b_col1, b_col2 = st.columns([1, 2.5])
    
    with b_col1:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if not st.session_state.breathing_active:
            if st.button("🚀 START SESSION", key="start_breathing"):
                st.session_state.breathing_active = True
                st.rerun()
        else:
            if st.button("⏹️ STOP", key="stop_breathing"):
                st.session_state.breathing_active = False
                st.rerun()

    with b_col2:
        breathing_placeholder = st.empty()
        
        if st.session_state.breathing_active:
            phases = [
                ("Inhale Deeply", "🌬️", 4), 
                ("Hold", "✋", 4), 
                ("Exhale Slowly", "🧘", 4), 
                ("Rest", "✨", 4)
            ]
            
            with breathing_placeholder.container():
                phase_colors = [PALETTE["accent_1"], PALETTE["accent_2"], PALETTE["accent_3"], PALETTE["accent_4"]]
                st.markdown('<div class="breathing-container">', unsafe_allow_html=True)
                icon_spot = st.empty()
                text_spot = st.empty()
                time_spot = st.empty()
                st.markdown('</div>', unsafe_allow_html=True)

            while st.session_state.breathing_active:
                for idx, (p_text, p_icon, p_secs) in enumerate(phases):
                    if not st.session_state.breathing_active: break
                    color = phase_colors[idx]
                    icon_spot.markdown(f"<h1 style='text-align: center; color: {color}; font-size: 6rem; margin:0;'>{p_icon}</h1>", unsafe_allow_html=True)
                    text_spot.markdown(f"<h2 style='text-align: center; color: {PALETTE['text']}; font-family: Playfair Display, serif; margin-top:1rem;'>{p_text}</h2>", unsafe_allow_html=True)
                    
                    for remaining in range(p_secs, 0, -1):
                        time_spot.markdown(f"<h1 style='text-align: center; color: {color}; font-size: 4rem; margin:0; font-family: Cinzel, serif;'>{remaining}</h1>", unsafe_allow_html=True)
                        time.sleep(1)
                    time.sleep(0.1)
        else:
            breathing_placeholder.info("Click 'Start Session' to begin the guided 4-4-4-4 Neuro-Breathing cycle.")

# ==========================================
# SECTION 3: AI RECOVERY (INFOGRAPHICS)
# ==========================================
elif st.session_state.active_section == "pain":
    st.markdown("<h2>🧘 AI Visual Recovery</h2>", unsafe_allow_html=True)
    st.write("Modular somatic recovery guides based on dance biomechanics.")
    
    RAW_BASE = "https://raw.githubusercontent.com/aditireddybollampally-ui/dance-neuro/main"
    
    ai_recovery_data = {
        "Plantar Fascia (Foot)": {
            "mechanism": "High impact stamping stress (classical dance).",
            "infographic_url": f"{RAW_BASE}/4eb93dc5-a2c3-4676-929e-2d488976471f.jpeg",
            "caption": "Modular guide for myofascial release of the arch."
        },
        "Achilles / Calf": {
            "mechanism": "Repetitive jumps/releve overload.",
            "infographic_url": f"{RAW_BASE}/Agent%20Image%20-%20Design%20a%20clean%20vertical%20step-by-step%20wellness%20infographic%20matching%20the%20layout_%20typogra.png",
            "caption": "Stretching protocols for lower leg tension."
        },
        "Lower Back": {
            "mechanism": "Postural holding strain and core fatigue.",
            "infographic_url": f"{RAW_BASE}/Agent%20Image%20-%20Design%20a%20clean%20vertical%20step-by-step%20wellness%20infographic%20matching%20the%20layout_%20typogra%20(1).png",
            "caption": "Spinal decompression and alignment guides."
        },
        "Hip Flexors": {
            "mechanism": "Extreme range-of-motion holding under neuromuscular tension.",
            "infographic_url": f"{RAW_BASE}/Agent%20Image%20-%20Design%20a%20clean%20vertical%20step-by-step%20wellness%20infographic%20matching%20the%20layout_%20typogra%20(2).png",
            "caption": "Hip mobility and flexor release routines."
        },
        "Neck / Cervical Spine": {
            "mechanism": "Nervous tension translating to upper trapezius strain.",
            "infographic_url": f"{RAW_BASE}/Agent%20Image%20-%20Design%20a%20clean%20vertical%20step-by-step%20wellness%20infographic%20matching%20the%20layout_%20typogra%20(3).png",
            "caption": "Levator scapulae and cervical release techniques."
        }
    }
    
    selected_pain = st.selectbox("Select Area of Tension:", list(ai_recovery_data.keys()))
    
    if selected_pain:
        data = ai_recovery_data[selected_pain]
        st.divider()
        st.markdown(f"<h3 style='color: {PALETTE['text']};'>🎯 Somatic Focus: {selected_pain}</h3>", unsafe_allow_html=True)
        st.caption(f"Biomechanical Context: {data['mechanism']}")
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([0.2, 4, 0.2])
        with col2:
            st.markdown(f"<h4 style='text-align: center; color: {PALETTE['accent_2']};'>Recovery Guide Infographic</h4>", unsafe_allow_html=True)
            st.image(data["infographic_url"], caption=data["caption"], use_column_width=True)
