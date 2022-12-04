from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine
from src.config.config import config

DB = PostgresEngine(config={
        "database": config['POSTGRES_DB'],
        "user": config['POSTGRES_USER'],
        "password": config['POSTGRES_PASSWORD'],
        "host": config['POSTGRES_HOST'],
        "port": config['POSTGRES_PORT'],
})


# A list of paths to piccolo apps
# e.g. ['blog.piccolo_app']
APP_REGISTRY = AppRegistry(apps=['market_data_piccolo.piccolo_app'])
