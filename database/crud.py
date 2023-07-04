from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from config import db_string
from models import Base

# access to database
try:
    engine = create_engine(db_string)
except Exception as e:
    print('Unable to access postgresql database', repr(e))

# Check if database exists
if not database_exists(engine.url):
    create_database(engine.url)
else:
    # Connect the database if exists.
    conn = engine.connect()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    conn.close()
    