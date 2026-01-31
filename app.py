import streamlit as st
import numpy as np
import pandas as pd
import time
from datetime import datetime

# --- 1. SETUP ---
st.set_page_config(page_title="SenseGuard Secure", layout="wide")

# --- 2. AUTHENTICATION ---
def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] == "admin" and st.session_state["password"] == "1234":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        return False
    
    elif not st.session_state["password_correct"]:
        # Password incorrect, show inputs + error
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        st.error("😕 User not found or password incorrect")
        return False
    
    else:
        # Password correct
        return True

# --- 3. MAIN APP LOGIC ---
if check_password():
    # **********************************************
    # EVERYTHING BELOW IS YOUR DASHBOARD CODE
    # **********************************************
    
    st.title("🛡️ SenseGuard: Secure Dashboard")
    
    # Logout Button
    if st.sidebar.button("Log Out"):
        st.session_state["password_correct"] = False
        st.rerun()

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Controls")
        noise = st.slider("Noise Level", 0.0, 0.5, 0.1)
        speed = st.slider("Speed", 0.05, 0.5, 0.1)
        run = st.checkbox('▶ START SIMULATION', value=True)
        if st.button("Reset"):
            st.session_state.clear()
            st.rerun()

    # --- STATE ---
    if 'data' not in st.session_state:
        st.session_state['data'] = []
    if 'logs' not in st.session_state:
        st.session_state['logs'] = []

    # --- LAYOUT ---
    st.subheader("1. Live Sensor Graph")
    chart_box = st.empty()

    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("2. Real-Time Metrics")
        metrics_box = st.empty()
    with col2:
        st.subheader("3. System Logs")
        logs_box = st.empty()

    # --- LOOP ---
    while run:
        val = 25.0 + np.random.normal(0, 0.5)
        
        # FIX IS HERE:
        if np.random.rand() < noise: val += np.random.choice([40, -40])
        
        if abs(val - 25) > 10:
            clean = 25.0
            status = "BLOCKED"
            color = "inverse"
        else:
            clean = val
            status = "OK"
            color = "normal"
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state['data'].append([val, clean])
        if len(st.session_state['data']) > 80: st.session_state['data'].pop(0)
        
        if status == "BLOCKED":
            st.session_state['logs'].insert(0, f"[{timestamp}] ⚠️ SPIKE: {val:.1f} rejected")

        with chart_box.container():
            df = pd.DataFrame(st.session_state['data'], columns=["Raw", "Clean"])
            st.line_chart(df, color=["#FF0000", "#00FF00"], height=300)

        with metrics_box.container():
            k1, k2, k3 = st.columns(3)
            k1.metric("Raw Input", f"{val:.1f}", delta=f"{val-25:.1f}", delta_color="inverse")
            k2.metric("Clean Output", f"{clean:.1f}", delta_color="normal")
            k3.metric("Status", status, delta_color=color)

        with logs_box.container():
            st.code("\n".join(st.session_state['logs'][:5]))

        time.sleep(speed)
