import database.db as db

class Dataset:
    TABLE_NAME = "data_science_projects"

    @staticmethod
    def get_all_projects():
        return db.fetch_all(Dataset.TABLE_NAME)

    @staticmethod
    def create_project(issue_type, description, priority, status):
        db.add_entry(Dataset.TABLE_NAME, issue_type, description, priority, status)

    @staticmethod
    def update_project(ticket_id, issue_type, description, priority, status):
        db.update_entry(Dataset.TABLE_NAME, ticket_id, issue_type, description, priority, status)

    @staticmethod
    def delete_project(ticket_id):
        db.delete_entry(Dataset.TABLE_NAME, ticket_id)