import json
from dotenv import load_dotenv
import logging
import os
import sqlite3

logger = logging.getLogger('littlebirdd')

path = os.getcwd()
parent = os.path.abspath(os.path.join(path, os.pardir))

with open(f"{parent}\\_config.json", "r") as f:
    config = json.load(f)


load_dotenv('.env.development')
logger.info('Load new .env.development')

connection = sqlite3.connect(f'{parent}\\bot\\data\\bot_data.db')
connection.execute(''' 
        CREATE TABLE IF NOT EXISTS search_history (
        id      INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        music   TEXT ,
        times   INTEGER 
        );
        ''')
connection.commit()

CONFIG = config
TOKEN = os.getenv('TOKEN')
APPLICATION_ID = os.getenv('APPLICATION_ID')
DATABASE = connection
