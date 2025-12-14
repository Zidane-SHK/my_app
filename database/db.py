import sqlite3
import pandas as pd
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

DB_NAME = "app.db"
DB_PATH = os.path.join(BASE_DIR, DB_NAME) 


FILES = {
    "IT": os.path.join(PROJECT_ROOT, "Assets", "IT.csv"),
    "CYBER": os.path.join(PROJECT_ROOT, "Assets", "Cybersec.csv"),
    "DATASCI": os.path.join(PROJECT_ROOT, "Assets", "DataSci.csv")
}

def parse_messy_row(parts):
    
    parts = [p.strip().replace('"', '') for p in parts]
    
    col2 = parts[2] if len(parts) > 2 else ""
    col3 = parts[3] if len(parts) > 3 else ""
    
    category = "Unknown"
    issue_type = "Other"
    description = ""
    
    if col2 == "IT" or col2 == "IT Operations":
        category = "IT Operations"
        desc_start = 4
    elif col2 == "Cybersecurity":
        category = "Cybersecurity"
        desc_start = 3
    elif col2 == "Data" and col3 == "Science":
        category = "Data Science"
        desc_start = 4
    else:
        category = "Unknown"
        desc_start = 2

    full_desc = " ".join(parts[desc_start:-2]) 
    
    known_issues = [
        'Malware', 'Ransomware', 'Trojan', 'Phishing', 'DDoS',
        'Server Failure', 'Network Down', 'VPN Access', 'Hardware', 'Software',
        'Analytics', 'Data Cleaning', 'Model Training', 'Visualization', 'Dataset'
    ]
    
    for issue in known_issues:
        if full_desc.startswith(issue):
            issue_type = issue
            description = full_desc.replace(issue, "").strip().strip(',').strip()
            if not description: description = full_desc 
            break
            
    if issue_type == "Other":
        description = full_desc
        
    return category, issue_type, description

def load_and_parse_csvs():
    all_data = []
    
    print(f"--- Starting Data Load ---")
    print(f"Looking for files in Project Root: {PROJECT_ROOT}")
    
    for key, fpath in FILES.items():
        if not os.path.exists(fpath):
            print(f"[WARNING] Could not find file for {key}: {fpath}")
            fallback = os.path.join(BASE_DIR, "Assets", os.path.basename(fpath))
            if os.path.exists(fallback):
                print(f"  -> Found in fallback location: {fallback}")
                fpath = fallback
            else:
                continue
            
        print(f"Parsing {key} file: {fpath}")
        try:
            with open(fpath, 'r') as f:
                lines = f.readlines()
                for line in lines[1:]: # Skip header
                    clean_line = line.replace('"', '').strip()
                    parts = clean_line.split(',')
                    
                    if len(parts) < 5: continue
                    
                    category, issue, desc = parse_messy_row(parts)
                    
                    row = {
                        'ticket_id': parts[0],
                        'date': parts[1],
                        'category': category,
                        'issue_type': issue,
                        'description': desc,
                        'priority': parts[-2],
                        'status': parts[-1]
                    }
                    all_data.append(row)
        except Exception as e:
            print(f"Error parsing {fpath}: {e}")
            
    print(f"--- Loaded {len(all_data)} total rows ---")
    return all_data

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db(force_reset=True):
    conn = get_connection()
    cursor = conn.cursor()

    if force_reset:
        cursor.execute("DROP TABLE IF EXISTS it_tickets")
        cursor.execute("DROP TABLE IF EXISTS security_incidents")
        cursor.execute("DROP TABLE IF EXISTS data_science_projects")
        cursor.execute("DROP TABLE IF EXISTS users")

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT, role TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS it_tickets (ticket_id TEXT PRIMARY KEY, date TEXT, issue_type TEXT, description TEXT, priority TEXT, status TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS security_incidents (ticket_id TEXT PRIMARY KEY, date TEXT, issue_type TEXT, description TEXT, priority TEXT, status TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS data_science_projects (ticket_id TEXT PRIMARY KEY, date TEXT, issue_type TEXT, description TEXT, priority TEXT, status TEXT)''')

    all_rows = load_and_parse_csvs()
    
    counts = {"IT": 0, "Cyber": 0, "DS": 0}
    
    for row in all_rows:
        if row['category'] == "IT Operations":
            cursor.execute('INSERT OR REPLACE INTO it_tickets VALUES (:ticket_id, :date, :issue_type, :description, :priority, :status)', row)
            counts["IT"] += 1
        elif row['category'] == "Cybersecurity":
            cursor.execute('INSERT OR REPLACE INTO security_incidents VALUES (:ticket_id, :date, :issue_type, :description, :priority, :status)', row)
            counts["Cyber"] += 1
        elif row['category'] == "Data Science":
            cursor.execute('INSERT OR REPLACE INTO data_science_projects VALUES (:ticket_id, :date, :issue_type, :description, :priority, :status)', row)
            counts["DS"] += 1

    try:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", ("admin", "0000", "admin"))
    except: pass
    
    conn.commit()
    conn.close()
    print(f"Database Seeded! IT: {counts['IT']}, Cyber: {counts['Cyber']}, DS: {counts['DS']}")

def fetch_all(table_name):
    conn = get_connection()
    try:
        return pd.read_sql(f"SELECT * FROM {table_name}", conn)
    except:
        return pd.DataFrame()
    finally:
        conn.close()

def generate_id(table_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT ticket_id FROM {table_name} ORDER BY ticket_id DESC LIMIT 1")
    res = cursor.fetchone()
    conn.close()
    if res:
        return f"TICK-{int(res[0].split('-')[1]) + 1}"
    return "TICK-1001"

def add_entry(table_name, issue, desc, prio, stat):
    tid = generate_id(table_name)
    dt = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    conn.execute(f"INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?, ?)", (tid, dt, issue, desc, prio, stat))
    conn.commit()
    conn.close()

def update_entry(table_name, tid, issue, desc, prio, stat):
    conn = get_connection()
    conn.execute(f"UPDATE {table_name} SET issue_type=?, description=?, priority=?, status=? WHERE ticket_id=?", (issue, desc, prio, stat, tid))
    conn.commit()
    conn.close()

def delete_entry(table_name, tid):
    conn = get_connection()
    conn.execute(f"DELETE FROM {table_name} WHERE ticket_id=?", (tid,))
    conn.commit()
    conn.close()

init_db()


def init_chat_db():
    """Adds the chat_logs table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            module TEXT,  -- e.g., 'IT', 'CYBER', 'DATASCI'
            sender TEXT,  -- 'user' or 'assistant'
            message TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_chat_message(username, module, sender, message):
    """Saves a single message to the DB."""
    conn = get_connection()
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO chat_logs (username, module, sender, message, timestamp) VALUES (?, ?, ?, ?, ?)",
        (username, module, sender, message, dt)
    )
    conn.commit()
    conn.close()

def get_chat_history(username, module):
    """Retrieves chat history for a specific user and module."""
    conn = get_connection()
    try:
        df = pd.read_sql(
            f"SELECT sender, message FROM chat_logs WHERE username='{username}' AND module='{module}' ORDER BY id ASC LIMIT 50", 
            conn
        )
        return df.to_dict('records')
    except:
        return []
    finally:
        conn.close()

def delete_chat_history(username, module):
    """Permanently wipes chat logs for a specific user and module."""
    conn = get_connection()
    conn.execute(
        "DELETE FROM chat_logs WHERE username=? AND module=?", 
        (username, module)
    )
    conn.commit()
    conn.close()
init_chat_db()
