from discord.ui import Button, View
import discord
import wavelink
from ui.language_respound import get_respound
from ui.embed_gen import createembed

async def check_before_play(interaction: discord.Interaction):
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

class pp(Button):
    def __init__(self, interaction,np):
        super().__init__(
            emoji="<a:1_:989120454063185940>",
            style=discord.ButtonStyle.green,
            custom_id="pp",
        )
        self.interaction = interaction
        self.np = np

    async def callback(self, interaction):
        await interaction.response.defer()
        vc: wavelink.Player = interaction.guild.voice_client
        vc.interaction = interaction
        if not await check_before_play(interaction):
            return
        if not vc.paused:
            await vc.pause(True)
        elif vc.paused:
            await vc.pause(False)
        pp = [x for x in vc.Myview.children if x.custom_id == "pp"][0]
        if vc.paused:
            pp.emoji = "<a:2_:989120456240025670>"
            pp.style = discord.ButtonStyle.red
        elif not vc.paused:
            pp.emoji = "<a:1_:989120454063185940>"
            pp.style = discord.ButtonStyle.green
        else:
            pp.emoji = "<a:1_:989120454063185940>"
            pp.style = discord.ButtonStyle.green
        await self.np(self, self.interaction)
        try:
            await interaction.followup.send(content="")
        except:
            pass

class pr(Button):
    def __init__(self, interaction,np):
        super().__init__(
            emoji="<a:10:989120441325068308>", style=discord.ButtonStyle.blurple
        )
        self.interaction = interaction
        self.np = np

    async def callback(self, interaction):
        await interaction.response.defer()
        vc: wavelink.Player = interaction.guild.voice_client
        vc.interaction = interaction
        if not await check_before_play(interaction):
            return
        respound = get_respound(interaction.locale, "previous")
        if len(vc.queue.history) < 2:
            await interaction.followup.send(content=respound.get('noprevious'),ephemeral=True)
            return
        pre_queuemode =  vc.queue.mode
        vc.queue.mode = wavelink.QueueMode.normal

        
        vc.queue.put_at(0,vc.queue.history[-1]) #insert current song
        vc.queue.history.delete(len(vc.queue.history)-1)#delete the current song
        vc.queue.put_at(0,vc.queue.history[-1]) #insert previous song       
        vc.queue.history.delete(len(vc.queue.history)-1) #delete the previous song
        await vc.skip() #play previous song

        vc.queue.mode = pre_queuemode
        try:
            await interaction.followup.send(content="")
        except:
            pass


class sk(Button):
    def __init__(self, interaction,np):
        super().__init__(
            emoji="<a:10:989120439655739432>", style=discord.ButtonStyle.blurple
        )
        self.interaction = interaction
        self.np = np

    async def callback(self, interaction):
        await interaction.response.defer()
        vc: wavelink.Player = interaction.guild.voice_client
        vc.interaction = interaction
        if not await check_before_play(interaction):
            return
        await vc.skip()
        try:
            await interaction.followup.send(content="")
        except:
            pass


class lo(Button):
    def __init__(self, interaction,np):
        super().__init__(
            emoji="<a:4_:989120448312803348>",
            style=discord.ButtonStyle.gray,
            custom_id="lo",
        )
        self.interaction = interaction
        self.np = np

    async def callback(self, interaction):
        await interaction.response.defer()
        vc: wavelink.Player = interaction.guild.voice_client
        vc.interaction = interaction
        lo = [x for x in vc.Myview.children if x.custom_id == "lo"][0]
        if not await check_before_play(self.interaction):
            return
        if vc.queue.mode == wavelink.QueueMode.normal:
            vc.queue.mode = wavelink.QueueMode.loop
            lo.style = discord.ButtonStyle.blurple
        elif vc.queue.mode == wavelink.QueueMode.loop:
            vc.queue.mode = wavelink.QueueMode.loop_all
            lo.style = discord.ButtonStyle.green
        elif vc.queue.mode == wavelink.QueueMode.loop_all:
            vc.queue.mode = wavelink.QueueMode.normal
            lo.style = discord.ButtonStyle.gray
        await self.np(self, self.interaction)
        try:
            await interaction.followup.send(content="")
        except:
            pass


class dw(Button):
    def __init__(self, interaction,np):
        super().__init__(
            emoji="<a:6_:989120452075094026>", style=discord.ButtonStyle.blurple
        )
        self.interaction = interaction
        self.np = np

    async def callback(self, interaction):
        await interaction.response.defer()
        vc: wavelink.Player = interaction.guild.voice_client
        vc.interaction = interaction
        if not await check_before_play(interaction):
            return
        if vc.volume - 15 < 0:
            volume = 0
        else:
            volume = vc.volume - 15
        await vc.set_volume(volume)
        await self.np(self, self.interaction)
        try:
            await interaction.followup.send(content="")
        except:
            pass


class uw(Button):
    def __init__(self, interaction,np):
        super().__init__(
            emoji="<a:5_:989120450254737418>", style=discord.ButtonStyle.blurple
        )
        self.interaction = interaction
        self.np = np

    async def callback(self, interaction):
        await interaction.response.defer()
        vc: wavelink.Player = interaction.guild.voice_client
        vc.interaction = interaction
        if not await check_before_play(interaction):
            return
        if vc.volume + 15 > 100:
            volume = 100
        else:
            volume = vc.volume + 15
        await vc.set_volume(volume)
        await self.np(self, self.interaction)
        try:
            await interaction.followup.send(content="")
        except:
            pass


class cl(Button):
    def __init__(self, interaction,np):
        super().__init__(
            emoji="<a:8_:989120444701491210>", style=discord.ButtonStyle.red
        )
        self.interaction = interaction
        self.np = np

    async def callback(self, interaction):
        await interaction.response.defer()
        vc: wavelink.Player = interaction.guild.voice_client
        vc.interaction = interaction
        if not await check_before_play(interaction):
            return
        vc.queue.clear()
        await vc.skip()
        try:
            await interaction.followup.send(content="")
        except:
            pass


class dc(Button):
    def __init__(self, interaction,np):
        super().__init__(
            emoji="<a:7_:989120442851811359>", style=discord.ButtonStyle.red
        )
        self.interaction = interaction  
        self.np = np

    async def callback(self, interaction):
        await interaction.response.defer()
        vc: wavelink.Player = interaction.guild.voice_client
        vc.interaction = interaction
        if not await check_before_play(interaction):
            return
        if vc == None:
            return
        vc.queue.clear()
        c = vc.np
        vc.np = None
        try:
            await c.delete()
        except:
            pass
        await vc.disconnect()
        try:
            await interaction.followup.send(content="")
        except:
            pass