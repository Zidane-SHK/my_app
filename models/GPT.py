import streamlit as st
from openai import OpenAI
import database.db as db
import pandas as pd

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    client = None

def get_current_username():
    """Safely extracts the username string."""
    user_obj = st.session_state.get('user')
    if user_obj and hasattr(user_obj, 'username'):
        return user_obj.username
    elif isinstance(user_obj, str):
        return user_obj
    return "guest"

def get_data_context(module_name):
    table_map = {
        "IT": "it_tickets",
        "CYBER": "security_incidents",
        "DATASCI": "data_science_projects"
    }
    
    target_table = table_map.get(module_name)
    
    if target_table:
        try:
            
            df = db.fetch_all(target_table)
            
            if not df.empty:
                
                return df.tail(20).to_csv(index=False)
        except Exception as e:
            return f"Error loading data: {e}"
            
    return "No data available."

def render_chat_interface(module_name):
    st.subheader(f"{module_name} AI Assistant")

    if not client:
        st.error("OpenAI API Key missing in .streamlit/secrets.toml")
        return

    username = get_current_username()

    if "messages" not in st.session_state:
        st.session_state.messages = db.get_chat_history(username, module_name)

    with st.sidebar:
        st.title("Chat Controls")
        st.metric("Messages", len(st.session_state.messages))
        
        if st.button("Clear History", type="primary", use_container_width=True):
            db.delete_chat_history(username, module_name)
            st.session_state.messages = []
            st.rerun()

    for msg in st.session_state.messages:
        role = msg["sender"]
        with st.chat_message(role, avatar=None):
            st.markdown(msg["message"])

    if prompt := st.chat_input(f"Ask about {module_name} data..."):
        
        with st.chat_message("user", avatar=None):
            st.markdown(prompt)
        
        st.session_state.messages.append({"sender": "user", "message": prompt})
        db.save_chat_message(username, module_name, "user", prompt)

        
        data_context = get_data_context(module_name)
        
        with st.chat_message("assistant", avatar=None):
            response_text = st.write_stream(
                stream_generator(module_name, prompt, st.session_state.messages, data_context)
            )
        
        st.session_state.messages.append({"sender": "assistant", "message": response_text})
        db.save_chat_message(username, module_name, "assistant", response_text)

def stream_generator(module_name, new_prompt, history, data_context):
    base_personas = {
        "IT": "You are an IT Support Specialist.",
        "CYBER": "You are a Cyber Security Analyst.",
        "DATASCI": "You are a Data Scientist."
    }
    
    system_instr = f"""
    {base_personas.get(module_name, "You are a helpful assistant.")}
    
    You have access to the following LIVE DATA from the database (last 20 entries):
    ---
    {data_context}
    ---
    Answer the user's question based on this data. 
    If they ask for stats (count, average), calculate them from the data above.
    """
    
    api_messages = [{"role": "system", "content": system_instr}]
    
    for m in history[-10:]:
        role = "user" if m["sender"] == "user" else "assistant"
        api_messages.append({"role": role, "content": m["message"]})
    
    api_messages.append({"role": "user", "content": new_prompt})

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=api_messages,
        stream=True,
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content