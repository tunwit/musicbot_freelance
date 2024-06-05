from typing import List, Optional
import discord
from discord.ext import commands
import wavelink
import asyncio
import json
from async_timeout import timeout
import math
import itertools
from cogs.createsource import createsource
import random
from discord.ui import Button, View
from discord import app_commands
from discord.app_commands import Choice
import random
from ui.embed_gen import createembed
from ui.language_respound import get_respound
from ui.button import buttin
from ui.controlpanal import *
import requests
import random
import os
import datetime
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import datetime
from urllib.parse import urlparse
from PIL import Image, ImageDraw 
import io
import logging
import sys
logger = logging.getLogger('littlebirdd')

def unhandle_exception(exc_type, exc_value, exc_traceback):
    logger = logging.getLogger('littlebirdd')
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = unhandle_exception
trans_queueMode= {
            'wavelink.QueueMode.normal':"Disable",
            'wavelink.QueueMode.loop':"Song",
            'wavelink.QueueMode.loop_all':"Queue"
        }

trans_autoMode= {
            'wavelink.AutoPlayMode.partial':"Disable",
            'wavelink.AutoPlayMode.enabled':"Enable"
        }

def convert(milliseconds):
    seconds = milliseconds // 1000  # Convert milliseconds to seconds
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)


async def check_before_play(interaction: discord.Interaction):
    vc: wavelink.Player = interaction.guild.voice_client
    respound = get_respound(interaction.locale, "check_before_play")
    if vc == None:
        embed = createembed.embed_fail(interaction,respound['novc'])
        await interaction.followup.send(embed=embed, ephemeral=True)
        return False
    if interaction.user.voice == None:
        embed = createembed.embed_fail(interaction,respound['usernotin'])
        await interaction.followup.send(embed=embed, ephemeral=True)
        return False
    if interaction.guild.voice_client.channel != interaction.user.voice.channel:
        embed = createembed.embed_fail(interaction,respound['diffchan'])
        await interaction.followup.send(embed=embed, ephemeral=True)
        return False
    return True


class nowplaying: 

    async def np2(self,interaction, send=False): # image with progressbar
            vc: wavelink.Player = interaction.guild.voice_client
            respound = get_respound(interaction.locale, "np")
            if vc:
                if vc.current is not None:
                    lst = list(vc.queue)
                    if vc.queue.mode == wavelink.QueueMode.loop_all:
                        lst = lst +list(vc.queue.history)
                    upcoming = list(itertools.islice(lst,0, 4))
                    fmt = "\n".join(
                        f'` {index}.{track} `' for index,track in enumerate(upcoming,start=1)  
                    )    
                    try:
                        duration = f"{convert(vc.position)}/{convert(vc.current.length)}"
                    except:
                        duration = respound.get("unable_duration")
                    npembed = discord.Embed(
                        title=f"{vc.current.title}  <a:blobdancee:969575788389220392>",
                        url=vc.current.uri,
                        color=0xFFFFFF,
                    )
                    npembed.set_author(
                        name=f"{respound.get('addedby')} {vc.current.extras.requester}",
                        icon_url=f"{vc.current.extras.requester_icon}",
                    )
                    npembed.add_field(
                        name=f"{respound.get('playingin')}", value=f"<#{vc.channel.id}>"
                    )
                    npembed.add_field(
                        name=f"{respound.get('duration')}", value=f"`{duration}`"
                    )
                    npembed.set_footer(
                        text=f"{'Paused'if vc.paused else 'Playing'} | {vc.volume}% | LoopStatus:{trans_queueMode[f'wavelink.{str(vc.queue.mode)}']} | Autoplay:{trans_autoMode[f'wavelink.{str(vc.autoplay)}']}"
                    )
                    npembed.set_image(url=vc.current.artwork)
                    more = f"`{respound.get('andmore').format(more=len(lst)-4)}`"
                    if len(lst) - 4 <= 0:
                        more = None
                    if len(fmt) == 0:
                        fmt = f"`{respound.get('fmt')}`"
                    with io.BytesIO() as image_binary:
                        total = vc.current.length // 1000
                        progress = vc.position // 1000
                        w, h =  350, 10
                        r=3
                        length = (progress*w)/total
                        img = Image.new("RGBA", (w, h)) 
                        img1 = ImageDraw.Draw(img)   
                        img1.line(xy=(-1,5,350,5),fill ="white",width=2) 
                        img1.line(xy=(-1,5,length,5),fill ="red",width=2,joint='curve')
                        img1.ellipse(xy=(length-r,5-r,length+r,5+r) ,fill='darkred')
                        img.save(image_binary,'PNG')
                        image_binary.seek(0)

                        file = discord.File(image_binary, filename="image.png")
                        
                        npembed.set_image(url="attachment://image.png")
                        if send:
                            content = f'**{respound.get("queue")}:**\n{fmt}'f'\n{more}' if more else f'**{respound.get("queue")}:**\n{fmt}'
                            vc.np = await vc.interaction.followup.send(content=content, embed=npembed,view=vc.Myview ,file=file)
                            return vc.np
                        if vc.np:
                            try:
                                content = f'**{respound.get("queue")}:**\n{fmt}'f'\n{more}' if more else f'**{respound.get("queue")}:**\n{fmt}'
                                vc.np = await vc.interaction.followup.edit_message(message_id=vc.np.id,content=content, embed=npembed,view=vc.Myview ,attachments=[file])
                            except:
                                content = f'**{respound.get("queue")}:**\n{fmt}'f'\n{more}' if more else f'**{respound.get("queue")}:**\n{fmt}'
                                vc.np = await vc.interaction.followup.edit_message(message_id=vc.np.id,content=content, embed=npembed,view=vc.Myview ,attachments=[file])
                        else:
                            content = f'**{respound.get("queue")}:**\n{fmt}'f'\n{more}' if more else f'**{respound.get("queue")}:**\n{fmt}'
                            vc.np = await vc.interaction.followup.send(content=content, embed=npembed,view=vc.Myview,file=file)
                        return vc.np
                                     
    async def np(self,interaction, send=False): # thumbnail with progressbar
            vc: wavelink.Player = interaction.guild.voice_client
            respound = get_respound(interaction.locale, "np")
            if vc:
                if vc.current is not None:
                    lst = list(vc.queue)
                    if vc.queue.mode == wavelink.QueueMode.loop_all:
                        lst = lst +list(vc.queue.history)
                    upcoming = list(itertools.islice(lst,0, 4))
                    fmt = "\n".join(
                        f'` {index}.{track} `' for index,track in enumerate(upcoming,start=1)  
                    )    
                    try:
                        duration = f"{convert(vc.position)}/{convert(vc.current.length)}"
                    except:
                        duration = respound.get("unable_duration")
                    npembed = discord.Embed(
                        title=f"{vc.current.title}  <a:blobdancee:969575788389220392>",
                        url=vc.current.uri,
                        color=0xFFFFFF,
                    )
                    npembed.set_author(
                        name=f"{respound.get('addedby')} {vc.current.extras.requester}",
                        icon_url=f"{vc.current.extras.requester_icon}",
                    )
                    npembed.add_field(
                        name=f"{respound.get('playingin')}", value=f"<#{vc.channel.id}>"
                    )
                    npembed.add_field(
                        name=f"{respound.get('duration')}", value=f"`{duration}`"
                    )
                    npembed.set_footer(
                        text=f"{'Paused'if vc.paused else 'Playing'} | {vc.volume}% | LoopStatus:{trans_queueMode[f'wavelink.{str(vc.queue.mode)}']} | Autoplay:{trans_autoMode[f'wavelink.{str(vc.autoplay)}']}"
                    )
                    npembed.set_thumbnail(url=vc.current.artwork)
                    more = f"`{respound.get('andmore').format(more=len(lst)-4)}`"
                    if len(lst) - 4 <= 0:
                        more = None
                    if len(fmt) == 0:
                        fmt = f"`{respound.get('fmt')}`"
                    with io.BytesIO() as image_binary:
                        total = vc.current.length // 1000
                        progress = vc.position // 1000
                        w, h =  350, 10
                        r=3
                        length = (progress*w)/total
                        img = Image.new("RGBA", (w, h)) 
                        img1 = ImageDraw.Draw(img)   
                        img1.line(xy=(-1,5,350,5),fill ="white",width=2) 
                        img1.line(xy=(-1,5,length,5),fill ="red",width=2,joint='curve')
                        img1.ellipse(xy=(length-r,5-r,length+r,5+r) ,fill='darkred')
                        img.save(image_binary,'PNG')
                        image_binary.seek(0)

                        file = discord.File(image_binary, filename="image.png")
                        
                        npembed.set_image(url="attachment://image.png")
                        if send:
                            content = f'**{respound.get("queue")}:**\n{fmt}'f'\n{more}' if more else f'**{respound.get("queue")}:**\n{fmt}'
                            vc.np = await vc.interaction.followup.send(content=content, embed=npembed,view=vc.Myview ,file=file)
                            return vc.np
                        if vc.np:
                            try:
                                content = f'**{respound.get("queue")}:**\n{fmt}'f'\n{more}' if more else f'**{respound.get("queue")}:**\n{fmt}'
                                vc.np = await vc.interaction.followup.edit_message(message_id=vc.np.id,content=content, embed=npembed,view=vc.Myview ,attachments=[file])
                            except:
                                content = f'**{respound.get("queue")}:**\n{fmt}'f'\n{more}' if more else f'**{respound.get("queue")}:**\n{fmt}'
                                vc.np = await vc.interaction.followup.edit_message(message_id=vc.np.id,content=content, embed=npembed,view=vc.Myview ,attachments=[file])
                        else:
                            content = f'**{respound.get("queue")}:**\n{fmt}'f'\n{more}' if more else f'**{respound.get("queue")}:**\n{fmt}'
                            vc.np = await vc.interaction.followup.send(content=content, embed=npembed,view=vc.Myview,file=file)
                        return vc.np

class music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.alonetime = bot.config.get('alonetime',0)
        self.nosongtime = bot.config.get('nosongtime',0)

    async def cleanup(self, guild, frm):
        vc: wavelink.Player = guild.voice_client
        if vc == None:
            return
        vc.queue.clear()
        try:
            await vc.np.delete()
        except:
            pass
        await vc.disconnect()

    async def check_before_play(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        respound = get_respound(interaction.locale, "check_before_play")
        if vc == None:
            embed = createembed.embed_fail(interaction,respound['novc'])
            await interaction.followup.send(embed=embed)
            return False
        if interaction.user.voice == None:
            embed = createembed.embed_fail(interaction,respound['usernotin'])
            await interaction.followup.send(embed=embed)
            return False
        if interaction.guild.voice_client.channel != interaction.user.voice.channel:
            embed = createembed.embed_fail(interaction,respound['diffchan'])
            await interaction.followup.send(embed=embed)
            return False
        return True

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, exp:wavelink.TrackExceptionEventPayload):
        interaction: discord.Interaction = exp.player.interaction
        vc:wavelink.Player = interaction.guild.voice_client
        respound = get_respound(interaction.locale, "on_wavelink_track_exception")
        await asyncio.sleep(2)
        if not vc.paused:
            await vc.stop()
        try:
            await vc.np.delete()
        except:pass
        vc.np = None
        await vc.stop()
        embed = createembed.embed_fail(interaction, respound)
        d = await interaction.followup.send(embed=embed)
        await asyncio.sleep(5)
        await d.delete()

    @app_commands.command(name="nowplaying", description="Show current music")
    async def nowplaying(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if await self.check_before_play(interaction):
            vc: wavelink.Player = interaction.guild.voice_client
            vc.interaction = interaction
            try:
                vc.task.cancel() # To prevent bot from send Nowplaying message twice
            except:
                pass
            vc.task = self.bot.loop.create_task(self.current_time(vc.interaction))
            
    @app_commands.command(
        name="autoplay",
        description="when ran out of music bot will random music for you",
    )
    async def autoplay(self, interaction: discord.Interaction):
        await interaction.response.defer()      
        if await self.check_before_play(interaction):
            vc: wavelink.Player = interaction.guild.voice_client
            vc.interaction = interaction
            au = [x for x in vc.Myview.children if x.custom_id == "au"][0]
            if vc.autoplay == wavelink.AutoPlayMode.partial:
                vc.autoplay = wavelink.AutoPlayMode.enabled
                au.style = discord.ButtonStyle.green
            elif vc.autoplay == wavelink.AutoPlayMode.enabled:
                vc.autoplay = wavelink.AutoPlayMode.partial
                au.style = discord.ButtonStyle.gray
            await nowplaying.np(self, interaction)
            respound = get_respound(interaction.locale, "autoplay")
            embed = createembed.embed_success(interaction, respound)
            d = await interaction.followup.send(embed=embed)
            await asyncio.sleep(5)
            await d.delete()

    def is_url(self,url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    async def statistic(self, search):
        if len(search) > 99:
            return
        
        if self.is_url(search):
            return
        cursor = self.bot.self.bot.database.cursor()
        data = cursor.execute("SELECT * FROM search_history WHERE music = ?",(search,))
        result = data.fetchall()
        if not result:
            print('no data')
            cursor.execute("INSERT INTO search_history (music,times) VALUES (?,?)",(search,1,))
        else:
            cursor.execute("UPDATE search_history SET times = times + 1 WHERE music = ?",(search,))
        self.bot.database.commit()
        cursor.close()

    @app_commands.command(name="play", description="play music")
    @app_commands.describe(search="Music name")
    async def play(self, interaction: discord.Interaction, search: str):
        await interaction.response.defer()
        
        respound = get_respound(interaction.locale, "check_before_play")
        if not interaction.user.voice:
            embed = createembed.embed_fail(interaction,respound['usernotin'])
            await interaction.followup.send(embed=embed)
            return
        
        elif not interaction.guild.voice_client:
            vc: wavelink.Player = await interaction.user.voice.channel.connect(cls=wavelink.Player)

        elif interaction.guild.voice_client.channel != interaction.user.voice.channel:
            embed = createembed.embed_fail(interaction,respound['diffchan'])
            await interaction.followup.send(embed=embed)
            return
        
        else:
            vc: wavelink.Player = interaction.guild.voice_client

        await interaction.guild.change_voice_state(channel=interaction.user.voice.channel, self_mute=False, self_deaf=True)
        
        await self.statistic(search)
        if not vc.playing and not vc.queue:
            setattr(vc, "np", None)
            setattr(vc, "loop", "False")
            setattr(vc, "task", None)
            setattr(vc, "Myview", None)
            setattr(vc, "interaction", interaction)
            pre = pr(interaction,nowplaying.np)
            pl = pp(interaction,nowplaying.np)
            loop = lo(interaction,nowplaying.np)
            skip = sk(interaction,nowplaying.np)
            # voldown = dw(interaction)
            # volup = uw(interaction)
            # clear = cl(interaction)
            auto = au(interaction,nowplaying.np)
            disconnect = dc(interaction,nowplaying.np)
            vc.Myview = View(timeout=None)
            vc.Myview.add_item(loop)
            vc.Myview.add_item(auto)
            vc.Myview.add_item(pre)
            vc.Myview.add_item(pl)
            vc.Myview.add_item(skip)
            # vc.Myview.add_item(voldown)
            # vc.Myview.add_item(volup)
            # vc.Myview.add_item(clear)
            vc.Myview.add_item(disconnect)
            vc.autoplay = wavelink.AutoPlayMode.partial

        vc.interaction = interaction
        yt = False
        if "onlytube" in search:
            yt = True
            search = search.replace("onlytube", "")
        track = await createsource.searchen(self, search, interaction.user, onlyyt=yt)
        if track == None:
            respound = get_respound(interaction.locale, "noresult")
            embed = createembed.embed_fail(interaction, respound)
            await interaction.followup.send(embed=embed)
            return
        
        if not vc.playing and not vc.queue:
            await vc.queue.put_wait(track)
            await vc.set_volume(100)
            await vc.play(await vc.queue.get_wait(),populate=True)
        else:
            await vc.queue.put_wait(track)
            logger.info(f'adding {track}')
            await self.addtoqueue(track, interaction)
            await nowplaying.np(self, interaction)

    @play.autocomplete("search")
    async def play_autocomplete(
        self,
        interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        cursor = self.bot.database.cursor()
        
        source = cursor.execute("SELECT * FROM search_history ORDER BY times DESC LIMIT 3")

        if len(current) > 0:
            source = cursor.execute("SELECT * FROM search_history WHERE music LIKE ? COLLATE NOCASE LIMIT 25",(f"%{current}%",))
        
        result = [app_commands.Choice(name = l[1],value=l[1]) for l in source]
        cursor.close()
        return result
    
    def convert(self, seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return "%d:%02d:%02d" % (hour, minutes, seconds)

    async def addtoqueue(self, track:wavelink.Playable|wavelink.Playlist, interaction, playlist=False, number=None,playlist_title=None):
        respound = get_respound(interaction.locale, "addtoqueue")
        if isinstance(track,wavelink.Playlist):
            number = len(track.tracks)
            playlist_title = track.name
            track = track.tracks[0]
            playlist = True
            
        if not playlist:
            embed = discord.Embed(
                title=track.title,
                description=f"{respound.get('added')} ✅",
                color=0x19AD3B,
            )
            embed.set_footer(
                text=f"{respound.get('addedby').format(user=interaction.user.name)}",
                icon_url=interaction.user.avatar.url,
            )
            embed.set_thumbnail(url=track.artwork)
            d = await interaction.followup.send(embed=embed)
            await asyncio.sleep(5)
            await d.delete()
        else:
            embed = discord.Embed(
                title=respound.get("addplaylist").format(title=playlist_title,number=number),
                description=f"{respound.get('added')} ✅",
                color=0x19AD3B,
            )
            embed.set_footer(
                text=f"{respound.get('addedby').format(user=interaction.user.name)}",
                icon_url=interaction.user.avatar.url,
            )
            embed.set_thumbnail(url=track.artwork)
            d = await interaction.followup.send(embed=embed)
            await asyncio.sleep(5)
            await d.delete()

    async def current_time(self, interaction:discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        try:
            await vc.np.delete()
        except:pass
        vc.np = None
        while True:
            vc: wavelink.Player = interaction.guild.voice_client
            if interaction.is_expired():
                try:
                    vc.task.cancel()
                except:pass
            elif not interaction.is_expired() and vc.task.cancelled(): # resume update nowplaying after get new interaction
                vc.task = self.bot.loop.create_task(self.current_time(vc.interaction))
            try:
                np = await nowplaying.np(self,interaction)
            except discord.errors.NotFound as e:
                break
            if vc == None:
                break
            if vc.np == None:
                break
            await asyncio.sleep(9)
            await asyncio.sleep(1)
        vc.task.cancel()
  
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload:wavelink.payloads.TrackStartEventPayload):
        vc: wavelink.Player = payload.player
        if not vc:
            return
        if not dict(vc.current.extras).get('requester',None):
            vc.current.extras = {'requester': 'Recommended','requester_icon' : payload.player.client.user.avatar.url}
        logger.info(f"Now playing : {vc.current}")
        await asyncio.sleep(0.3)
        vc.task = self.bot.loop.create_task(self.current_time(vc.interaction))

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload:wavelink.payloads.TrackEndEventPayload):
        logger.info(f"ending: {payload.track}")
        vc: wavelink.Player = payload.player
        if not vc:
            return
        vc.task.cancel()
        try:
            await vc.np.delete()
        except:
            pass
        vc.np = None
        if payload.player == None:
            return
        interaction = payload.player.interaction
        respound = get_respound(interaction.locale, "on_wavelink_track_end")
        if not vc.queue and vc:
            try:
                async with timeout(self.nosongtime):
                    await self.nosong(interaction)
            except:
                await self.cleanup(interaction.guild, "trackend")
                embed = createembed.embed_info(vc.interaction, respound)
                try:
                    d = await interaction.followup.send(embed=embed)
                    await asyncio.sleep(5)
                    await d.delete()
                except:
                    pass
                return
            
    async def nosong(self, interaction:discord.Interaction):
        i=0
        while True:
            vc: wavelink.Player = interaction.guild.voice_client
            if vc.queue or vc.current:
                break
            i+=1
            logger.info(f'counting no song {interaction.guild.name} | {i}')
            await asyncio.sleep(0.4)

    @app_commands.command(name="loop", description="Set music loop status")
    @app_commands.describe(status="loop status")
    @app_commands.choices(
        status=[
            Choice(name="False (ปิด)", value='wavelink.QueueMode.normal'),
            Choice(name="Song (เพลง)", value="wavelink.QueueMode.loop"),
            Choice(name="Queue (ทั้งคิว)", value="wavelink.QueueMode.loop_all"),
        ]
    )
    async def loop(self, interaction: discord.Interaction, status: str):
        await interaction.response.defer()
        if await self.check_before_play(interaction):
            vc: wavelink.Player = interaction.guild.voice_client
            vc.interaction = interaction
            vc.queue.mode = eval(status)
            lo = [x for x in vc.Myview.children if x.custom_id == "lo"][0]
            if vc.queue.mode == wavelink.QueueMode.normal:
                lo.style = discord.ButtonStyle.gray
            elif vc.queue.mode == wavelink.QueueMode.loop:
                lo.style = discord.ButtonStyle.blurple
            elif vc.queue.mode == wavelink.QueueMode.loop_all:
                lo.style = discord.ButtonStyle.green
            await nowplaying.np(self, interaction)
            respound = get_respound(interaction.locale, "loop")
            embed = createembed.embed_success(interaction, respound,trans_queueMode[status])
            d = await interaction.followup.send(embed=embed)
            await asyncio.sleep(5)
            await d.delete()

    @app_commands.command(name="resume", description="Resume music")
    async def resume(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if await self.check_before_play(interaction):
            vc: wavelink.Player = interaction.guild.voice_client
            vc.interaction = interaction
            re = [x for x in vc.Myview.children if x.custom_id == "pp"][0]
            re.style = discord.ButtonStyle.green
            re.emoji = "<a:1_:989120454063185940>"
            await vc.pause(False)
            respound = get_respound(interaction.locale, "resume")
            embed = createembed.embed_success(interaction, respound)
            d = await interaction.followup.send(embed=embed)
            await asyncio.sleep(5)
            await d.delete()

    @app_commands.command(name="pause", description="Pause music")
    async def pause(self, interaction: discord.Interaction):
        await interaction.response.defer()
        respound = get_respound(interaction.locale, "pause")
        if await self.check_before_play(interaction):
            vc: wavelink.Player = interaction.guild.voice_client
            vc.interaction = interaction
            re = [x for x in vc.Myview.children if x.custom_id == "pp"][0]
            re.style = discord.ButtonStyle.red
            re.emoji = "<a:2_:989120456240025670>"
            await vc.pause(True)
            await nowplaying.np(self, interaction)
            respound = get_respound(interaction.locale, "pause")
            embed = createembed.embed_success(interaction, respound)
            d = await interaction.followup.send(embed=embed)
            await asyncio.sleep(5)
            await d.delete()

    @app_commands.command(name="skip", description="Skip music")
    @app_commands.describe(to="Skip to given music")
    async def skip(self, interaction: discord.Interaction, to: Optional[int] = False):
        await interaction.response.defer()
        if await self.check_before_play(interaction):
            vc: wavelink.Player = interaction.guild.voice_client
            vc.interaction = interaction
            if to:
                respound = get_respound(interaction.locale, "skipto")
                if to > len(vc.queue):
                    embed = createembed.embed_fail(interaction, respound)
                    await interaction.followup.send(embed=embed)
                    return
                wanted = vc.queue[to-1]
                vc.queue.delete(to-1)
                vc.queue.put_at(0,wanted)
                await vc.skip()
                embed = createembed.embed_success(interaction, respound,to)
                d = await interaction.followup.send(embed=embed)
                await asyncio.sleep(5)
                await d.delete()
            else:
                await vc.skip()
                respound = get_respound(interaction.locale, "skip")
                embed = createembed.embed_success(interaction, respound)
                d = await interaction.followup.send(embed=embed)
                await asyncio.sleep(5)
                await d.delete()

    @app_commands.command(name="shuffle", description="Shuffle music queue")
    async def shuffle(self, interaction: discord.Interaction):
        await interaction.response.defer()
        vc: wavelink.Player = interaction.guild.voice_client
        if await self.check_before_play(interaction):
            vc: wavelink.Player = interaction.guild.voice_client
            vc.interaction = interaction
            vc.queue.shuffle()
            respound = get_respound(interaction.locale, "shuffle")
            embed = createembed.embed_success(interaction, respound)
            d = await interaction.followup.send(embed=embed)
            await asyncio.sleep(5)
            await d.delete()

    @app_commands.command(name="disconnect", description="Leave voice chat")
    async def dc(self, interaction: discord.Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        vc.interaction = interaction
        await interaction.response.defer()
        if await self.check_before_play(interaction):
            vc: wavelink.Player = interaction.guild.voice_client
            vc.interaction = interaction
            await self.cleanup(interaction.guild, "dc")
            respound = get_respound(interaction.locale, "dc")
            embed = createembed.embed_success(interaction, respound)
            d = await interaction.followup.send(embed=embed)
            await asyncio.sleep(5)
            await d.delete()

    @app_commands.command(name="remove", description="Remove given music from queue")
    @app_commands.describe(index="Music Sequence")
    async def remove(self, interaction: discord.Interaction, index: int):
        await interaction.response.defer()
        if await self.check_before_play(interaction):
            vc: wavelink.Player = interaction.guild.voice_client
            vc.interaction = interaction
            delete = None 
            if vc.queue.mode == wavelink.QueueMode.loop_all:
                if index > (vc.queue.count+vc.queue.history.count):#Index out of range handler
                    respound = get_respound(interaction.locale, "remove")
                    erembed = createembed.embed_fail(interaction, respound)
                    await interaction.followup.send(embed=erembed)
                    return
                if index > vc.queue.count: 
                    delete = vc.queue.history.peek(index-len(vc.queue)-1)
                    vc.queue.history.delete(index-len(vc.queue)-1)
                else:
                    delete = vc.queue.peek(index-1)
                    vc.queue.delete(index-1)
            else:
                if index > vc.queue.count: #Index out of range handler
                    respound = get_respound(interaction.locale, "remove")
                    erembed = createembed.embed_fail(interaction, respound)
                    await interaction.followup.send(embed=erembed)
                    return
                delete = vc.queue.peek(index-1)
                vc.queue.delete(index-1)
            respound = get_respound(interaction.locale, "remove")
            embed = createembed.embed_success(interaction, respound,delete)
            d = await interaction.followup.send(embed=embed)
            await asyncio.sleep(5)
            await d.delete()
            await nowplaying.np(self, interaction)

    @app_commands.command(name="queue", description="Send queuelist")
    async def queueList(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if await self.check_before_play(interaction):
            pag = []
            respound = get_respound(interaction.locale, "queueList")
            vc: wavelink.Player = interaction.guild.voice_client
            vc.interaction = interaction
            upcoming = vc.queue
            if vc.queue.mode == wavelink.QueueMode.loop_all:
                upcoming = list(upcoming)+list(vc.queue.history)
            number = len(upcoming)
            page = math.ceil(number / 10)
            if page == 0:
                page = 1
            lst = []

            for index,track in enumerate(upcoming,1):
                op = f'{index}.{track}'
                lst.append(op)

            for i in range(page):
                items = list(itertools.islice(lst, 0, 10))
                if i != 0:
                    fmt = "\n".join(f"**` {_}`**" for _ in items)
                    embed = discord.Embed(color=0xFFFFFF)
                else:
                    fmt = "\n".join(f"**` {_}`**" for _ in items)
                    plus = 1
                    if len(fmt) == 0:
                        plus = 0
                    embed = discord.Embed(
                        title=respound.get("more").format(more=number - plus),
                        color=0xFFFFFF,
                    )
                    if vc.current == None:
                        embed.add_field(
                            name=respound.get("playing"),
                            value=respound.get("noplay"),
                            inline=False,
                        )
                    else:
                        embed.add_field(
                            name=respound.get("playing"),
                            value=f"**`{vc.current.title}`**",
                            inline=False,
                        )
                if number <= 1:
                    embed.add_field(
                        name=respound.get("inqueue"),
                        value=respound.get("nomorequeue"),
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name=respound.get("inqueue"), value=f"{fmt}", inline=False
                    )
                pag.append(embed)
                for i in range(10):
                    try:
                        del lst[0]
                    except:
                        pass
            embed.set_footer(text=respound.get("notupdate"))
            view = buttin(pag, 120, interaction)
            view.interaction = interaction
            await interaction.followup.send(embed=pag[0], view=view)

    async def checkdc(self, member:discord.Member):
        vc: wavelink.Player = member.guild.voice_client
        i=0
        while True:
            i += 1
            logger.info(f'counting alonetime {member.guild.name} | {i}')
            if len(vc.channel.members) > 1:
                break
            await asyncio.sleep(0.5)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before, after):
        vc: wavelink.Player = member.guild.voice_client
        if member == self.bot.user:
            return
        if not vc:
            return
        if before.channel != after.channel:
            if after.channel == vc.channel:
                return
            if after.channel != vc.channel:
                if len(vc.channel.members) <= 1:
                    lastone = member
                    try:
                        async with timeout(self.alonetime):
                            await self.checkdc(member)
                            pass
                    except asyncio.TimeoutError:
                        await self.cleanup(member.guild, "voiceupdate no one")
                        respound = get_respound(lastone.guild.preferred_locale, "ononeleft")
                        embed = createembed.embed_info(lastone, respound)
                        try:
                            d = await vc.interaction.followup.send(embed=embed)
                            await asyncio.sleep(5)
                            await d.delete()
                        except:
                            pass
                        return
                    return


async def setup(bot):
    await bot.add_cog(music(bot))
