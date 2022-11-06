from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = automap_base()
SessionLocal = scoped_session(sessionmaker())


def initialize_db(echo: bool = False) -> Engine:
    """Initializes engine of the database."""
    engine = create_engine("postgresql+psycopg2://vmorskyi:psql3FS-DI@localhost:5432/usos",
                           echo=echo,
                           future=True)
    return engine


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
