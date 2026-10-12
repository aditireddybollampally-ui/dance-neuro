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

    /* Global Background & Base Font (Yana Regular / Taberna Serif Aesthetic) */
    .stApp {
        background-color: #EDDFD9;
        color: #4A3E3D;
        font-family: 'Playfair Display', 'Yana Regular', 'Taberna Serif', Georgia, serif;
    }

    /* Titles & Headings */
    h1 {
        font-family: 'Cinzel', 'Taberna Serif', serif !important;
        color: #CE8127 !important;
        text-align: center;
        font-weight: 600 !important;
        letter-spacing: 1px;
    }

    h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #D893A4 !important;
    }

    /* Subtitle Tagline (Bickham Script Pro Aesthetic) */
    .script-subtitle {
        font-family: 'Great Vibes', 'Bickham Script Pro', cursive;
        font-size: 28px !important;
        color: #D893A4;
        text-align: center;
        margin-top: -15px;
        margin-bottom: 25px;
    }

    /* Buttons */
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
    }

    .stButton>button:hover {
        background-color: #CE8127 !important;
        color: #FFFFFF !important;
        transform: translateY(-2px);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        justify-content: center;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #D8BFCE !important;
        color: #4A3E3D !important;
        border-radius: 12px 12px 0px 0px !important;
        padding: 10px 20px !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: #E5A38F !important;
        color: #FFFFFF !important;
    }

    /* Expanders & Cards */
    .streamlit-expanderHeader {
        background-color: #D8BFCE !important;
        color: #4A3E3D !important;
        border-radius: 10px !important;
        font-family: 'Playfair Display', serif !important;
    }

    /* Slider / Input Accents */
    div[data-baseweb="slider"] {
        color: #CE8127 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Custom App Title Banner
st.markdown("<h1>🩰 DanceVault</h1>", unsafe_allow_html=True)
st.markdown("<div class='script-subtitle'>Dance. Track. Breathe. Stretch. Repeat.</div>", unsafe_allow_html=True)

# Independent Standalone Tabs
tab_choreo, tab_stress, tab_pain = st.tabs(["📹 Log Choreography & Calendar", "🧠 Stress Tracker & Breathing Lounge", "🧘 Pain & Visual AI Recovery"])

# ==========================================
# TAB 1: CHOREOGRAPHY + CALENDAR
# ==========================================
with tab_choreo:
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
    st.subheader("📅 Choreo Calendar & Archive Viewer")
    db = load_db()
    choreo_items = [x for x in db if x.get("type") == "choreo"]
    
    if choreo_items:
        available_dates = sorted(list(set([item["date"] for item in choreo_items])))
        selected_calendar_date = st.date_input("Filter Choreo Logs by Date:", value=datetime.strptime(available_dates[-1], "%Y-%m-%d").date() if available_dates else datetime.now(), key="cal_choreo")
        
        filtered_choreo = [item for item in choreo_items if item["date"] == str(selected_calendar_date)]
        
        st.markdown(f"**Showing choreography entries for: {selected_calendar_date}**")
        if filtered_choreo:
            for item in filtered_choreo:
                with st.expander(f"🎵 {item['piece']} - {item['style']}"):
                    if item['file_type'] in ['mp4', 'mov', 'avi']:
                        st.video(item['path'])
                    else:
                        st.audio(item['path'])
        else:
            st.info("No choreography media logged on this specific date.")
    else:
        st.info("No choreography saved yet.")

# ==========================================
# TAB 2: STRESS TRACKER + BREATHING LOUNGE
# ==========================================
with tab_stress:
    st.header("Mental Stress Tracker & Neuro-Breathing Lounge")
    
    s_date = st.date_input("Log Date:", datetime.now(), key="s_date")
    s_level = st.slider("Mental Strain / Anxiety Level (1-10):", 1, 10, 5, key="s_level")
    s_notes = st.text_area("Mental State Reflection / Thoughts to Unload:", placeholder="e.g., Felt nervous about performance timing...", key="s_notes")
    
    if st.button("Log Mental Stress 🧠", key="btn_stress"):
        db = load_db()
        db.append({
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "type": "stress",
            "date": str(s_date),
            "stress_level": s_level,
            "notes": s_notes
        })
        save_db(db)
        st.success("Stress log saved successfully!")
        
    st.divider()
    
    # Styled Breathing Lounge using Palettes (#E5A38F, #D8BFCE, #CE8127)
    st.subheader("🌬️ Optional Neuro-Breathing & Calm Audio Lounge")
    st.write("Feeling overwhelmed or stressed post-rehearsal? Use this interactive visualizer to synchronize your breathing with calming ambient sound.")
    
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
    st.subheader("📅 Stress Calendar & Historical View")
    db = load_db()
    stress_items = [x for x in db if x.get("type") == "stress"]
    
    if stress_items:
        s_dates = sorted(list(set([item["date"] for item in stress_items])))
