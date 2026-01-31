import streamlit as st
import numpy as np
import pandas as pd
import time
from datetime import datetime

# --- 1. ENTERPRISE CONFIGURATION ---
st.set_page_config(
    page_title="SenseGuard Enterprise",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ADVANCED CSS STYLING ---
st.markdown("""
    <style>
    /* Dark Industrial Theme */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Custom Title */
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(#00C9FF, #92FE9D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    /* Card Styling */
    div[data-testid="stMetric"] {
        background-color: #1F2229;
        border: 1px solid #2B303B;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Progress Bar Color */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #00C9FF, #92FE9D);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. AUTHENTICATION ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    def password_entered():
        if st.session_state["username"] == "admin" and st.session_state["password"] == "1234":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        # Login Screen
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align: center;'>🔐 Access Control</h1>", unsafe_allow_html=True)
            st.text_input("Operator ID", key="username")
            st.text_input("Access Key", type="password", key="password")
            st.button("Authenticate", on_click=password_entered, type="primary", use_container_width=True)
        return False
    return True

# --- 4. MAIN APPLICATION ---
if check_password():
    
    # -- HEADER --
    st.markdown("<h1 class='main-title'>🏭 SenseGuard Enterprise</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Industrial IoT Anomaly Detection Suite v2.0</p>", unsafe_allow_html=True)
    
    # -- SIDEBAR CONTROLS --
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/900/900782.png", width=100)
        st.title("Control Panel")
        
        st.subheader("⚙️ Simulation Params")
        noise_level = st.slider("Signal Noise Ratio", 0.0, 1.0, 0.2)
        refresh_rate = st.slider("Polling Rate (s)", 0.05, 1.0, 0.2)
        
        st.subheader("🔧 Calibration")
        threshold_temp = st.number_input("Temp Threshold (°C)", value=80)
        threshold_vib = st.number_input("Vibration Limit (Hz)", value=40)
        
        st.divider()
        run = st.checkbox('🔴 SYSTEM LIVE', value=True)
        
        if st.button("Download System Logs"):
            df_download = pd.DataFrame(st.session_state.get('logs', []), columns=["Event Log"])
            st.download_button("Click to Save CSV", df_download.to_csv(), "logs.csv", "text/csv")
            
        if st.button("🔒 Secure Logout"):
            st.session_state["password_correct"] = False
            st.rerun()

    # -- STATE INIT --
    if 'temp_data' not in st.session_state: st.session_state['temp_data'] = []
    if 'vib_data' not in st.session_state: st.session_state['vib_data'] = []
    if 'pressure_data' not in st.session_state: st.session_state['pressure_data'] = []
    if 'logs' not in st.session_state: st.session_state['logs'] = []
    if 'system_health' not in st.session_state: st.session_state['system_health'] = 100

    # -- TABS LAYOUT --
    tab1, tab2, tab3 = st.tabs(["🖥️ Live Dashboard", "📊 Analytics", "📋 System Health"])

    with tab1:
        # Top Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        
        # Simulation Logic
        if run:
            # 1. Temperature (Stable with slow rise)
            temp = 65.0 + np.random.normal(0, 0.5) + (noise_level * np.random.choice([0, 15]))
            
            # 2. Vibration (Fast noise)
            vib = 20.0 + np.random.normal(0, 2.0)
            if np.random.rand() < noise_level: vib += np.random.choice([30, -10])
            
            # 3. Pressure (Constant)
            press = 1013 + np.random.normal(0, 5)
            
            # Update Lists
            st.session_state['temp_data'].append(temp)
            st.session_state['vib_data'].append(vib)
            st.session_state['pressure_data'].append(press)
            
            # Keep List Size Managed
            if len(st.session_state['temp_data']) > 60:
                st.session_state['temp_data'].pop(0)
                st.session_state['vib_data'].pop(0)
                st.session_state['pressure_data'].pop(0)

            # Anomaly Logic
            status = "NOMINAL"
            if temp > threshold_temp:
                status = "OVERHEAT"
                st.session_state['system_health'] -= 5
                st.toast(f"⚠️ ALERT: High Temp Detected! ({temp:.1f}°C)", icon="🔥")
                st.session_state['logs'].insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] 🔥 CRITICAL: Temp {temp:.1f}°C")
            
            if vib > threshold_vib:
                status = "VIBRATION SPIKE"
                st.session_state['system_health'] -= 2
                st.toast(f"⚠️ ALERT: Vibration Spike! ({vib:.1f}Hz)", icon="〰️")
                st.session_state['logs'].insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] 〰️ WARNING: Vib {vib:.1f}Hz")

            # Health Regen
            if status == "NOMINAL" and st.session_state['system_health'] < 100:
                st.session_state['system_health'] += 1

            # Render Metrics
            m1.metric("🔥 Core Temp", f"{temp:.1f} °C", delta=f"{temp-65:.1f}")
            m2.metric("〰️ Vibration", f"{vib:.1f} Hz", delta=f"{vib-20:.1f}", delta_color="inverse")
            m3.metric("💨 Valve Pressure", f"{press:.0f} psi", delta=f"{press-1013:.0f}")
            m4.metric("🛡️ System Status", status, delta_color="off" if status=="NOMINAL" else "inverse")

        # Graphs Grid
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Temperature Trend")
            st.area_chart(st.session_state['temp_data'], color="#FF4B4B", height=200)
        with c2:
            st.subheader("Vibration Analysis")
            st.line_chart(st.session_state['vib_data'], color="#00C9FF", height=200)

        st.subheader("Pressure Monitor")
        st.bar_chart(st.session_state['pressure_data'], color="#92FE9D", height=150)

    with tab2:
        st.subheader("Statistical Anomaly Analysis")
        colA, colB = st.columns([2,1])
        with colA:
            # Fake Heatmap Data
            heatmap_data = pd.DataFrame(
                np.random.randn(10, 5),
                columns=['Sensor A', 'Sensor B', 'Sensor C', 'Sensor D', 'Sensor E']
            )
            st.write("Sensor Correlation Matrix")
            st.dataframe(heatmap_data.style.background_gradient(cmap="coolwarm"), use_container_width=True)
        
        with colB:
            st.write("Metric Distribution")
            st.bar_chart({"Normal": 85, "Warning": 10, "Critical": 5})

    with tab3:
        st.subheader("System Health Integrity")
        health = st.session_state['system_health']
        
        # Color logic for progress bar
        bar_color = "green" if health > 80 else "orange" if health > 50 else "red"
        
        st.progress(health / 100)
        st.caption(f"Current Integrity: {health}%")
        
        if health < 50:
            st.error("⚠️ MAINTENANCE REQUIRED: System Integrity Critical")
        else:
            st.success("✅ SYSTEM STABLE: All sub-routines functional")

        st.subheader("Audit Log")
        st.dataframe(pd.DataFrame(st.session_state['logs'], columns=["Timestamp | Event Description"]), use_container_width=True)

    if run:
        time.sleep(refresh_rate)
        st.rerun()
