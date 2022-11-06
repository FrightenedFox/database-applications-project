from logging_setup import initialize_logging
from pull_from_usos import pull_data
from db_utils import initialize_db

if __name__ == '__main__':
    initialize_logging()
    # pull_data()
    initialize_db(echo=True)

