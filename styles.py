# FILE: styles.py
import streamlit as st

def load_css():
    """
    Mengatur tampilan agar terlihat seperti Dashboard Profesional (Corporate Style).
    Menggunakan warna Navy Blue, Putih, dan Abu-abu.
    """
    st.markdown("""
    <style>
    /* 1. Import Font Modern (Inter) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    /* 2. Reset Global & Background */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1f2937; /* Abu-abu gelap (lebih nyaman di mata daripada hitam pekat) */
        background-color: #f3f4f6; /* Background Abu-abu Muda (Clean Look) */
    }

    /* 3. Header & Judul */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700;
        color: #111827;
        letter-spacing: -0.5px;
    }

    /* 4. Sidebar Professional */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb; /* Garis pemisah halus */
    }

    /* 5. Card UI (Kotak Putih untuk Konten) */
    /* Membuat konten terlihat berada di dalam 'kartu' */
    div.block-container {
        background-color: #ffffff;
        padding: 3rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
    }

    /* 6. Tombol (Flat Design) */
    div.stButton > button {
        background-color: #2563eb; /* Biru Profesional */
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s;
        width: 100%;
    }

    div.stButton > button:hover {
        background-color: #1d4ed8;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* 7. Tabs Minimalis */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #e5e7eb;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: transparent;
        border: none;
        color: #6b7280;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: #2563eb !important;
        border-bottom: 2px solid #2563eb;
    }
    
    /* 8. Menghilangkan padding berlebih di atas */
    .main .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)