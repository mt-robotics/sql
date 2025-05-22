import os
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# retrieve environment variables
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', 55432)

# dvdrental database
POSTGRES_DB_DVDRENTAL = os.getenv('POSTGRES_DB_DVDRENTAL', 'postgres')
DVDRENTAL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB_DVDRENTAL}"

# northwind database
POSTGRES_DB_NORTHWIND = os.getenv('POSTGRES_DB_NORTHWIND', 'postgres')
NORTHWIND = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB_NORTHWIND}"

# movies database
POSTGRES_DB_MOVIES = os.getenv('POSTGRES_DB_MOVIES', 'postgres')
MOVIES = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB_MOVIES}"