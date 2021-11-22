import argparse
import os
import re
from email.parser import BytesParser
from email.policy import default
from glob import glob

import db_connector


def parse_email(file):
    with open(file, 'rb') as f:
        return BytesParser(policy=default).parse(f)


def get_attachments_name(attachment):
    match = re.search(r'name=".*"', attachment)
    return match.group(0)[6:-1] if match else attachment


def store_file(email_body, output_dir):
    with open(output_dir, 'wb') as f:
        f.write(bytes(email_body))


def main():
    parser = argparse.ArgumentParser(
        description='Specify directories for input, output and attachments.')

    parser.add_argument('-i', '--input', default='emails')
    parser.add_argument('-o', '--output', default='parsed_emails')
    parser.add_argument('-a', '--attachments', default='attachments')
    args = parser.parse_args()

    connector = db_connector.MysqlConnector(host="localhost", port=3307)
    email_files = glob(f'./{args.input}/*.eml')

    for file in email_files:
        parsed_email = parse_email(file)
        new_path = f'./{args.output}{file[len(args.input) + 2:-4]}'
        connector.insert_email(parsed_email, new_path)
        store_file(bytes(parsed_email.get_body()), new_path)
        for attachment in parsed_email.iter_attachments():
            filename = get_attachments_name(attachment['Content-Type'])
            attachment_path = f'./static/{args.attachments}/{filename}'
            store_file(attachment.get_payload(decode=True), attachment_path)
            connector.insert_attachment(parsed_email, attachment_path)

        os.rename(file, file + ".bkp")


if __name__ == '__main__':
    main()
