"""
Streamlit Dashboard for FairLens

Purpose: Interactive visual dashboard for real-time fairness monitoring.

This dashboard provides:
- Real-time fairness metrics visualization
- DIR trend tracking over multiple checks
- Alert status and explanations
- Interactive controls for simulation parameters
- Compliance audit log viewer

How it fits: This is the VISUALIZE step in the FairLens pipeline.
Data → Metric → Detect → Alert → Log → Explain → Visualize [THIS]
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import subprocess
import sys
import os

st.set_page_config(
    page_title="FairLens - Fairness Monitoring",
    page_icon="⚖️",
    layout="wide"
)

API_BASE_URL = "http://127.0.0.1:8000"

@st.cache_resource
def start_flask_api():
    """Start Flask API on port 8000 in background."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=1)
        if response.status_code == 200:
            return True
    except:
        pass
    
    try:
        flask_process = subprocess.Popen(
            [sys.executable, "-c", 
             "from fairlens_backend.app import app; app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        time.sleep(3)
        return True
    except Exception as e:
        st.error(f"Failed to start Flask API: {str(e)}")
        return False

start_flask_api()


def check_api_health():
    """Check if Flask API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def fetch_fairness_data(n_samples, drift_level):
    """Fetch fairness metrics from API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/monitor_fairness",
            params={"n_samples": n_samples, "drift_level": drift_level},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None


def fetch_audit_history(last_n=20):
    """Fetch compliance audit log."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/audit_history",
            params={"last_n": last_n},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None


st.title("⚖️ FairLens - Fairness Drift Alert System")
st.markdown("**Real-time monitoring of algorithmic fairness in loan decisions**")

if 'history' not in st.session_state:
    st.session_state.history = []

if 'last_check_time' not in st.session_state:
    st.session_state.last_check_time = None

if not check_api_health():
    st.error("🔴 Flask API is not running!")
    st.info("Please start the Flask API server:")
    st.code("python fairlens_backend/app.py", language="bash")
    st.stop()

st.sidebar.header("⚙️ Configuration")

n_samples = st.sidebar.slider(
    "Number of Loan Applications",
    min_value=100,
    max_value=5000,
    value=1000,
    step=100,
    help="Total number of synthetic loan applications to generate"
)

drift_level = st.sidebar.slider(
    "Bias Drift Level",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.1,
    help="0.0 = No bias (fair), 1.0 = Maximum bias (40% approval rate reduction for females)"
)

auto_refresh = st.sidebar.checkbox("Auto-refresh (every 10s)", value=False)

if st.sidebar.button("🔄 Run Fairness Check") or auto_refresh:
    data = fetch_fairness_data(n_samples, drift_level)
    
    if data:
        data['timestamp'] = datetime.now().isoformat()
        st.session_state.history.append(data)
        
        if len(st.session_state.history) > 50:
            st.session_state.history = st.session_state.history[-50:]
        
        st.session_state.last_check_time = datetime.now()

if st.session_state.history:
    latest_data = st.session_state.history[-1]
    drifted = latest_data['drifted_scenario']
    fair = latest_data['fair_scenario']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        dir_value = drifted['dir']
        if dir_value is None:
            st.metric("DIR (Drifted)", "N/A", help="Disparate Impact Ratio")
        else:
            dir_color = "🔴" if drifted['dir_alert'] else "🟢"
            st.metric(
                f"{dir_color} DIR (Drifted)",
                f"{dir_value:.3f}",
                delta=f"{(dir_value - 0.8):.3f} from threshold",
                delta_color="inverse" if dir_value < 0.8 else "normal",
                help="Disparate Impact Ratio - EEOC 80% rule threshold = 0.8"
            )
    
    with col2:
        gap_value = drifted['gap']
        gap_color = "🔴" if drifted['gap_alert'] else "🟢"
        st.metric(
            f"{gap_color} Approval Gap",
            f"{gap_value:.1%}",
            help="Absolute difference between male and female approval rates"
        )
    
    with col3:
        st.metric(
            "Female Approval Rate",
            f"{drifted['female_rate']:.1%}",
            help="Percentage of female applicants approved"
        )
    
    with col4:
        st.metric(
            "Male Approval Rate",
            f"{drifted['male_rate']:.1%}",
            help="Percentage of male applicants approved"
        )
    
    st.markdown("---")
    
    if drifted['dir_alert']:
        st.error("⚠️ **FAIRNESS ALERT: Potential Bias Detected**")
        st.warning(f"**Explanation:** {drifted['explanation']}")
        
        with st.expander("🔒 View Encrypted Alert Token"):
            if drifted.get('encrypted_alert'):
                st.code(drifted['encrypted_alert'], language="text")
            else:
                st.info("No encrypted alert generated")
        
        st.subheader("🔍 Likely Causes of Bias")
        for i, cause in enumerate(drifted.get('likely_causes', []), 1):
            st.write(f"{i}. {cause}")
    else:
        st.success("✅ **System Operating Within Fairness Bounds**")
        st.info(f"**Explanation:** {drifted['explanation']}")
    
    st.markdown("---")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📊 Approval Rate Comparison")
        
        comparison_df = pd.DataFrame({
            'Group': ['Female', 'Male', 'Female (Fair)', 'Male (Fair)'],
            'Approval Rate': [
                drifted['female_rate'],
                drifted['male_rate'],
                fair['female_rate'],
                fair['male_rate']
            ],
            'Scenario': ['Drifted', 'Drifted', 'Fair Baseline', 'Fair Baseline']
        })
        
        fig_bars = px.bar(
            comparison_df,
            x='Group',
            y='Approval Rate',
            color='Scenario',
            barmode='group',
            title="Approval Rates: Drifted vs Fair Baseline",
            color_discrete_map={
                'Drifted': '#FF6B6B',
                'Fair Baseline': '#4ECDC4'
            }
        )
        fig_bars.add_hline(
            y=0.8 * drifted['male_rate'],
            line_dash="dash",
            line_color="orange",
            annotation_text="80% of Male Rate (DIR threshold)"
        )
        fig_bars.update_layout(yaxis_tickformat='.0%')
        st.plotly_chart(fig_bars, use_container_width=True)
    
    with col_right:
        st.subheader("📈 DIR Trend Over Time")
        
        if len(st.session_state.history) > 1:
            trend_data = []
            for i, entry in enumerate(st.session_state.history):
                dir_val = entry['drifted_scenario']['dir']
                if dir_val is not None:
                    trend_data.append({
                        'Check': i + 1,
                        'DIR': dir_val,
                        'Alert': '🔴 Alert' if entry['drifted_scenario']['dir_alert'] else '🟢 OK'
                    })
            
            if trend_data:
                trend_df = pd.DataFrame(trend_data)
                
                fig_trend = go.Figure()
                
                fig_trend.add_trace(go.Scatter(
                    x=trend_df['Check'],
                    y=trend_df['DIR'],
                    mode='lines+markers',
                    name='DIR',
                    line=dict(color='#667EEA', width=3),
                    marker=dict(size=8)
                ))
                
                fig_trend.add_hline(
                    y=0.8,
                    line_dash="dash",
                    line_color="red",
                    annotation_text="EEOC 80% Threshold"
                )
                
                fig_trend.update_layout(
                    title="DIR Evolution Across Checks",
                    xaxis_title="Check Number",
                    yaxis_title="Disparate Impact Ratio",
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("No trend data available (DIR values were None)")
        else:
            st.info("Run multiple checks to see trend analysis")
    
    st.markdown("---")
    
    with st.expander("📋 Detailed Statistics"):
        stats_col1, stats_col2 = st.columns(2)
        
        with stats_col1:
            st.markdown("**Drifted Scenario**")
            st.json(drifted['details'])
        
        with stats_col2:
            st.markdown("**Fair Baseline**")
            st.json(fair['details'])
    
    st.markdown("---")
    
    st.subheader("📜 Compliance Audit Log")
    
    audit_data = fetch_audit_history(last_n=20)
    
    if audit_data and audit_data.get('entries'):
        audit_entries = audit_data['entries']
        
        audit_display = []
        for entry in audit_entries:
            audit_display.append({
                'Timestamp': entry['timestamp'],
                'Event': entry['event_type'],
                'Status': entry['details'].get('status', 'N/A'),
                'DIR': entry['details'].get('dir', 'N/A'),
                'Drift Level': entry['details'].get('drift_level', 'N/A')
            })
        
        audit_df = pd.DataFrame(audit_display)
        st.dataframe(audit_df, use_container_width=True, hide_index=True)
        
        with st.expander("🔍 View Raw Audit Entries"):
            st.json(audit_entries)
    else:
        st.info("No audit history available")

else:
    st.info("👈 Click 'Run Fairness Check' in the sidebar to begin monitoring")
    
    st.markdown("""
    ### About FairLens
    
    FairLens monitors algorithmic fairness in automated loan decision systems using:
    
    - **Disparate Impact Ratio (DIR)**: Measures the ratio of approval rates between protected and privileged groups
    - **EEOC 80% Rule**: DIR < 0.8 indicates potential discrimination
    - **Encrypted Alerts**: Sensitive fairness findings are encrypted for security
    - **Immutable Audit Log**: All checks are logged for compliance and forensic analysis
    - **Statistical Explanations**: Identifies likely causes of detected bias
    
    #### How to Use:
    1. Adjust the **Bias Drift Level** slider (0 = fair, 1 = maximum bias)
    2. Set the **Number of Loan Applications** to simulate
    3. Click **Run Fairness Check** to perform analysis
    4. Review metrics, alerts, and explanations
    5. Examine audit log for compliance tracking
    """)

if auto_refresh and st.session_state.last_check_time:
    time.sleep(10)
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**FairLens v1.0.0**")
st.sidebar.markdown("Fairness Drift Alert System")
if st.session_state.last_check_time:
    st.sidebar.caption(f"Last check: {st.session_state.last_check_time.strftime('%H:%M:%S')}")
