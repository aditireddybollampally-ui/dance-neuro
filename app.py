import streamlit as st
import pandas as pd
import os
import json
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

# ==========================================
# CUSTOM AESTHETIC STYLING (Berry Calming Palette)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Great+Vibes&family=Cinzel:wght@400..700&display=swap');

    .stApp {
        background-color: #EDDFD9;
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

    .stButton>button {
        background-color: #D893A4 !important;
        color: #FFFFFF !important;
        border-radius: 20px !important;
        border: none !important;
        font-family: 'Cinzel', serif !important;
        font-size: 14px !important;
        padding: 8px 22px !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(216, 147, 164, 0.3);
        width: 100%;
    }

    .stButton>button:hover {
        background-color: #CE8127 !important;
        color: #FFFFFF !important;
        transform: translateY(-2px);
    }

    .streamlit-expanderHeader {
        background-color: #D8BFCE !important;
        color: #4A3E3D !important;
        border-radius: 10px !important;
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

DANCE_STYLES = ["Bharathanatyam", "Ballet", "Contemporary", "Hip Hop", "Kathak", "Jazz", "Tap", "Other"]
AVATAR_OPTIONS = ["🩰", "💃", "🕺", "🧘", "🧠", "🎭", "✨"]

# If not logged in, render Auth Gateway
if not st.session_state.logged_in:
    st.markdown("<h1>🩰 DanceVault</h1>", unsafe_allow_html=True)
    st.markdown("<div class='script-subtitle'>Dance. Track. Breathe. Stretch. Repeat.</div>", unsafe_allow_html=True)
    
    col_spacer1, col_auth, col_spacer2 = st.columns([1, 1.2, 1])
    
    with col_auth:
        st.markdown("### 🔐 Account Access")
        auth_mode = st.radio("Choose Action:", ["Sign In", "Sign Up with Email", "Forgot Password"], horizontal=True)
        
        users = load_users()
        
        if auth_mode == "Sign In":
            email_input = st.text_input("Email Address", key="si_email")
            pass_input = st.text_input("Password", type="password", key="si_pass")
            
            if st.button("Sign In to Vault 🚀"):
                if email_input in users and users[email_input]["password"] == pass_input:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email_input
                    st.success("Welcome back!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
            
            st.markdown("<div style='text-align: center; margin: 10px 0;'>— OR —</div>", unsafe_allow_html=True)
            if st.button("🔵 Sign in with Google"):
                google_email = "dancer.google@gmail.com"
                if google_email not in users:
                    users[google_email] = {
                        "password": "google_oauth_user",
                        "full_name": "Google User",
                        "preferred_name": "Dancer",
                        "dance_style": "Bharathanatyam",
                        "daily_reminder": True,
                        "avatar": "🩰"
                    }
                    save_users(users)
                st.session_state.logged_in = True
                st.session_state.user_email = google_email
                st.success("Successfully authenticated with Google!")
                st.rerun()

        elif auth_mode == "Sign Up with Email":
            new_email = st.text_input("New Email Address", key="su_email")
            new_pass = st.text_input("Create Password", type="password", key="su_pass")
            full_name = st.text_input("Full Name", key="su_fullname")
            pref_name = st.text_input("Preferred Name", key="su_prefname")
            primary_style = st.selectbox("Primary Dance Style:", DANCE_STYLES, key="su_style")
            daily_reminder = st.checkbox("Enable daily reminders to log rehearsals & mental health", value=True, key="su_reminder")
            
            if st.button("Create Account & Vault ✨"):
                if new_email and new_pass and full_name and pref_name:
                    if new_email in users:
                        st.error("An account with this email already exists. Please Sign In.")
                    else:
                        users[new_email] = {
                            "password": new_pass,
                            "full_name": full_name,
                            "preferred_name": pref_name,
                            "dance_style": primary_style,
                            "daily_reminder": daily_reminder,
                            "avatar": "🩰"
                        }
                        save_users(users)
                        st.session_state.logged_in = True
                        st.session_state.user_email = new_email
                        st.success("Account created successfully!")
                        st.rerun()
                else:
                    st.error("Please fill out all required fields.")
            
            st.markdown("<div style='text-align: center; margin: 10px 0;'>— OR —</div>", unsafe_allow_html=True)
            if st.button("🔵 Sign up with Google"):
                google_email = "dancer.google@gmail.com"
                if google_email not in users:
                    users[google_email] = {
                        "password": "google_oauth_user",
                        "full_name": "Google User",
                        "preferred_name": "Dancer",
                        "dance_style": "Bharathanatyam",
                        "daily_reminder": True,
                        "avatar": "🩰"
                    }
                    save_users(users)
                st.session_state.logged_in = True
                st.session_state.user_email = google_email
                st.success("Successfully signed up with Google!")
                st.rerun()

        elif auth_mode == "Forgot Password":
            reset_email = st.text_input("Enter your registered email", key="fp_email")
            if st.button("Recover Password 🔑"):
                if reset_email in users:
                    st.info(f"Your password is: **{users[reset_email]['password']}**")
                else:
                    st.error("Email not found in database.")

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
        st.rerun()
        
    if st.button("🔴 Delete Account", key="btn_del_acc"):
        if st.session_state.user_email in users_db:
            del users_db[st.session_state.user_email]
            save_users(users_db)
        st.session_state.logged_in = False
        st.session_state.user_email = ""
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
    st.header("Physical Pain & Visual AI Recovery Protocols")
    st.write("Select a specific area of somatic tension to view step-by-step instructions accompanied by reference illustrations.")
    
    ai_recommendations = {
        "Plantar Fascia / Arch": {
            "mechanism": "High impact shock absorption stress (common in classical foot-stamping).",
            "protocol": "1. Myofascial release using a lacrosse ball under the medial longitudinal arch (2 mins).\n2. Eccentric calf drops to unload insertion points.",
            "image": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=600&q=80"
        },
        "Achilles / Calf": {
            "mechanism": "Repetitive rebound acceleration and plantarflexion overload.",
            "protocol": "1. Soleus-focused bent-knee wall stretches.\n2. Dynamic ankle dorsiflexion mobility drills.",
            "image": "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=600&q=80"
        },
        "Lumbar Spine (Lower Back)": {
            "mechanism": "Compensatory extension strain during postural alignment or core fatigue.",
            "protocol": "1. Cat-Camel spinal articulation to reset proprioception.\n2. Dead-bug core stabilization activation.",
            "image": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=600&q=80"
        },
        "Hip Flexors / Hamstrings": {
            "mechanism": "Extreme range-of-motion holding under neuromuscular tension.",
            "protocol": "1. 90/90 hip transitions for internal/external rotation.\n2. PNF contract-relax stretching for hamstrings.",
            "image": "https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=600&q=80"
        },
        "Cervical Spine / Neck & Shoulders": {
            "mechanism": "Sympathetic nervous system elevation translated into upper trapezius tension.",
            "protocol": "1. Vagus nerve stimulation: 4-7-8 diaphragmatic breathing block.\n2. Scapular retraction and thoracic spine rolling.",
            "image": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=600&q=80"
        }
    }
    
    selected_pain = st.selectbox("Select Active Pain Area:", list(ai_recommendations.keys()))
    
    if st.button("Generate Visual Recovery Protocol ⚙️", key="btn_pain"):
        data = ai_recommendations[selected_pain]
        st.markdown(f"### 🎯 Target System: {selected_pain}")
        
        col_img, col_text = st.columns([1, 1.5])
        with col_img:
            st.image(data["image"], caption=f"Recommended Form Reference for {selected_pain}", use_container_width=True)
        with col_text:
            st.info(f"**Biomechanical Analysis:** {data['mechanism']}")
            st.success(f"**Step-by-Step Action Protocol:**\n{data['protocol']}")
