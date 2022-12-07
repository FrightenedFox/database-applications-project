import asyncio

from ab_project.logging_setup import initialize_logging
from ab_project.pull_from_usos import pull_data
from ab_project.db import UsosDB

if __name__ == '__main__':
    initialize_logging()
    db = UsosDB()
    db.connect()
    asyncio.run(pull_data(db))
    db.disconnect()

