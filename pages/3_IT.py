import streamlit as st
import altair as alt
from models.it_ticket import ITTicket
from models import GPT


ISSUE_TYPES = ["Server Failure", "Network Down", "VPN Access", "Hardware", "Software", "Other"]

if 'user' not in st.session_state or st.session_state.user is None:
    st.warning("Please log in.")
    st.stop()

st.title("IT Operations")
action = st.selectbox("Action", ["View Dashboard", "Create Ticket", "Update Ticket", "Delete Ticket", "AI Assistant"])

df = ITTicket.get_all_tickets()

if action == "View Dashboard":
    if not df.empty:
        st.subheader("Systems Status Analytics")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("### Common Issues")
            
            base = alt.Chart(df).encode(
                x=alt.X('count()', title='Ticket Count'),
                y=alt.Y('issue_type', sort='-x', title='Issue Type')
            )
            
            rule = base.mark_rule(size=2).encode(
                color=alt.Color('issue_type', legend=None),
                opacity=alt.value(0.6)
            )
            
            circle = base.mark_circle(size=100).encode(
                color=alt.Color('issue_type', legend=None),
                tooltip=['issue_type', 'count()']
            )
            
            st.altair_chart(rule + circle, use_container_width=True)

        with c2:
            st.markdown("### Resolution Chart")
            chart_pie = alt.Chart(df).mark_arc(innerRadius=50).encode(
                theta=alt.Theta("count()"),
                color=alt.Color("status", scale=alt.Scale(scheme='category10')),
                tooltip=["status", "count()"]
            ).properties(height=300)
            st.altair_chart(chart_pie, use_container_width=True)
            
        st.divider()

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Tickets", len(df))
        m2.metric("High Priority", len(df[df['priority'].isin(['High', 'Critical'])]))
        m3.metric("Resolved", len(df[df['status'] == 'Resolved']))

        with st.expander("View Ticket Records", expanded=True):
            st.dataframe(df, use_container_width=True)

    else:
        st.info("No tickets found.")

elif action == "Create Ticket":
    with st.form("add_form"):
        new_issue = st.selectbox("Issue", ISSUE_TYPES)
        new_desc = st.text_area("Description")
        new_prio = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
        if st.form_submit_button("Submit"):
            ITTicket.create_ticket(new_issue, new_desc, new_prio, new_status)
            st.success("Ticket Created!")
            st.rerun()

elif action == "Update Ticket":
    ticket = st.selectbox("Select Ticket", df['ticket_id'])
    if ticket:
        row = df[df['ticket_id'] == ticket].iloc[0]
        with st.form("edit_form"):
            idx_issue = ISSUE_TYPES.index(row['issue_type']) if row['issue_type'] in ISSUE_TYPES else 0
            e_issue = st.selectbox("Issue", ISSUE_TYPES, index=idx_issue)
            e_desc = st.text_area("Description", value=row['description'])
            p_opts = ["Low", "Medium", "High", "Critical"]
            e_prio = st.selectbox("Priority", p_opts, index=p_opts.index(row['priority']))
            s_opts = ["Open", "In Progress", "Resolved"]
            e_stat = st.selectbox("Status", s_opts, index=s_opts.index(row['status']))
            if st.form_submit_button("Update"):
                ITTicket.update_ticket(ticket, e_issue, e_desc, e_prio, e_stat)
                st.success("Updated!")
                st.rerun()

elif action == "Delete Ticket":
    ticket = st.selectbox("Select Ticket", df['ticket_id'])
    if st.button(f"Delete {ticket}", type="primary"):
        ITTicket.delete_ticket(ticket)
        st.rerun()
elif action == "AI Assistant":
    GPT.render_chat_interface("IT")