import os

import re
from dotenv import load_dotenv
from mysql import connector

load_dotenv()


def _get_value_from_brackets(line):
    match = re.search(r'<.*>', line)
    return match.group(0)[1:-1] if match else line


class MysqlConnector:
    def __init__(self):
        self.connection = connector.connect(
            host=os.getenv('MYSQL_HOST'),
            database=os.getenv('MYSQL_DB'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'))

    def fetch_emails(self):
        query = 'SELECT * FROM email;'
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        return result

    def delete_email_by_id(self, email_id):
        query = 'DELETE FROM email WHERE id=%s;'
        with self.connection.cursor() as cursor:
            cursor.execute(query, tuple(email_id))

    def fetch_email_by_id(self, email_id):
        query = 'SELECT * FROM email WHERE id = %s;'
        with self.connection.cursor() as cursor:
            cursor.execute(query, tuple(email_id))
            result = cursor.fetchone()
        return result

    def insert_email(self, email):
        query = 'INSERT INTO email(email_id, msg_from, msg_to, subject) VALUES (%s, %s, %s, %s);'
        values = (
            str(_get_value_from_brackets(email['Message-Id'])),
            str(_get_value_from_brackets(email['From'])),
            str(_get_value_from_brackets(email['To'])),
            str(email['Subject'].strip()),
        )
        with self.connection.cursor() as cursor:
            cursor.execute(query, values)
        self.connection.commit()

    def create_views(self):
        query = """
        CREATE OR REPLACE VIEW received_statistics AS
        SELECT COUNT(*) AS messages_count, msg_from
        FROM email
        GROUP BY msg_from;
        
        CREATE OR REPLACE VIEW recipients_statistics AS
        SELECT COUNT(*) AS messages_count, msg_to
        FROM email
        GROUP BY msg_to;
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query)
