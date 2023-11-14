import sqlite3

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def add_check(self, user_id, bill_id):
        with self.connection:
            self.cursor.execute("INSERT INTO 'check' ('user_id', 'bill_id') VALUES (?, ?)", (user_id, bill_id))

    def get_check(self, bill_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM 'check' WHERE 'bill_id' = ?", (bill_id, )).fetchmany(1)
            if not bool(len(result)):
                return False
            return result[0]

    def delete_check(self, bill_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM 'check' WHERE 'bill_id' = ?", (bill_id,))
       