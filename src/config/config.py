import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'POSTGRES_HOST': os.environ['POSTGRES_HOST'],
    'POSTGRES_DB': os.environ['POSTGRES_DB'],
    'POSTGRES_USER': os.environ['POSTGRES_USER'],
    'POSTGRES_PASSWORD': os.environ['POSTGRES_PASSWORD'],
    'POSTGRES_PORT': os.environ['POSTGRES_PORT'] or 5432
}