import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="NeuroDance Vault", page_icon="🩰", layout="wide")

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

st.title("🩰 NeuroDance: Modular Recovery & Choreo Vault")
st.markdown("*A modular local web tool designed to independently track choreography, mental stress, and somatic pain.*")

# Creating separate standalone tabs as requested
tab_choreo, tab_stress, tab_pain = st.tabs(["📹 Log Choreography", "🧠 Stress Tracker", "🧘 Pain & AI Recovery"])

# ==========================================
# TAB 1: LOG CHOREOGRAPHY ONLY
# ==========================================
with tab_choreo:
    st.header("Choreography & Media Upload")
    st.write("Log your piece, date, and save your practice videos or audio files locally without touching stress or pain metrics.")
    
    c_style = st.selectbox("Dance Style:", ["Bharathanatyam", "Ballet", "Contemporary", "Hip Hop", "Kathak", "Other"], key="c_style")
    c_piece = st.text_input("Song / Piece Title:", placeholder="e.g., Tillana, Swan Lake", key="c_piece")
    c_date = st.date_input("Practice Date:", datetime.now(), key="c_date")
    c_file = st.file_uploader("Upload Rehearsal Media (Saved Locally):", type=["mp4", "mov", "avi", "mp3"], key="c_file")
    
    if st.button("Save Choreography 💾"):
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
    st.subheader("Saved Choreography Archive")
    db = load_db()
    choreo_items = [x for x in db if x.get("type") == "choreo"]
    if choreo_items:
        for item in choreo_items:
            with st.expander(f"🎵 {item['piece']} ({item['date']}) - {item['style']}"):
                if item['file_type'] in ['mp4', 'mov', 'avi']:
                    st.video(item['path'])
                else:
                    st.audio(item['path'])
    else:
        st.info("No choreography saved yet.")

# ==========================================
# TAB 2: STRESS TRACKER ONLY
# ==========================================
with tab_stress:
    st.header("Mental & Performance Stress Tracker")
    st.write("Log how you're feeling mentally—completely independent of your choreography or physical logs.")
    
    s_date = st.date_input("Date:", datetime.now(), key="s_date")
    s_level = st.slider("Mental Strain / Anxiety Level (1-10):", 1, 10, 5, key="s_level")
    s_notes = st.text_area("Mental State Reflection / Thoughts to Unload:", placeholder="e.g., Felt pressured about timing today...", key="s_notes")
    
    if st.button("Log Mental Stress 🧠"):
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
    st.subheader("Past Stress Logs")
    db = load_db()
    stress_items = [x for x in db if x.get("type") == "stress"]
    if stress_items:
        for item in stress_items:
            st.markdown(f"**📅 Date:** {item['date']} | **Stress Index:** {item['stress_level']}/10")
            st.write(f"*Notes:* {item['notes']}")
            st.divider()
    else:
        st.info("No stress logs recorded yet.")

# ==========================================
# TAB 3: PAIN & AI RECOVERY ONLY
# ==========================================
with tab_pain:
    st.header("Physical Pain & AI Recovery Matrix")
    st.write("Select a specific area of somatic tension to immediately trigger your customized neuromuscular recovery protocol.")
    
    ai_recommendations = {
        "Plantar Fascia / Arch": {
            "mechanism": "High impact shock absorption stress (common in classical foot-stamping).",
            "protocol": "1. Myofascial release using a lacrosse ball under the medial longitudinal arch (2 mins).\n2. Eccentric calf drops to unload insertion points."
        },
        "Achilles / Calf": {
            "mechanism": "Repetitive rebound acceleration and plantarflexion overload.",
            "protocol": "1. Soleus-focused bent-knee wall stretches.\n2. Dynamic ankle dorsiflexion mobility drills."
        },
        "Lumbar Spine (Lower Back)": {
            "mechanism": "Compensatory extension strain during postural alignment or core fatigue.",
            "protocol": "1. Cat-Camel spinal articulation to reset proprioception.\n2. Dead-bug core stabilization activation."
        },
        "Hip Flexors / Hamstrings": {
            "mechanism": "Extreme range-of-motion holding under neuromuscular tension.",
            "protocol": "1. 90/90 hip transitions for internal/external rotation.\n2. PNF contract-relax stretching for hamstrings."
        },
        "Cervical Spine / Neck & Shoulders": {
            "mechanism": "Sympathetic nervous system elevation translated into upper trapezius tension.",
            "protocol": "1. Vagus nerve stimulation: 4-7-8 diaphragmatic breathing block.\n2. Scapular retraction and thoracic spine rolling."
        }
    }
    
    selected_pain = st.selectbox("Select Active Pain Area:", list(ai_recommendations.keys()))
    
    if st.button("Generate Recovery Protocol ⚙️"):
        data = ai_recommendations[selected_pain]
        st.markdown(f"### 🎯 Target System: {selected_pain}")
        st.info(f"**Biomechanical Analysis:** {data['mechanism']}")
        st.success(f"**Prescribed Action Protocol:**\n{data['protocol']}")
