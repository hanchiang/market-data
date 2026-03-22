import os
from dotenv import load_dotenv

load_dotenv()

required_keys = [
    'POSTGRES_HOST',
    'POSTGRES_DB',
    'POSTGRES_USER',
    'POSTGRES_PASSWORD',
]

missing_keys = [key for key in required_keys if not os.getenv(key)]
if missing_keys:
    raise RuntimeError(f'Missing required environment variables: {", ".join(missing_keys)}')

config = {
    'POSTGRES_HOST': os.environ['POSTGRES_HOST'],
    'POSTGRES_DB': os.environ['POSTGRES_DB'],
    'POSTGRES_USER': os.environ['POSTGRES_USER'],
    'POSTGRES_PASSWORD': os.environ['POSTGRES_PASSWORD'],
    'POSTGRES_PORT': int(os.getenv('POSTGRES_PORT', '5432')),
}
