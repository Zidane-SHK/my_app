from models.user import User
import sqlite3

class AuthManager:
    
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def login(self, username, password):
        if not username or not password:
            return None

        query = "SELECT password_hash, role FROM users WHERE username = ?"
        result = self.db_manager.fetch_one(query, (username,))

        if result:
            stored_password, role = result
            
            if password == stored_password:
                return User(username, stored_password, role)
        
        return None

    def register(self, username, password):
        """Registers a new user into the database."""
        if not username or not password:
            return False

        check_query = "SELECT 1 FROM users WHERE username = ?"
        if self.db_manager.fetch_one(check_query, (username,)):
            return False 

        try:
            insert_sql = "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)"
            self.db_manager.execute_query(insert_sql, (username, password, "user"))
            return True
        except Exception as e:
            print(f"Registration error: {e}")
            return False