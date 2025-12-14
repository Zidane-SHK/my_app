import streamlit as st
import altair as alt
from models.security_incident import SecurityIncident
from models import GPT

ISSUE_TYPES = ["Malware", "Phishing", "Ransomware", "DDoS", "Trojan", "Other"]

if 'user' not in st.session_state or st.session_state.user is None:
    st.warning("Please log in.")
    st.stop()

st.title("Cybersecurity Operations")
action = st.selectbox("Action", ["View Dashboard", "Log Incident", "Update Incident", "Delete Incident", "AI Assistant"])

df = SecurityIncident.get_all_incidents()

if action == "View Dashboard":
    if not df.empty:

        st.subheader("Live Data")
        
        col1, col2 = st.columns(2)
        with col1:

            chart_bar = alt.Chart(df).mark_bar().encode(
                x=alt.X('issue_type', sort='-y', title='Threat Type'),
                y=alt.Y('count()', title='Frequency'),
                color=alt.Color('issue_type', scale=alt.Scale(scheme='reds'), legend=None),
                tooltip=['issue_type', 'count()']
            ).properties(height=300, title="Threat Frequency")
            st.altair_chart(chart_bar, use_container_width=True)

        with col2:
            chart_pie = alt.Chart(df).mark_arc(innerRadius=60).encode(
                theta=alt.Theta("count()"),
                color=alt.Color("priority", scale=alt.Scale(domain=['Low', 'Medium', 'High', 'Critical'], range=['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c'])),
                tooltip=["priority", "count()"]
            ).properties(height=300, title="Severity Distribution")
            st.altair_chart(chart_pie, use_container_width=True)

        st.divider()

        m1, m2, m3 = st.columns(3)
        m1.metric("Critical Threats", len(df[df['priority'] == 'Critical']))
        m2.metric("Active Incidents", len(df[df['status'] != 'Resolved']))
        m3.metric("Total Logs", len(df))
        
        with st.expander("View Incident Logs", expanded=True):
            st.dataframe(df, use_container_width=True)

    else:
        st.info("No incidents found.")

elif action == "Log Incident":
    with st.form("add_form"):
        st.subheader("Log New Incident")
        new_issue = st.selectbox("Type", ISSUE_TYPES)
        new_desc = st.text_area("Description")
        new_prio = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
        if st.form_submit_button("Log Incident"):
            SecurityIncident.log_incident(new_issue, new_desc, new_prio, new_status)
            st.success("Incident Logged!")
            st.rerun()

elif action == "Update Incident":
    ticket = st.selectbox("Select ID", df['ticket_id'])
    if ticket:
        row = df[df['ticket_id'] == ticket].iloc[0]
        with st.form("edit_form"):
            idx_issue = ISSUE_TYPES.index(row['issue_type']) if row['issue_type'] in ISSUE_TYPES else 0
            e_issue = st.selectbox("Type", ISSUE_TYPES, index=idx_issue)
            e_desc = st.text_area("Description", value=row['description'])
            p_opts = ["Low", "Medium", "High", "Critical"]
            e_prio = st.selectbox("Priority", p_opts, index=p_opts.index(row['priority']))
            s_opts = ["Open", "In Progress", "Resolved"]
            e_stat = st.selectbox("Status", s_opts, index=s_opts.index(row['status']))
            if st.form_submit_button("Update"):
                SecurityIncident.update_incident(ticket, e_issue, e_desc, e_prio, e_stat)
                st.success("Updated!")
                st.rerun()

elif action == "Delete Incident":
    ticket = st.selectbox("Select ID", df['ticket_id'])
    if st.button(f"Confirm Delete {ticket}", type="primary"):
        SecurityIncident.delete_incident(ticket)
        st.rerun()
elif action == "AI Assistant":
    GPT.render_chat_interface("CYBER")