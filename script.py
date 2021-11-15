import os
import re
from email.parser import BytesParser
from email.policy import default
import mysql.connector


class EmailFields:
    msg_id = "Message-Id"
    msg_to = "To"
    msg_from = "From"
    msg_reply_to = "Reply-To"
    msg_subject = "Subject"


def get_value_from_brackets(line):
    match = re.search(r"<.*>", line)
    return match.group(0)[1:-1] if match else line


def parse_email(file):
    with open(file, "rb") as f:
        return BytesParser(policy=default).parse(f)


def prepare_insert_email_query(email):
    query = "INSERT INTO email(email_id, msg_from, msg_to, subject) VALUES (%s, %s, %s, %s);"
    values = [
        str(get_value_from_brackets(email[EmailFields.msg_id])),
        str(get_value_from_brackets(email[EmailFields.msg_from])),
        str(get_value_from_brackets(email[EmailFields.msg_to])),
        str(email[EmailFields.msg_subject].strip()),
    ]
    return query, values


def prepare_views_query():
    return """
    CREATE OR REPLACE VIEW received_statistics AS
    SELECT COUNT(*) AS messages_count, msg_from
    FROM email
    GROUP BY msg_from;
    
    CREATE OR REPLACE VIEW recipients_statistics AS
    SELECT COUNT(*) AS messages_count, msg_to
    FROM email
    GROUP BY msg_to;
    """


DIRECTORY = "./emails"


def main():
    email_files = [
        os.path.join(DIRECTORY, file)
        for file in os.listdir(DIRECTORY)
        if file.endswith(".eml")
    ]
    parsed_emails = [parse_email(email) for email in email_files]

    connection = mysql.connector.connect(
        host="localhost", database="email_test", user="root", password="pass"
    )
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE email;")

        for email in parsed_emails:
            cursor.execute(*prepare_insert_email_query(email))
        connection.commit()

        cursor.execute(prepare_views_query(), multi=True)


if __name__ == "__main__":
    main()
