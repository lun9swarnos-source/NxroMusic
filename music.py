
import discord, wavelink, asyncio
from discord.ext import commands
from discord import app_commands

queues = {}

class PlayerView(discord.ui.View):
    def __init__(self, player):
        super().__init__(timeout=None)
        self.player = player

    @discord.ui.button(label="⏯️", style=discord.ButtonStyle.green)
    async def pause(self, interaction, button):
        if self.player.is_playing():
            await self.player.pause()
        else:
            await self.player.resume()
        await interaction.response.defer()

    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.blurple)
    async def skip(self, interaction, button):
        await self.player.stop()
        await interaction.response.defer()

    @discord.ui.button(label="⏹️", style=discord.ButtonStyle.red)
    async def stop(self, interaction, button):
        await self.player.disconnect()
        await interaction.response.defer()

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_queue(self, guild):
        return queues.setdefault(guild.id, [])

    async def play_next(self, player, guild):
        q = self.get_queue(guild)
        if not q:
            return
        track = q.pop(0)
        await player.play(track)

    @app_commands.command(name="play")
    async def play(self, interaction: discord.Interaction, query: str):
        if not interaction.user.voice:
            return await interaction.response.send_message("Join a VC first.", ephemeral=True)

        vc: wavelink.Player = interaction.guild.voice_client
        if not vc:
            vc = await interaction.user.voice.channel.connect(cls=wavelink.Player)

        track = await wavelink.YouTubeTrack.search(query=query, return_first=True)
        queue = self.get_queue(interaction.guild)

        if vc.is_playing():
            queue.append(track)
            await interaction.response.send_message(f"Queued **{track.title}**")
        else:
            await vc.play(track)
            embed = discord.Embed(title="Now Playing", description=track.title, color=0x1DB954)
            embed.set_thumbnail(url=track.thumbnail)
            await interaction.response.send_message(embed=embed, view=PlayerView(vc))

    @app_commands.command(name="queue")
    async def queue_cmd(self, interaction: discord.Interaction):
        q = self.get_queue(interaction.guild)
        if not q:
            return await interaction.response.send_message("Queue empty.")
        desc = "\n".join(f"{i+1}. {t.title}" for i,t in enumerate(q[:10]))
        embed = discord.Embed(title="Queue", description=desc, color=0x1DB954)
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload):
        player = payload.player
        await self.play_next(player, player.guild)

async def setup(bot):
    await bot.add_cog(Music(bot))
