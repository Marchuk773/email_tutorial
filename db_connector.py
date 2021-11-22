import os
import re

from dotenv import load_dotenv
from mysql import connector

load_dotenv()


def _get_value_from_brackets(line):
    match = re.search(r'<.*>', line)
    return match.group(0)[1:-1] if match else line


class MysqlConnector:
    def __init__(self, host=None, port=None):
        self.connection = connector.connect(
            host=host or os.getenv('MYSQL_HOST'),
            port=port or os.getenv('MYSQL_PORT'),
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
            cursor.execute(query, (email_id, ))

    def fetch_email_by_id(self, email_id):
        query = 'SELECT * FROM email WHERE id = %s;'
        with self.connection.cursor() as cursor:
            cursor.execute(query, (email_id, ))
            result = cursor.fetchone()
        return {
            'email_id': result[1],
            'filepath': result[5]
        } if result else None

    def fetch_attachments_by_email_id(self, email_id):
        query = 'SELECT * FROM attachment WHERE email_id = %s;'
        with self.connection.cursor() as cursor:
            cursor.execute(query, (email_id, ))
            result = cursor.fetchall()
        return [{
            'id': attachment[0],
            'email_id': attachment[1],
            'filepath': attachment[2],
            'filename': attachment[2].split('/')[-1]
        } for attachment in result] if result else None

    def fetch_attachments_by_id(self, email_id):
        query = 'SELECT * FROM attachment WHERE id = %s;'
        with self.connection.cursor() as cursor:
            cursor.execute(query, (email_id, ))
            result = cursor.fetchone()
        return {
            'id': result[0],
            'email_id': result[1],
            'filepath': result[2],
            'filename': result[2].split('/')[-1]
        } if result else None

    def insert_email(self, email, parsed_email_path):
        query = ('INSERT INTO email(email_id, msg_from, msg_to, subject, ' +
                 'parsed_email_path) VALUES (%s, %s, %s, %s, %s);')

        values = (str(_get_value_from_brackets(email['Message-Id'])),
                  str(_get_value_from_brackets(email['From'])),
                  str(_get_value_from_brackets(email['To'])),
                  str(email['Subject'].strip()), parsed_email_path)

        with self.connection.cursor() as cursor:
            cursor.execute(query, values)
        self.connection.commit()

    def insert_attachment(self, email, attachment_path):
        query = ('INSERT INTO attachment(email_id, path) ' +
                 'VALUES (%s, %s);')
        values = (_get_value_from_brackets(email['Message-Id']),
                  attachment_path)
        with self.connection.cursor() as cursor:
            cursor.execute(query, values)

    def create_db(self):
        email_query = """
        CREATE TABLE IF NOT EXISTS email (
            id INT PRIMARY KEY AUTO_INCREMENT,
            email_id VARCHAR(120) UNIQUE NOT NULL,
            msg_from VARCHAR(120),
            msg_to VARCHAR(120),
            subject VARCHAR(120),
            parsed_email_path VARCHAR(120)
        );
        """
        attachment_query = """
        CREATE TABLE IF NOT EXISTS attachment (
            id INT PRIMARY KEY AUTO_INCREMENT,
            email_id VARCHAR(120),
            path varchar(120),
            FOREIGN KEY (email_id) REFERENCES email(email_id)
        );
        """
        with self.connection.cursor() as cursor:
            cursor.execute(email_query)
            cursor.execute(attachment_query)

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
