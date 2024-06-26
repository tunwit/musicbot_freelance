import logsetup #essential
import logging
import subprocess
from discord.ext import commands,tasks
import json
import os
import discord
import wavelink
import random
import spotipy
from spotipy import SpotifyClientCredentials
import pylast
from datetime import datetime
from pymongo.mongo_client import MongoClient
import time
import aioschedule
import sys
import asyncio
import itertools
from logging.handlers import TimedRotatingFileHandler
import winsound

logger = logging.getLogger('littlebirdd')
from config import CONFIG,TOKEN,APPLICATION_ID,LOCAL_LAVALINK,DATABASE,PARENT

close_by_cooling = False
intents = discord.Intents.all()

class Musicbot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            intents=intents,
            command_prefix=CONFIG.get("defualt_prefix"),
            help_command=None,
            application_id=APPLICATION_ID,
        )
        self.config = CONFIG
        self.database = DATABASE

    # Load all commands
    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("_"):
                await bot.load_extension(f"cogs.{filename[:-3]}")

        await self.tree.sync()


bot = Musicbot()

async def node_connect(): 
    if LOCAL_LAVALINK:
        node = wavelink.Node(uri ='http://localhost:2333', password="youshallnotpass",retries=1) # Local Lavalink server
    else:
        node = wavelink.Node(uri ='http://n1.ll.darrennathanael.com:2269', password="glasshost1984") # prefered Lavalink server
        # node2 = wavelink.Node(uri ='http://lavalink.rudracloud.com:2333', password="RudraCloud.com") # reserve Lavalink server
    
    connection = await wavelink.Pool.connect(client=bot, nodes=[node])
    if connection[list(connection)[0]].status == wavelink.NodeStatus.DISCONNECTED:
        if LOCAL_LAVALINK:
            winsound.PlaySound(f'{PARENT}/bot/audio/connect_to_Lava.wav',winsound.SND_FILENAME)
            logger.critical(f"Unable to connect Lavalink, Make sure you have start Lavalink server via this path {PARENT}\\start_lavalink.bat")
            sys.exit("Unable to connect Lavalink")
        else :
            winsound.PlaySound(f'{PARENT}/bot/audio/cannotconnect_contact.wav',winsound.SND_FILENAME)
            logger.critical(f"Unable to connect Lavalink")
            sys.exit("Unable to connect Lavalink")

@bot.event
async def on_ready():
    await node_connect()
    logger.info("-------------------------------")
    logger.info(f"{bot.user} is Ready")
    logger.info("-------------------------------")
    winsound.PlaySound(f'{PARENT}/bot/audio/ready.wav',winsound.SND_FILENAME)


@bot.event
async def on_wavelink_node_ready(node: wavelink.NodeReadyEventPayload):
    logger.info(f"Wavelink {node.node.identifier} connected")

bot.run(TOKEN,log_level=logging.ERROR)
