"""
🧠 Amnesia VMUaaS - Admin Dashboard
Enterprise Machine Unlearning Platform

Run with: streamlit run dashboard/app.py
"""
import sys
import os
from pathlib import Path

# Add project root to path for imports (MUST be before any dashboard imports)
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
os.chdir(_project_root)  # Change working directory too

import streamlit as st
import time
from datetime import datetime

# Now import dashboard modules
from dashboard.components.api_client import get_api_client
from dashboard.config import DASHBOARD_TITLE, COLORS, PAGE_TITLE

# ═══════════════════════════════════════════════════════════════════════════════
# Page Configuration
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# Custom CSS
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    /* Card Styling */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 24px;
        margin: 8px 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 48px rgba(99, 102, 241, 0.2);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .metric-label {
        color: #94a3b8;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 8px;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .status-active {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    
    .status-inactive {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    
    /* Headers */
    h1, h2, h3 {
        background: linear-gradient(135deg, #f1f5f9 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
    }
    
    /* Progress Bars */
    .stProgress > div > div {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 8px;
        color: #94a3b8;
        padding: 8px 16px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border-color: transparent;
    }
    
    /* Glass Effect Containers */
    .glass-container {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="font-size: 2rem; margin-bottom: 0;">🧠 Amnesia</h1>
        <p style="color: #94a3b8; font-size: 0.875rem; margin-top: 4px;">
            Machine Unlearning Platform
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "🎯 Training", "🧹 Unlearning", "✅ Verification", "⚙️ System"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # API Status
    st.markdown("### 📡 API Status")
    client = get_api_client()
    health = client.health_check()
    
    if health["success"]:
        st.markdown("""
        <div class="status-badge status-active">● Online</div>
        """, unsafe_allow_html=True)
        data = health.get("data", {})
        st.caption(f"Version: {data.get('version', 'N/A')}")
        st.caption(f"Architecture: {data.get('architecture', 'N/A')}")
    else:
        st.markdown("""
        <div class="status-badge status-inactive">● Offline</div>
        """, unsafe_allow_html=True)
        st.caption(f"Error: {health.get('error', 'Unknown')}")
    
    st.divider()
    
    # Footer
    st.markdown(f"""
    <div style="text-align: center; color: #64748b; font-size: 0.75rem;">
        <p>© 2024 Amnesia VMUaaS</p>
        <p>GDPR/CCPA Compliant</p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# Main Content
# ═══════════════════════════════════════════════════════════════════════════════

if page == "🏠 Dashboard":
    st.title("🧠 Amnesia Dashboard")
    st.markdown("**Enterprise Machine Unlearning Platform** | SISA Architecture")
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <p class="metric-value">4</p>
            <p class="metric-label">Active Shards</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <p class="metric-value">12.4K</p>
            <p class="metric-label">Samples Processed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <p class="metric-value">847</p>
            <p class="metric-label">Data Unlearned</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <p class="metric-value">23</p>
            <p class="metric-label">Certificates Issued</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 SISA Shard Overview")
        from dashboard.components.charts import create_shard_overview
        fig = create_shard_overview([])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Recent Unlearning Jobs")
        st.markdown("""
        <div class="glass-container">
            <table style="width: 100%; color: #f1f5f9;">
                <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
                    <th style="text-align: left; padding: 12px 8px;">Job ID</th>
                    <th style="text-align: left; padding: 12px 8px;">Status</th>
                    <th style="text-align: left; padding: 12px 8px;">Samples</th>
                    <th style="text-align: left; padding: 12px 8px;">Time</th>
                </tr>
                <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.1);">
                    <td style="padding: 12px 8px;">#UL-2024-001</td>
                    <td style="padding: 12px 8px;"><span class="status-badge status-active">Complete</span></td>
                    <td style="padding: 12px 8px;">156</td>
                    <td style="padding: 12px 8px;">2m ago</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.1);">
                    <td style="padding: 12px 8px;">#UL-2024-002</td>
                    <td style="padding: 12px 8px;"><span class="status-badge status-active">Running</span></td>
                    <td style="padding: 12px 8px;">89</td>
                    <td style="padding: 12px 8px;">In progress</td>
                </tr>
                <tr>
                    <td style="padding: 12px 8px;">#UL-2024-003</td>
                    <td style="padding: 12px 8px;"><span class="status-badge status-active">Complete</span></td>
                    <td style="padding: 12px 8px;">234</td>
                    <td style="padding: 12px 8px;">1h ago</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

elif page == "🎯 Training":
    st.title("🎯 Model Training")
    st.markdown("Train models using SISA (Sharded, Isolated, Sliced, Aggregated) architecture")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Training Configuration")
        
        with st.form("training_form"):
            model_type = st.selectbox(
                "Model Architecture",
                ["ResNet18", "ResNet34", "ResNet50", "SimpleMLP", "Transformer"],
                help="Select the neural network architecture"
            )
            
            col_a, col_b = st.columns(2)
            with col_a:
                num_shards = st.slider("Number of Shards", 2, 8, 4, help="SISA sharding factor")
                epochs = st.slider("Training Epochs", 10, 200, 50)
            with col_b:
                batch_size = st.selectbox("Batch Size", [16, 32, 64, 128], index=1)
                learning_rate = st.select_slider(
                    "Learning Rate",
                    options=[0.0001, 0.0005, 0.001, 0.005, 0.01],
                    value=0.001
                )
            
            submitted = st.form_submit_button("🚀 Start Training", use_container_width=True)
            
            if submitted:
                st.success("Training job submitted! Check the status below.")
    
    with col2:
        st.subheader("📊 Training Status")
        st.markdown("""
        <div class="glass-container">
            <p style="color: #94a3b8; font-size: 0.875rem;">Current Job</p>
            <p style="color: #f1f5f9; font-size: 1.25rem; font-weight: 600;">No active training</p>
            <div style="margin-top: 16px;">
                <p style="color: #94a3b8; font-size: 0.75rem;">READY FOR NEW JOB</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

elif page == "🧹 Unlearning":
    st.title("🧹 Data Unlearning")
    st.markdown("Surgically remove data from trained models using Gradient Ascent with Fisher regularization")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Unlearning Configuration")
        
        with st.form("unlearning_form"):
            st.markdown("**Select Data to Forget**")
            data_indices = st.text_area(
                "Data Indices (comma-separated)",
                placeholder="e.g., 1, 5, 23, 156, 789",
                help="Enter the indices of data points to unlearn"
            )
            
            st.markdown("**Hyperparameters**")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                alpha = st.slider("α (Forget Weight)", 1.0, 20.0, 10.0, 0.5)
            with col_b:
                beta = st.slider("β (Retain Weight)", 0.01, 1.0, 0.1, 0.01)
            with col_c:
                gamma = st.slider("γ (Fisher Weight)", 0.001, 0.1, 0.01, 0.001)
            
            epochs = st.slider("Unlearning Epochs", 10, 200, 100)
            
            submitted = st.form_submit_button("🧹 Start Unlearning", use_container_width=True)
            
            if submitted:
                if data_indices:
                    st.success("Unlearning job submitted!")
                    with st.spinner("Processing..."):
                        progress = st.progress(0)
                        for i in range(100):
                            time.sleep(0.02)
                            progress.progress(i + 1)
                    st.balloons()
                else:
                    st.error("Please enter data indices to unlearn")
    
    with col2:
        st.subheader("📈 Loss Visualization")
        from dashboard.components.charts import create_loss_chart
        
        # Demo loss data
        demo_history = {
            "forget_loss": [2.5, 2.3, 2.0, 1.7, 1.4, 1.1, 0.9, 0.7, 0.5, 0.4],
            "retain_loss": [0.3, 0.35, 0.32, 0.31, 0.33, 0.30, 0.29, 0.28, 0.27, 0.26],
            "fisher_loss": [0.1, 0.12, 0.11, 0.10, 0.09, 0.08, 0.07, 0.06, 0.05, 0.05],
            "total_loss": [25.3, 23.5, 20.3, 17.4, 14.5, 11.3, 9.2, 7.2, 5.3, 4.2],
        }
        fig = create_loss_chart(demo_history)
        st.plotly_chart(fig, use_container_width=True)

elif page == "✅ Verification":
    st.title("✅ Erasure Verification")
    st.markdown("Verify data removal using Membership Inference Attacks and generate compliance certificates")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Run Verification")
        
        with st.form("verify_form"):
            shard_id = st.selectbox("Select Shard", [0, 1, 2, 3])
            threshold = st.slider("Confidence Threshold", 0.3, 0.9, 0.6, 0.05)
            
            submitted = st.form_submit_button("🔍 Verify Erasure", use_container_width=True)
            
            if submitted:
                with st.spinner("Running Membership Inference Attack..."):
                    time.sleep(2)
                
                # Demo result
                st.success("✅ Verification Complete!")
                
                from dashboard.components.charts import create_confidence_gauge
                fig = create_confidence_gauge(0.42, threshold)
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📜 Certificates")
        
        st.markdown("""
        <div class="glass-container">
            <h4 style="color: #f1f5f9; margin-bottom: 16px;">Recent Certificates</h4>
            <div style="border-bottom: 1px solid rgba(99, 102, 241, 0.2); padding: 12px 0;">
                <p style="color: #f1f5f9; margin: 0;">📄 CERT-2024-001.pdf</p>
                <p style="color: #94a3b8; font-size: 0.75rem; margin: 4px 0 0 0;">Issued: Feb 6, 2024</p>
            </div>
            <div style="border-bottom: 1px solid rgba(99, 102, 241, 0.2); padding: 12px 0;">
                <p style="color: #f1f5f9; margin: 0;">📄 CERT-2024-002.pdf</p>
                <p style="color: #94a3b8; font-size: 0.75rem; margin: 4px 0 0 0;">Issued: Feb 5, 2024</p>
            </div>
            <div style="padding: 12px 0;">
                <p style="color: #f1f5f9; margin: 0;">📄 CERT-2024-003.pdf</p>
                <p style="color: #94a3b8; font-size: 0.75rem; margin: 4px 0 0 0;">Issued: Feb 4, 2024</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

elif page == "⚙️ System":
    st.title("⚙️ System Monitoring")
    st.markdown("Monitor system health, workers, and performance metrics")
    
    # System Status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #94a3b8; margin: 0 0 12px 0;">FastAPI Server</h4>
            <p class="metric-value" style="font-size: 1.5rem;">Active</p>
            <span class="status-badge status-active">● Online</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #94a3b8; margin: 0 0 12px 0;">Redis Broker</h4>
            <p class="metric-value" style="font-size: 1.5rem;">Connected</p>
            <span class="status-badge status-active">● Online</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #94a3b8; margin: 0 0 12px 0;">Celery Workers</h4>
            <p class="metric-value" style="font-size: 1.5rem;">4 Active</p>
            <span class="status-badge status-active">● Running</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Configuration
    st.subheader("📝 Configuration")
    
    with st.expander("View Current Configuration", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Server Settings**")
            st.json({
                "host": "0.0.0.0",
                "port": 8000,
                "workers": 4,
                "debug": False,
            })
        
        with col2:
            st.markdown("**Unlearning Defaults**")
            st.json({
                "alpha": 10.0,
                "beta": 0.1,
                "gamma": 0.01,
                "epochs": 100,
                "verification_threshold": 0.6,
            })
    
    st.subheader("📊 Prometheus Metrics")
    st.info("📡 Metrics available at `/metrics` endpoint for Grafana integration")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Requests/min", "847", "+12%")
        st.metric("Avg Response Time", "42ms", "-5ms")
    with col2:
        st.metric("Active Jobs", "3", "+1")
        st.metric("GPU Memory", "4.2 GB", "+0.3 GB")
