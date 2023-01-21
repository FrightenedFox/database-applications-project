import argparse
import asyncio

from ab_project.usosapi.usosapi import USOSAPIConnection
from ab_project.logging_setup import initialize_logging
from ab_project.pull_from_usos import pull_data
from ab_project.db import UsosDB
from ab_project.config.config import app_config


parser = argparse.ArgumentParser(description='Receive USOS connection.')
parser.add_argument('--access_token', type=str, dest="access_token", required=True,
                    help='USOS API connection access token')
parser.add_argument('--access_token_secret', type=str, dest="access_token_secret", required=True,
                    help='USOS API connection access token secret')

args = parser.parse_args()

if __name__ == '__main__':
    initialize_logging()
    usos_connection = USOSAPIConnection(
        api_base_address=app_config.usosapi.api_base_address,
        consumer_key=app_config.usosapi.consumer_key,
        consumer_secret=app_config.usosapi.consumer_secret
    )
    usos_connection.set_access_data(
        access_token=args.access_token,
        access_token_secret=args.access_token_secret
    )
    db = UsosDB()
    db.connect()
    for _ in range(10):
        try:
            asyncio.run(pull_data(usos_connection, db))
        except:
            pass
        else: 
            break
    db.disconnect()

