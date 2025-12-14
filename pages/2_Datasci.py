import streamlit as st
import altair as alt
from models.dataset import Dataset
from models import GPT


ISSUE_TYPES = ["Analytics", "Data Cleaning", "Model Training", "Visualization", "Dataset", "Other"]

if 'user' not in st.session_state or st.session_state.user is None:
    st.warning("Please log in.")
    st.stop()

st.title("Data Science Projects")
action = st.selectbox("Manage Projects", ["View Dashboard", "Create Project", "Update Project", "Delete Project", "AI Assistant"])

df = Dataset.get_all_projects()

if action == "View Dashboard":
    if not df.empty:
        st.subheader("Project Analytics")
        
        base = alt.Chart(df).encode(
            x=alt.X('status', title='Status'),
            y=alt.Y('issue_type', title='Project Category')
        )

        heatmap = base.mark_rect().encode(
            color=alt.Color('count()', title='Count', scale=alt.Scale(scheme='viridis')),
            tooltip=['issue_type', 'status', 'count()']
        )

        text = base.mark_text().encode(
            text='count()',
            color=alt.value('white')  
        )

        chart = (heatmap + text).properties(
            height=400, 
            title="Project Density (Category To Status)"
        )
        
        st.altair_chart(chart, use_container_width=True)
        
        st.divider()

        c1, c2 = st.columns(2)
        c1.metric("Total Projects", len(df))
        c2.metric("Active Tickets", len(df[df['status'] != 'Resolved']))
        
        with st.expander("View Project Details", expanded=True):
            st.dataframe(df, use_container_width=True)

    else:
        st.info("No projects found.")

elif action == "Create Project":
    with st.form("add_form"):
        new_issue = st.selectbox("Category", ISSUE_TYPES)
        new_desc = st.text_area("Description")
        new_prio = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
        if st.form_submit_button("Create"):
            Dataset.create_project(new_issue, new_desc, new_prio, new_status)
            st.success("Project Created!")
            st.rerun()

elif action == "Update Project":
    ticket = st.selectbox("Select Project", df['ticket_id'])
    if ticket:
        row = df[df['ticket_id'] == ticket].iloc[0]
        with st.form("edit_form"):
            idx_issue = ISSUE_TYPES.index(row['issue_type']) if row['issue_type'] in ISSUE_TYPES else 0
            e_issue = st.selectbox("Category", ISSUE_TYPES, index=idx_issue)
            e_desc = st.text_area("Description", value=row['description'])
            p_opts = ["Low", "Medium", "High", "Critical"]
            e_prio = st.selectbox("Priority", p_opts, index=p_opts.index(row['priority']))
            s_opts = ["Open", "In Progress", "Resolved"]
            e_stat = st.selectbox("Status", s_opts, index=s_opts.index(row['status']))
            if st.form_submit_button("Update"):
                Dataset.update_project(ticket, e_issue, e_desc, e_prio, e_stat)
                st.success("Updated!")
                st.rerun()

elif action == "Delete Project":
    ticket = st.selectbox("Select Project", df['ticket_id'])
    if st.button(f"Delete {ticket}", type="primary"):
        Dataset.delete_project(ticket)
        st.rerun()
elif action == "AI Assistant":
    GPT.render_chat_interface("DATASCI")