from flask import Flask
from flask import jsonify
from flask.globals import request
import db_connector

app = Flask(__name__)

connector = db_connector.MysqlConnector()


@app.route('/emails', methods=['GET'])
def get_emails():
    emails = connector.fetch_emails()
    return jsonify(emails)


@app.route('/email/<email_id>', methods=['GET', 'DELETE'])
def handle_email(email_id):
    if request.method == 'GET':
        email = connector.fetch_email_by_id(email_id)
        return jsonify(email)
    elif request.method == 'DELETE':
        connector.delete_email_by_id(email_id)
        return f'Email with id {email_id} deleted!'


if __name__ == '__main__':
    app.run()
