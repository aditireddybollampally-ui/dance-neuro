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

# Set up the page and visual theme
st.set_page_config(
    page_title="DanceVault | Modular NeuroDance Vault",
    page_icon="🩰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Define the "Berry Calming" Palette
PALETTE = {
    "bg": "#FDFBFB",      # Main background
    "card": "#FFFFFF",     # Content cards
    "border": "#EBEDEE",   # Subtle borders
    "text": "#4A3E3D",     # Dark brown text
    "caption": "#7A6A68",  # Muted brown captions
    "accent_1": "#CE8127", # Gold/Tan accent
    "accent_2": "#D893A4", # Rose accent
    "accent_3": "#E5A38F", # Peach accent
    "accent_4": "#D8BFCE"  # Lavender accent
}

# Apply Global CSS
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Great+Vibes&display=swap');

    .stApp {{
        background-color: {PALETTE["bg"]};
        color: {PALETTE["text"]};
        font-family: 'Playfair Display', serif;
    }}

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

    div[data-testid="stVerticalBlock"] > div:has(div.stExpander),
    div[data-testid="stVerticalBlock"] > div:has(div.stTabs),
    div.login-card {{
        background-color: {PALETTE["card"]};
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.03);
        border: 1px solid {PALETTE["border"]};
    }}

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
