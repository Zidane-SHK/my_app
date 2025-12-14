import streamlit as st
import pandas as pd
import altair as alt
import time

from services.auth_manager import AuthManager
from services.database_manager import DatabaseManager

try:
    from models.security_incident import SecurityIncident
    from models.it_ticket import ITTicket
    from models.dataset import Dataset
except ImportError:
    st.error("Error: Could not import Models. Ensure 'models/' folder exists.")

st.set_page_config(
    page_title="Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager("database/app.db")

if 'auth_manager' not in st.session_state:
    st.session_state.auth_manager = AuthManager(st.session_state.db_manager)

if 'user' not in st.session_state:
    st.session_state.user = None

def get_unified_data():
    """
    Fetches data from all models and standardizes it for the master dashboard.
    """
    try:
        df_cyber = SecurityIncident.get_all_incidents()
        df_it = ITTicket.get_all_tickets()
        df_data = Dataset.get_all_projects()
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    if not df_cyber.empty:
        df_cyber['Department'] = 'Cyber Security'
    if not df_it.empty:
        df_it['Department'] = 'IT Operations'
    if not df_data.empty:
        df_data['Department'] = 'Data Analysis'

    common_cols = ['Department', 'priority', 'status']
    frames = []
    
    for df in [df_cyber, df_it, df_data]:
        if not df.empty and set(common_cols).issubset(df.columns):
            df['priority'] = df['priority'].str.title() 
            df['status'] = df['status'].str.title()
            frames.append(df[common_cols])
            
    if frames:
        df_all = pd.concat(frames, ignore_index=True)
        return df_all, df_cyber, df_data, df_it
    
    return pd.DataFrame(), df_cyber, df_data, df_it

def login_page():
    st.title("Intelligence Platform")
    st.subheader("Authentication Required")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if not username or not password:
                    st.warning("Please enter both username and password.")
                    st.stop()

                user = st.session_state.auth_manager.login(username, password)
                
                if user is None:
                    st.error("Invalid username or password.")
                else:
                    st.session_state.user = user
                    st.success(f"Welcome back, {user.get_username()}!")
                    time.sleep(0.5)
                    st.rerun()

    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("New Username")
            new_pass = st.text_input("New Password", type="password")
            reg_submitted = st.form_submit_button("Register")
            
            if reg_submitted:
                if not new_user or not new_pass:
                    st.warning("Username and password cannot be empty.")
                else:
                    success = st.session_state.auth_manager.register(new_user, new_pass)
                    if success:
                        st.success("Account created! Please log in.")
                    else:
                        st.error("Username already exists or error occurred.")


def home_dashboard():
    st.title("Overview Statistics")
    st.markdown("### Information")

    df_all, df_cyber, df_data, df_it = get_unified_data()
    total_records = len(df_all)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Volume", total_records)
    
    crit_count = len(df_all[df_all['priority'] == 'Critical']) if not df_all.empty else 0
    col2.metric("Alerts", crit_count, delta="High Priority", delta_color="inverse")
    
    resolved_count = len(df_all[df_all['status'].isin(['Resolved', 'Closed'])]) if not df_all.empty else 0
    col3.metric("Resolved", resolved_count, delta="Completed")
    
    col4.metric("Categories", df_all['Department'].nunique() if not df_all.empty else 0)

    st.divider()

    if not df_all.empty:
        priority_scale = alt.Scale(domain=['Critical', 'High', 'Medium', 'Low'], range=['#d62728', '#ff7f0e', '#fdbf11', '#2ca02c'])
        dept_scale = alt.Scale(scheme='tableau10')

        r1c1, r1c2 = st.columns(2)
        
        with r1c1:
            st.subheader("1. Distribution by Category")
            chart_donut = alt.Chart(df_all).mark_arc(innerRadius=60).encode(
                theta=alt.Theta("count()", stack=True),
                color=alt.Color("Department", scale=dept_scale),
                tooltip=["Department", "count()"],
                order=alt.Order("count()", sort="descending")
            ).properties(height=300)
            st.altair_chart(chart_donut, use_container_width=True)

        with r1c2:
            st.subheader("2. Risk Profile")
            chart_bar = alt.Chart(df_all).mark_bar().encode(
                x=alt.X('priority', sort=['Critical', 'High', 'Medium', 'Low'], title='Priority'),
                y=alt.Y('count()', title='Ticket Count'),
                color=alt.Color('priority', scale=priority_scale, legend=None),
                tooltip=['priority', 'count()']
            ).properties(height=300)
            st.altair_chart(chart_bar, use_container_width=True)

        st.divider()

        r2c1, r2c2 = st.columns(2)

        with r2c1:
            st.subheader("3. Status Graphs")
            chart_stack = alt.Chart(df_all).mark_bar().encode(
                y=alt.Y('Department', title=None),
                x=alt.X('count()', title='Volume'),
                color=alt.Color('status', title='Status', scale=alt.Scale(scheme='set2')),
                tooltip=['Department', 'status', 'count()']
            ).properties(height=300)
            st.altair_chart(chart_stack, use_container_width=True)

        with r2c2:
            st.subheader("4. Risk Map")
            chart_heat = alt.Chart(df_all).mark_rect().encode(
                x=alt.X('status', title='Status'),
                y=alt.Y('priority', title='Priority', sort=['Critical', 'High', 'Medium', 'Low']),
                color=alt.Color('count()', title='Density', scale=alt.Scale(scheme='reds')),
                tooltip=['priority', 'status', 'count()']
            ).properties(height=300)
            st.altair_chart(chart_heat, use_container_width=True)

    else:
        st.info("No data available. Please add records via the sidebar pages.")

def cyber_page():
    st.title("Cyber Security Operations")
    df = SecurityIncident.get_all_incidents()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No cyber security data available.")

def data_page():
    st.title("Data Analysis")
    df = Dataset.get_all_projects()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No data available.")

def it_page():
    st.title("IT Operations Center")
    df = ITTicket.get_all_tickets()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No IT operations data available.")

def main_app():
    with st.sidebar:
        if st.session_state.user:
            st.header(f"User: {st.session_state.user.get_username()}")
            st.caption(f"Role: {st.session_state.user.get_role()}")
        
        st.divider()
        
        page_selection = st.selectbox(
            "Navigate to:", 
            ["Home Dashboard", "Cyber Security", "Data Analysis", "IT Operations"]
        )
        
        st.divider()
        
        if st.button("Logout", key="logout_main"):
            st.session_state.user = None
            st.rerun()

    if page_selection == "Home Dashboard":
        home_dashboard()
    elif page_selection == "Cyber Security":
        cyber_page()
    elif page_selection == "Data Analysis":
        data_page()
    elif page_selection == "IT Operations":
        it_page()

if __name__ == "__main__":
    if st.session_state.user:
        main_app()
    else:
        login_page()