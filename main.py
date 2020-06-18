import discord
import asyncio
import nest_asyncio
from discord.ext import commands
from modules import bot_db
nest_asyncio.apply()

bot = commands.Bot(command_prefix="!")
loop = asyncio.get_event_loop()
hochanic_db = bot_db.HoChanicDB("database.db")


@bot.event
async def on_ready():
    print("Bot Ready.")


bot.run(loop.run_until_complete(hochanic_db.get_from_table("bot_settings", "key", "token"))[0][1])
