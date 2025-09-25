"""
24DIGI Revenue & Profit Analytics Platform
Main Application Entry Point
"""

import streamlit as st
import sys
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent))

from config.app_config import AppConfig
from modules.data_manager import DataManager
from modules.calculator import RevenueCalculator
from modules.forecaster import Forecaster
from pages import dashboard, calculator, pricing, analytics, forecast, reports

# Page configuration
st.set_page_config(
    page_title="24DIGI Revenue Analytics",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional appearance
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1e3c72;
    }
    
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 0 24px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1e3c72 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

def check_login():
    """Check if user is logged in"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    return st.session_state.logged_in

def login_page():
    """Render the login page"""
    st.markdown("""
    <div class="main-header">
        <h1>🔐 24DIGI Login</h1>
        <p style="margin: 0; opacity: 0.9;">Access Revenue Analytics Platform</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### Please Login")

        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        if st.button("Login", type="primary", use_container_width=True):
            # Simple authentication (username: admin, password: admin123)
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password")


def initialize_app():
    """Initialize the application with default data"""
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()

    if 'calculator' not in st.session_state:
        st.session_state.calculator = RevenueCalculator(st.session_state.data_manager)

    if 'forecaster' not in st.session_state:
        st.session_state.forecaster = Forecaster(st.session_state.calculator)

def render_header():
    """Render the main application header"""
    st.markdown("""
    <div class="main-header">
        <h1> 24DIGI Revenue Analytics Platform</h1>
        <p style="margin: 0; opacity: 0.9;"> Revenue Forecasting & Business Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function"""
    # Check if user is logged in
    if not check_login():
        login_page()
        return

    initialize_app()
    render_header()
    
    # Create tabs
    tabs = st.tabs([
        "📊 Dashboard", 
        "🧮 Revenue Calculator", 
        "💰 Pricing Config", 
        "📈 Analytics", 
        "🔮 Forecasting",
        "📋 Reports"
    ])
    
    with tabs[0]:
        dashboard.render(st.session_state.data_manager, st.session_state.calculator)
    
    with tabs[1]:
        calculator.render(st.session_state.data_manager, st.session_state.calculator)
    
    with tabs[2]:
        pricing.render(st.session_state.data_manager)
    
    with tabs[3]:
        analytics.render(st.session_state.data_manager, st.session_state.calculator)
    
    with tabs[4]:
        forecast.render(st.session_state.forecaster)
    
    with tabs[5]:
        reports.render(st.session_state.calculator, st.session_state.forecaster)
    
    # Sidebar with company info and quick stats
    with st.sidebar:
        st.markdown("### 🏢 24DIGI Analytics")
        st.markdown("*Professional Revenue Intelligence*")

        # User info and logout
        if 'username' in st.session_state:
            st.markdown(f"👤 Welcome, **{st.session_state.username}**")
            if st.button("🚪 Logout", type="secondary"):
                st.session_state.logged_in = False
                if 'username' in st.session_state:
                    del st.session_state.username
                st.rerun()

        st.markdown("---")
        
        # Quick stats
        if hasattr(st.session_state, 'last_calculation'):
            calc_results = st.session_state.last_calculation
            st.metric("Total Revenue", f"{calc_results.get('total_revenue', 0):,.0f} AED")
            st.metric("Total Profit", f"{calc_results.get('total_profit', 0):,.0f} AED")
            profit_margin = calc_results.get('profit_margin', 0)
            st.metric("Profit Margin", f"{profit_margin:.1f}%")
        
        st.markdown("---")
        st.markdown("### 📞 Support")
        st.info("""
        **24DIGI Support Team**
        
        📧 support@24digi.com
        📱 +1 (555) 24-DIGI
        🌐 www.24digi.com
        """)

if __name__ == "__main__":
    main()
