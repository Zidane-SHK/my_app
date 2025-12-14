import database.db as db

class SecurityIncident:
    TABLE_NAME = "security_incidents"

    @staticmethod
    def get_all_incidents():
        return db.fetch_all(SecurityIncident.TABLE_NAME)

    @staticmethod
    def log_incident(issue_type, description, priority, status):
        db.add_entry(SecurityIncident.TABLE_NAME, issue_type, description, priority, status)

    @staticmethod
    def update_incident(ticket_id, issue_type, description, priority, status):
        db.update_entry(SecurityIncident.TABLE_NAME, ticket_id, issue_type, description, priority, status)

    @staticmethod
    def delete_incident(ticket_id):
        db.delete_entry(SecurityIncident.TABLE_NAME, ticket_id)