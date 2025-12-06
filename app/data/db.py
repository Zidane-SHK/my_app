import sqlite3
import bcrypt
import pandas as pd
from pathlib import Path

DATA_DIR = Path("DATA")
DB_PATH = DATA_DIR / "intelligence_platform.db"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def connect_database(db_path=DATA_DIR):
    """Connect to SQLite database."""
    return sqlite3.connect(str(db_path))

def connect_database(db_path=DATA_DIR):
    """
    Connect to the SQLite database.
    Creates the database file if it doesn't exist.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        sqlite3.Connection: Database connection object
    """
    conn = sqlite3.connect(str(db_path))
    return conn

# Test the connection
test_conn = connect_database()
print(" Database connection successful!")
print(f"Database type: {type(test_conn)}")
test_conn.close()
print(" Connection closed.")

def create_users_table(conn):
    """
    Create the users table if it doesn't exist.
    
    Args:
        conn: Database connection object
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    );
    """
    
    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()
    print(" Users table created successfully!")

# Test: Create the users table
conn = connect_database()
create_users_table(conn)
conn.close()

def create_cyber_incidents_table(conn):
    """
    Create the cyber_incidents table matching the CSV structure.
    """
    # Schema matches 'cyber-operations-incidents(in).csv' columns
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS cyber_incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        date TEXT,
        affiliations TEXT,
        description TEXT,
        response TEXT,
        victims TEXT,
        sponsor TEXT,
        type TEXT,
        category TEXT,
        sources_1 TEXT,
        sources_2 TEXT,
        sources_3 TEXT
    );
    """
    
    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()
    print(" Cyber incidents table created (matches CSV structure)!")

def create_datasets_metadata_table(conn):
    """
    Create the datasets_metadata table.
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS datasets_metadata (
        dataset_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_name TEXT NOT NULL,
        description TEXT,
        source_path TEXT,
        file_format TEXT,
        total_records INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        owner_id INTEGER,
        FOREIGN KEY(owner_id) REFERENCES users(id)
    );
    """
    
    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()
    print(" Datasets metadata table created!")

def create_it_tickets_table(conn):
    """
    Create the it_tickets table.
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS it_tickets (
        ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        description TEXT,
        category TEXT CHECK(category IN ('Hardware', 'Software', 'Network', 'Access')),
        priority TEXT CHECK(priority IN ('Low', 'Medium', 'High', 'Critical')),
        status TEXT DEFAULT 'Open',
        requester_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(requester_id) REFERENCES users(id)
    );
    """
    
    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()
    print(" IT tickets table created!")

def import_cyber_data_from_csv(conn, csv_path="cyber-operations-incidents(in).csv"):
    """
    Helper function to load the CSV data into the table.
    """
    import pandas as pd
    import os
    
    if not os.path.exists(csv_path):
        print(f"Skipping import: {csv_path} not found.")
        return

    try:
        df = pd.read_csv(csv_path)
        # Clean column names to match DB schema if necessary, or rely on order
        # We'll map DataFrame columns to the table structure defined above
        # Table columns (excluding id): title, date, affiliations, description, response, victims, sponsor, type, category, sources_1, sources_2, sources_3
        
        # Ensure header names match what we expect from the file
        expected_cols = ['Title', 'Date', 'Affiliations', 'Description', 'Response', 
                         'Victims', 'Sponsor', 'Type', 'Category', 'Sources_1', 'Sources_2', 'Sources_3']
        
        # Insert data
        cursor = conn.cursor()
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT INTO cyber_incidents 
                (title, date, affiliations, description, response, victims, sponsor, type, category, sources_1, sources_2, sources_3)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(row[col] for col in expected_cols))
            
        conn.commit()
        print(f"Successfully imported {len(df)} rows into cyber_incidents!")
    except Exception as e:
        print(f"Error importing CSV: {e}")

def create_all_tables(conn):
    """
    Create all tables for the intelligence platform.
    """
    create_users_table(conn) # Assumes this is defined in your previous block
    create_cyber_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)
    
    # Optional: Automatically import data if file exists
    import_cyber_data_from_csv(conn)
    
    print("\n🎉 All tables created and initialized successfully!")

# Test: Create all tables
if __name__ == "__main__":
    conn = connect_database()
    create_all_tables(conn)
    conn.close()

def migrate_users_from_file(conn, filepath=DATA_DIR / "users.txt"):
    """
    Migrate users from users.txt to the database.
    
    Args:
        conn: Database connection
        filepath: Path to users.txt file
        
    Returns:
        int: Number of users migrated
    """
    path = Path(filepath)
    
    # Check if file exists
    if not path.exists():
        print(f"Warning: {filepath} not found. Skipping migration.")
        return 0
    
    cursor = conn.cursor()
    migrated_count = 0
    
    # Read the file line by line
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            
            # Parse the line
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 2:
                continue
            
            username = parts[0]
            password_hash = parts[1]
            role = parts[2] if len(parts) >= 3 else "user"
            
            # Insert into database using parameterized query
            try:
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, password_hash, role)
                )
                migrated_count += 1
            except sqlite3.IntegrityError:
                # User already exists (username is UNIQUE)
                print(f" User '{username}' already exists. Skipping.")
    
    conn.commit()
    return migrated_count

# Test: Migrate users
conn = connect_database()
create_users_table(conn)  # Ensure table exists
count = migrate_users_from_file(conn)
print(f"\nSuccessfully migrated {count} user(s) from users.txt to database!")
conn.close()

# Verify users were migrated
conn = connect_database()
cursor = conn.cursor()

# Query all users
cursor.execute("SELECT id, username, role FROM users")
users = cursor.fetchall()

print(" Users in database:")
print(f"{'ID':<5} {'Username':<15} {'Role':<10}")
print("-" * 35)
for user in users:
    print(f"{user[0]:<5} {user[1]:<15} {user[2]:<10}")

print(f"\nTotal users: {len(users)}")
conn.close()

def register_user(username, password, role="user"):
    """
    Register a new user in the database.
    
    Args:
        username: User's login name
        password: Plain text password (will be hashed)
        role: User role (default: 'user')
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate input
    if not username or not password:
        return False, "Username and password are required."
    
    conn = connect_database()
    cursor = conn.cursor()
    
    # Ensure users table exists
    create_users_table(conn)
    
    # Check if username already exists
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, f"Username '{username}' already exists."
    
    # Hash the password
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    password_hash_str = password_hash.decode("utf-8")
    
    # Insert new user
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash_str, role)
    )
    conn.commit()
    conn.close()
    
    return True, f"User '{username}' registered successfully with role '{role}'."

# Test: Register a new user
success, message = register_user("charlie", "SecurePass123!", "analyst")
print(f"{'' if success else ''} {message}")

def login_user(username, password):
    """
    Authenticate a user against the database.
    
    Args:
        username: User's login name
        password: Plain text password to verify
        
    Returns:
        tuple: (success: bool, message: str)
    """
    conn = connect_database()
    cursor = conn.cursor()
    
    # Look up user
    cursor.execute(
        "SELECT password_hash, role FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()
    
    # User not found
    if not row:
        return False, "User not found."
    
    stored_hash, role = row
    
    # Verify password
    if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        return True, f"Login successful! Welcome {username} (role: {role})."
    else:
        return False, "Incorrect password."

# Test: Login with correct password
print("\n Testing login...")
success, message = login_user("charlie", "SecurePass123!")
print(f"{'' if success else ''} {message}")

# Test: Login with wrong password
success, message = login_user("charlie", "WrongPassword")
print(f"{'' if success else ''} {message}")

def load_csv_to_table(conn, csv_path, table_name):
    """
    Load a CSV file into a database table using pandas.
    
    Args:
        conn: Database connection
        csv_path: Path to CSV file
        table_name: Name of the database table
        
    Returns:
        int: Number of rows loaded
    """
    path = Path(csv_path)
    
    # Check if file exists
    if not path.exists():
        print(f" Warning: {csv_path} not found. Skipping.")
        return 0
    
    # Read CSV into DataFrame
    df = pd.read_csv(path)
    
    # Clean column names (remove extra whitespace)
    df.columns = df.columns.str.strip()
    
    # Preview data
    print(f"\n Loading {csv_path}...")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Rows: {len(df)}")
    
    
    
    # Load into database
    df.to_sql(table_name, conn, if_exists='append', index=False)
    
    print(f"    Loaded {len(df)} rows into '{table_name}' table.")
    return len(df)

def load_all_csv_data(conn):
    """
    Load all three domain CSV files into the database.
    """
    print("\n Starting CSV data loading...")
    
    total_rows = 0
    
    # Load cyber incidents
    total_rows += load_csv_to_table(
        conn,
        DATA_DIR / "cyber_incidents.csv",
        "cyber_incidents"
    )
    
    # Load datasets metadata
    total_rows += load_csv_to_table(
        conn,
        DATA_DIR / "datasets_metadata.csv",
        "datasets_metadata"
    )
    
    # Load IT tickets
    total_rows += load_csv_to_table(
        conn,
        DATA_DIR / "it_tickets.csv",
        "it_tickets"
    )
    
    print(f"\nTotal rows loaded: {total_rows}")
    return total_rows

# Test: Load all CSV files
conn = connect_database()
create_all_tables(conn)  # Ensure tables exist
load_all_csv_data(conn)
conn.close()

def insert_incident(conn, date, incident_type, severity, status, description, reported_by=None):
    """
    Insert a new cyber incident into the database.
    
    Args:
        conn: Database connection
        date: Incident date (YYYY-MM-DD)
        incident_type: Type of incident (e.g., 'Phishing', 'Malware')
        severity: Severity level (e.g., 'High', 'Medium', 'Low')
        status: Current status (e.g., 'Open', 'Investigating', 'Resolved')
        description: Incident description
        reported_by: Username of reporter (optional)
        
    Returns:
        int: ID of the newly inserted incident
    """
    #TODO: Complete the function to insert a new incident into the cyber_incidents table.

# Test: Insert a new incident
conn = connect_database()
new_id = insert_incident(
    conn,
    date="2024-11-05",
    incident_type="Phishing",
    severity="High",
    status="Open",
    description="Suspicious email with malicious link detected.",
    reported_by="charlie"
)
conn.close()


def get_all_incidents(conn):
    """
    Retrieve all incidents from the database.
    
    Returns:
        pandas.DataFrame: All incidents
    """
    query = "SELECT * FROM cyber_incidents ORDER BY id DESC"
    df = pd.read_sql_query(query, conn)
    return df

def get_incidents_by_severity(conn, severity):
    """
    Retrieve incidents filtered by severity.
    
    Args:
        conn: Database connection
        severity: Severity level to filter by
        
    Returns:
        pandas.DataFrame: Filtered incidents
    """
    # Use parameterized query
    # TODO: Complete the function to retrieve incidents by severity.


def get_incidents_by_status(conn, status):
    """
    Retrieve incidents filtered by status.
    """
    #TODO: Complete the function to retrieve incidents by status.

# Test: Query incidents
conn = connect_database()

print("\nAll incidents:")
df_all = get_all_incidents(conn)
print(df_all.head())
print(f"Total incidents: {len(df_all)}")

print("\n High severity incidents:")
df_high = get_incidents_by_severity(conn, "High")
print(df_high.head())
print(f"High severity count: {len(df_high)}")

conn.close()

def update_incident_status(conn, incident_id, new_status):
    """
    Update the status of an incident.
    
    Args:
        conn: Database connection
        incident_id: ID of the incident to update
        new_status: New status value
        
    Returns:
        bool: True if update was successful
    """
    cursor = conn.cursor()
    
    # Use parameterized query
    cursor.execute(
        "UPDATE cyber_incidents SET status = ? WHERE id = ?",
        (new_status, incident_id)
    )
    
    conn.commit()
    rows_affected = cursor.rowcount
    
    if rows_affected > 0:
        print(f"✅ Incident #{incident_id} status updated to '{new_status}'.")
        return True
    else:
        print(f"⚠️ No incident found with ID {incident_id}.")
        return False

# Test: Update an incident
conn = connect_database()

# Get the first incident
df = get_all_incidents(conn)
if len(df) > 0:
    first_id = df.iloc[0]['id']
    print(f"\n Updating incident #{first_id}...")
    update_incident_status(conn, first_id, "Resolved")
    
    # Verify the update
    df_updated = pd.read_sql_query(
        "SELECT id, status FROM cyber_incidents WHERE id = ?",
        conn,
        params=(first_id,)
    )
    print(f"   New status: {df_updated.iloc[0]['status']}")

conn.close()

def delete_incident(conn, incident_id):
    """
    Delete an incident from the database.
    
    Args:
        conn: Database connection
        incident_id: ID of the incident to delete
        
    Returns:
        bool: True if deletion was successful
    """
    cursor = conn.cursor()
    
    # CRITICAL: Always use WHERE clause with DELETE!
    cursor.execute(
        "DELETE FROM cyber_incidents WHERE id = ?",
        (incident_id,)
    )
    
    conn.commit()
    rows_affected = cursor.rowcount
    
    if rows_affected > 0:
        print(f" Incident #{incident_id} deleted successfully.")
        return True
    else:
        print(f"No incident found with ID {incident_id}.")
        return False

# Test: Delete an incident (commented out for safety)
# conn = connect_database()
# delete_incident(conn, 999)  # Replace with actual ID to test
# conn.close()

print(" DELETE function defined but not executed (for safety).")
print("   Uncomment the test code above to try deleting an incident.")

def get_incidents_by_type_count(conn):
    """
    Count incidents by type.
    Uses: SELECT, FROM, GROUP BY, ORDER BY
    """
    query = """
    SELECT incident_type, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY incident_type
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_high_severity_by_status(conn):
    """
    Count high severity incidents by status.
    Uses: SELECT, FROM, WHERE, GROUP BY, ORDER BY
    """
    query = """
    SELECT status, COUNT(*) as count
    FROM cyber_incidents
    WHERE severity = 'High'
    GROUP BY status
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def get_incident_types_with_many_cases(conn, min_count=5):
    """
    Find incident types with more than min_count cases.
    Uses: SELECT, FROM, GROUP BY, HAVING, ORDER BY
    """
    query = """
    SELECT incident_type, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY incident_type
    HAVING COUNT(*) > ?
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn, params=(min_count,))
    return df

# Test: Run analytical queries
conn = connect_database()

print("\n Incidents by Type:")
df_by_type = get_incidents_by_type_count(conn)
print(df_by_type)

print("\n High Severity Incidents by Status:")
df_high_severity = get_high_severity_by_status(conn)
print(df_high_severity)

print("\n Incident Types with Many Cases (>5):")
df_many_cases = get_incident_types_with_many_cases(conn, min_count=5)
print(df_many_cases)

conn.close()

def setup_database_complete():
    """
    Complete database setup:
    1. Connect to database
    2. Create all tables
    3. Migrate users from users.txt
    4. Load CSV data for all domains
    5. Verify setup
    """
    print("\n" + "="*60)
    print("STARTING COMPLETE DATABASE SETUP")
    print("="*60)
    
    # Step 1: Connect
    print("\n[1/5] Connecting to database...")
    conn = connect_database()
    print("       Connected")
    
    # Step 2: Create tables
    print("\n[2/5] Creating database tables...")
    create_all_tables(conn)
    
    # Step 3: Migrate users
    print("\n[3/5] Migrating users from users.txt...")
    user_count = migrate_users_from_file(conn)
    print(f"       Migrated {user_count} users")
    
    # Step 4: Load CSV data
    print("\n[4/5] Loading CSV data...")
    total_rows = load_all_csv_data(conn)
    
    # Step 5: Verify
    print("\n[5/5] Verifying database setup...")
    cursor = conn.cursor()
    
    # Count rows in each table
    tables = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']
    print("\n Database Summary:")
    print(f"{'Table':<25} {'Row Count':<15}")
    print("-" * 40)
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:<25} {count:<15}")
    
    conn.close()
    
    print("\n" + "="*60)
    print(" DATABASE SETUP COMPLETE!")
    print("="*60)
    print(f"\n Database location: {DB_PATH.resolve()}")
    print("\nYou're ready for Week 9 (Streamlit web interface)!")

# Run the complete setup
setup_database_complete()

def run_comprehensive_tests():
    """
    Run comprehensive tests on your database.
    """
    print("\n" + "="*60)
    print("🧪 RUNNING COMPREHENSIVE TESTS")
    print("="*60)
    
    conn = connect_database()
    
    # Test 1: Authentication
    print("\n[TEST 1] Authentication")
    success, msg = register_user("test_user", "TestPass123!", "user")
    print(f"  Register: {'✅' if success else '❌'} {msg}")
    
    success, msg = login_user("test_user", "TestPass123!")
    print(f"  Login:    {'✅' if success else '❌'} {msg}")
    
    # Test 2: CRUD Operations
    print("\n[TEST 2] CRUD Operations")
    
    # Create
    test_id = insert_incident(
        conn,
        "2024-11-05",
        "Test Incident",
        "Low",
        "Open",
        "This is a test incident",
        "test_user"
    )
    print(f"  Create: ✅ Incident #{test_id} created")
    
    # Read
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents WHERE id = ?",
        conn,
        params=(test_id,)
    )
    print(f"  Read:    Found incident #{test_id}")
    
    # Update
    update_incident_status(conn, test_id, "Resolved")
    print(f"  Update:  Status updated")
    
    # Delete
    delete_incident(conn, test_id)
    print(f"  Delete:  Incident deleted")
    
    # Test 3: Analytical Queries
    print("\n[TEST 3] Analytical Queries")
    
    df_by_type = get_incidents_by_type_count(conn)
    print(f"  By Type:     Found {len(df_by_type)} incident types")
    
    df_high = get_high_severity_by_status(conn)
    print(f"  High Severity: Found {len(df_high)} status categories")
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)

# Run tests
run_comprehensive_tests()