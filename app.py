import streamlit as st
import numpy as np
import pandas as pd
import time
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="SenseGuard Enterprise",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. PROFESSIONAL CSS STYLING ---
st.markdown("""
    <style>
    /* Dark Theme Setup */
    .stApp {
        background-color: #0F172A; /* Deep Space Blue */
        color: white;
    }
    
    /* Metrics Styling */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 15px;
        border-radius: 10px;
        color: white;
    }
    
    /* Header Styling */
    h1, h2, h3 {
        color: #F8FAFC !important;
        font-family: sans-serif;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1E293B;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. AUTHENTICATION (FIXED) ---
def check_password():
    """Simple and secure password check."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    def password_entered():
        if st.session_state["username"] == "admin" and st.session_state["password"] == "1234":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            # --- FIX: FORCE RERUN IMMEDIATELY TO CLEAR LOGIN SCREEN ---
            st.rerun()
        else:
            st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        # Login Screen
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown("<h1 style='text-align: center; color: #38BDF8;'>🛡️ SenseGuard Access</h1>", unsafe_allow_html=True)
            st.text_input("Operator ID", key="username")
            st.text_input("Access Key", type="password", key="password")
            st.button("Authenticate", on_click=password_entered, type="primary", use_container_width=True)
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("⛔ ACCESS DENIED")
        return False
    return True

# --- 4. MAIN APPLICATION ---
# The dashboard code ONLY runs if check_password() is True
if check_password():
    
    # --- HEADER ---
    st.markdown("""
        <div style='text-align: center; margin-bottom: 25px;'>
            <h1 style='margin:0; font-size: 2.5rem;'>🛡️ SENSEGUARD <span style='color: #38BDF8;'>ENTERPRISE</span></h1>
            <p style='color: #94A3B8;'>Real-Time Industrial Anomaly Detection Engine</p>
        </div>
    """, unsafe_allow_html=True)

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Control Panel")
        noise_level = st.slider("Signal Noise", 0.0, 1.0, 0.2, help="Increases random interference")
        refresh_rate = st.slider("Polling Rate", 0.1, 1.0, 0.2)
        
        st.divider()
        run = st.toggle("🔴 LIVE MONITORING", value=True)
        
        if st.button("🔄 Reset System"):
            st.session_state['data_temp'] = []
            st.session_state['data_vib'] = []
            st.session_state['logs'] = []
            st.rerun()
            
        if st.button("🔒 Secure Logout"):
            st.session_state["password_correct"] = False
            st.rerun()

    # --- INITIALIZE STATE ---
    if 'data_temp' not in st.session_state: 
        st.session_state['data_temp'] = [65.0 + np.random.normal(0,0.5) for _ in range(50)]
    if 'data_vib' not in st.session_state: 
        st.session_state['data_vib'] = [20.0 + np.random.normal(0,0.5) for _ in range(50)]
    if 'logs' not in st.session_state: 
        st.session_state['logs'] = []

    # --- DATA GENERATION (The "Engine") ---
    if run:
        # 1. Temperature (Slow moving)
        new_temp = 65.0 + np.random.normal(0, 0.2) + (noise_level * 5)
        
        # 2. Vibration (Fast moving + Spikes)
        new_vib = 20.0 + np.random.normal(0, 1.0)
        
        # Inject Anomaly Logic
        anomaly = False
        if np.random.rand() < noise_level: 
            new_vib += 40  # Big Spike
            anomaly = True
            
        # Update Lists
        st.session_state['data_temp'].append(new_temp)
        st.session_state['data_vib'].append(new_vib)
        
        # Maintain Buffer
        if len(st.session_state['data_temp']) > 80:
            st.session_state['data_temp'].pop(0)
            st.session_state['data_vib'].pop(0)
            
        # Logging
        if anomaly:
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state['logs'].insert(0, f"[{timestamp}] ⚠️ CRITICAL: Vibration Spike {new_vib:.1f}Hz")

    # --- DASHBOARD LAYOUT ---
    
    # 1. KPI Metrics
    k1, k2, k3, k4 = st.columns(4)
    cur_t = st.session_state['data_temp'][-1]
    cur_v = st.session_state['data_vib'][-1]
    
    k1.metric("Core Temperature", f"{cur_t:.1f}°C", "Stable")
    
    if cur_v > 40:
        k2.metric("Vibration Sensor", f"{cur_v:.1f} Hz", "Critical", delta_color="inverse")
    else:
        k2.metric("Vibration Sensor", f"{cur_v:.1f} Hz", "Nominal", delta_color="normal")
        
    k3.metric("System Uptime", "99.99%", "Optimal")
    k4.metric("Active Threads", "4", "Healthy")

    st.markdown("---")

    # 2. Charts Area
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("📡 Multi-Sensor Telemetry")
        chart_df = pd.DataFrame({
            'Temperature': st.session_state['data_temp'],
            'Vibration': st.session_state['data_vib']
        })
        st.line_chart(chart_df, color=["#F43F5E", "#38BDF8"], height=350)
        
    with c2:
        st.subheader("📝 Audit Log")
        if len(st.session_state['logs']) > 0:
            for log in st.session_state['logs'][:7]:
                st.code(log, language="text")
        else:
            st.info("System initializing... No events logged.")

    # 3. Status Footer
    if cur_v > 40:
        st.error(f"⚠️ HIGH VIBRATION DETECTED ({cur_v:.1f} Hz) - AUTOMATED DAMPENING ACTIVE")
    else:
        st.success("✅ ALL SYSTEMS OPERATIONAL")

    # --- AUTO-UPDATE ---
    if run:
        time.sleep(refresh_rate)
        st.rerun()
