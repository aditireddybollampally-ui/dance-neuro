import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="DanceVault", page_icon="🩰", layout="wide")

VAULT_DIR = "./local_dance_vault"
DB_FILE = "./vault_database.json"
os.makedirs(VAULT_DIR, exist_ok=True)

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

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

# App Title & Tagline
st.markdown("<h1>🩰 DanceVault</h1>", unsafe_allow_html=True)
st.markdown("<div class='script-subtitle'>Dance. Track. Breathe. Stretch. Repeat.</div>", unsafe_allow_html=True)

# Initialize Session State for Section Navigation
if "active_section" not in st.session_state:
    st.session_state.active_section = "choreo"

# Section Navigation Buttons (Acts like custom section tabs)
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

# ==========================================
# SECTION 1: CHOREOGRAPHY + INTERACTIVE CALENDAR
# ==========================================
if st.session_state.active_section == "choreo":
    st.header("Choreography & Media Vault")
    
    col1, col2 = st.columns(2)
    with col1:
        c_style = st.selectbox("Dance Style:", ["Bharathanatyam", "Ballet", "Contemporary", "Hip Hop", "Kathak", "Other"], key="c_style")
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
                "timestamp": timestamp,
                "type": "choreo",
                "date": str(c_date),
                "style": c_style,
                "piece": c_piece.strip(),
                "path": filepath,
                "file_type": ext
            })
            save_db(db)
            st.success(f"Successfully saved choreography for '{c_piece}'!")
        else:
            st.error("Please provide a piece title and upload a media file.")
            
    st.divider()
    st.subheader("📅 Interactive Choreo Calendar & Viewer")
    db = load_db()
    choreo_items = [x for x in db if x.get("type"] == "choreo"]
    
    if choreo_items:
        # Interactive calendar date picker to pull up exact day's choreo records
        selected_calendar_date = st.date_input("Select a Date on the Calendar to View Choreo:", value=datetime.now(), key="cal_choreo_interactive")
        
        filtered_choreo = [item for item in choreo_items if item["date"] == str(selected_calendar_date)]
        
        st.markdown(f"**Showing choreography records for: {selected_calendar_date}**")
        if filtered_choreo:
            for item in filtered_choreo:
                with st.expander(f"🎵 {item['piece']} - {item['style']} ({item['date']})"):
                    if item['file_type'] in ['mp4', 'mov', 'avi']:
                        st.video(item['path'])
                    else:
                        st.audio(item['path'])
        else:
            st.info("No choreography media logged on this specific calendar date.")
    else:
        st.info("No choreography saved yet.")

# ==========================================
# SECTION 2: STRESS JOURNAL & BREATHING
# ==========================================
elif st.session_state.active_section == "stress":
    st.header("Mental Stress Journal & Neuro-Breathing Lounge")
    
    s_date = st.date_input("Log Date:", datetime.now(), key="s_date")
    s_level = st.slider("Mental Strain / Anxiety Level (1-10):", 1, 10, 5, key="s_level")
    s_notes = st.text_area("Mental State Reflection / Journal Entry:", placeholder="e.g., Felt pressured during complex footwork patterns...", key="s_notes")
    
    if st.button("Save Journal Entry 🧠", key="btn_stress"):
        db = load_db()
        db.append({
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "type": "stress",
            "date": str(s_date),
            "stress_level": s_level,
            "notes": s_notes
        })
        save_db(db)
        st.success("Journal entry saved successfully!")
        
    st.divider()
    
    # Breathing Lounge Visualizer
    st.subheader("🌬️ Optional Neuro-Breathing & Calm Audio Lounge")
    st.write("Use this interactive visualizer to synchronize your breathing with calming ambient sound.")
    
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
    st.subheader("📅 Interactive Journal Calendar & Historical View")
    db = load_db()
    stress_items = [x for x in db if x.get("type") == "stress"]
    
    if stress_items:
        selected_journal_date = st.date_input("Select a Date on the Calendar to View Journal Entries:", value=datetime.now(), key="cal_stress_interactive")
        
        filtered_stress = [item for item in stress_items if item["date"] == str(selected_journal_date)]
        
        if filtered_stress:
            for item in filtered_stress:
                st.markdown(f"**📅 Date:** {item['date']} | **Stress Index:** {item['stress_level']}/10")
                st.write(f"*Journal Notes:* {item['notes']}")
                st.divider()
        else:
            st.info("No journal entries recorded on this specific calendar date.")
    else:
        st.info("No journal entries recorded yet.")

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
