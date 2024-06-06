import json
from dotenv import load_dotenv
import logging
import os
import sqlite3
import requests
import sys
import subprocess
import time 
logger = logging.getLogger('littlebirdd')

path = os.getcwd()
PARENT = os.path.abspath(os.path.join(path, os.pardir))

with open(f"{PARENT}\\_config.json", "r") as f:
    config = json.load(f)


load_dotenv('.env.development')
logger.info('Load new .env.development')

connection = sqlite3.connect(f'{PARENT}\\bot\\data\\bot_data.db')
connection.execute(''' 
        CREATE TABLE IF NOT EXISTS search_history (
        id      INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        music   TEXT ,
        times   INTEGER 
        );
        ''')
connection.commit()

LOCAL_LAVALINK = config['local_lavalink']
if LOCAL_LAVALINK:
    logger.info("using Local Lavalink")
    if not os.path.isfile(f"{PARENT}\\bot\\lavalink\\Lavalink.jar"):
        try:
            logger.info('Downloading Lavalink.jar.')
            response = requests.get('https://github.com/lavalink-devs/Lavalink/releases/download/4.0.5/Lavalink.jar', stream=True)
            response.raise_for_status()
            with open(f"{PARENT}\\bot\\lavalink\\Lavalink.jar", 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            logger.info('Lavalink success fully dowloaded')        
        except requests.exceptions.RequestException as e:
            logger.info(f'Fail to dowload Lavalike due to \n{e}')  
            sys.exit()

    if not os.path.isfile(f"{PARENT}\\start_lavalink.bat"):      
        with open(f'{PARENT}\\start_lavalink.bat', "w") as bat_file:
            bat_file.write(f"""start cmd.exe /k "cd bot\lavalink && java -jar lavalink.jar""")   

CONFIG = config
TOKEN = os.getenv('TOKEN')
APPLICATION_ID = os.getenv('APPLICATION_ID')
DATABASE = connection

