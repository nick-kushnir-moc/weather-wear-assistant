import psycopg2
from sqlalchemy.ext.declarative import declarative_base

# Database Connection Parameters
db_params = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "mocAi",
    "host": "localhost",
    "port": 5432
}

Base = declarative_base()

# Database connection
def get_db():
    db = psycopg2.connect(**db_params)
    try:
        yield db
    finally:
        db.close()