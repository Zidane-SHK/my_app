import database.db as db

class ITTicket:
    TABLE_NAME = "it_tickets"

    @staticmethod
    def get_all_tickets():
        return db.fetch_all(ITTicket.TABLE_NAME)

    @staticmethod
    def create_ticket(issue_type, description, priority, status):
        db.add_entry(ITTicket.TABLE_NAME, issue_type, description, priority, status)

    @staticmethod
    def update_ticket(ticket_id, issue_type, description, priority, status):
        db.update_entry(ITTicket.TABLE_NAME, ticket_id, issue_type, description, priority, status)

    @staticmethod
    def delete_ticket(ticket_id):
        db.delete_entry(ITTicket.TABLE_NAME, ticket_id)