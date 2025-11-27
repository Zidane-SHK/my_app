from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.services.user_service import register_user, login_user, migrate_users_from_file
from app.data.incidents import insert_incident, get_all_incidents

def main():
    print("=" * 60)
    print("Week 8: Database Demo")
    print("=" * 60)
    
    # 1. Setup database
    conn = connect_database()
    create_all_tables(conn)
    conn.close()
    
    # 2. Migrate users
    migrate_users_from_file()
    
    # 3. Test authentication
    success, msg = register_user("alice", "SecurePass123!", "analyst")
    print(msg)
    
    success, msg = login_user("alice", "SecurePass123!")
    print(msg)
    
    # 4. Test CRUD
    incident_id = insert_incident(
        "2024-11-05",
        "Phishing",
        "High",
        "Open",
        "Suspicious email detected",
        "alice"
    )
    print(f"Created incident #{incident_id}")
    
    # 5. Query data
    df = get_all_incidents()
    print(f"Total incidents: {len(df)}")

if __name__ == "__main__":
    main()


'''import streamlit as st
import pandas as pd
import numpy as np
st.set_page_config(page_title="Layout Demo", layout="wide")
st.title("1. Layout Demo -- Building a Simple Dashboard")

#Side-bar

with st.sidebar:
    st.header('Controls')
    points = st.slider('No. Points', 10, 500, 100)
    table = st.checkbox('Raw data')

#Main
st.header('Main content')
data = pd.DataFrame(
    np.random.randn(points, 3),
    columns = ['Feature 1', 'Feature 2', 'Feature 3']
)
col1, col2 = st.columns(2)

with col1:
    st.header('Line Chart')
    st.line_chart(data)

with col2:
    st.header('Bar Chart')
    st.bar_chart(data)

with st.expander('Raw data'):
    if table:
        st.dataframe(data)
    else:
        st.info('--')
'''