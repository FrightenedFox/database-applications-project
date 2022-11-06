from logging_setup import initialize_logging
from pull_from_usos import pull_data
from db import UsosDB

if __name__ == '__main__':
    initialize_logging()
    db = UsosDB()
    db.connect()
    pull_data(db)
    db.disconnect()

