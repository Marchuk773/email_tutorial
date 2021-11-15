import argparse
import os
from email.parser import BytesParser
from email.policy import default
from glob import glob

import db_connector


def parse_email(file):
    with open(file, 'rb') as f:
        return BytesParser(policy=default).parse(f)


def main():
    parser = argparse.ArgumentParser(
        description='Specify input and output directories.')

    parser.add_argument('-i', '--input', default='./emails')
    args = parser.parse_args()

    connector = db_connector.MysqlConnector()
    email_files = glob(args.input + '/*.eml')

    for file in email_files:
        parsed_email = parse_email(file)
        connector.insert_email(parsed_email)
        os.rename(file, file + ".bkp")


if __name__ == '__main__':
    main()
