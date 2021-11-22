from flask import Flask, jsonify, redirect, render_template, send_file, url_for
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
    email_id = int(email_id)
    if request.method == 'GET':
        email = connector.fetch_email_by_id(email_id)
        if not email:
            return f'No email with id {email_id}', 404
        with open(email['filepath'], 'r') as email_file:
            email_body = email_file.read()
        attachments = connector.fetch_attachments_by_email_id(
            email['email_id'])
        return render_template('email_viewer.html',
                               email_body=email_body,
                               attachments=attachments)
    elif request.method == 'DELETE':
        connector.delete_email_by_id(email_id)
        return f'Email with id {email_id} deleted!'


@app.route('/download/<email_id>', methods=['GET'])
def download_attachment(email_id):
    email_id = int(email_id)
    filepath = connector.fetch_attachments_by_id(email_id)['filepath']
    return send_file(filepath, as_attachment=True)


@app.route('/display')
def display_image():
    filepath = request.args.get('filepath')[2:]
    return redirect(url_for('static', filename=filepath), code=301)


if __name__ == '__main__':
    connector.create_db()
    app.run(host="0.0.0.0", port=5000)
