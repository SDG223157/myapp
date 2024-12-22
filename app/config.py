import os
from dotenv import load_dotenv

load_dotenv()

# Get database configuration with validation
DB_HOST = os.getenv('MYSQL_HOST')
if not DB_HOST:
    raise ValueError("MYSQL_HOST environment variable is not set")

DB_USER = os.getenv('MYSQL_USER')
if not DB_USER:
    raise ValueError("MYSQL_USER environment variable is not set")

DB_PASSWORD = os.getenv('MYSQL_PASSWORD')
if not DB_PASSWORD:
    raise ValueError("MYSQL_PASSWORD environment variable is not set")

DB_NAME = os.getenv('MYSQL_DATABASE')
if not DB_NAME:
    raise ValueError("MYSQL_DATABASE environment variable is not set")

DB_PORT = os.getenv('MYSQL_PORT', '3306')

class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Print the URI for debugging (without password)
    def __init__(self):
        debug_uri = f"mysql+mysqlconnector://{DB_USER}:xxxxx@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        print(f"Database URI (sanitized): {debug_uri}")