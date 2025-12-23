
import discord, os, asyncio, wavelink
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await wavelink.NodePool.create_node(
        bot=bot,
        host=os.getenv("LAVALINK_HOST"),
        port=int(os.getenv("LAVALINK_PORT")),
        password=os.getenv("LAVALINK_PASSWORD")
    )
    await bot.tree.sync()
    print("NxroMusic ONLINE")

async def main():
    async with bot:
        await bot.load_extension("music")
        await bot.start(os.getenv("DISCORD_TOKEN"))

asyncio.run(main())
