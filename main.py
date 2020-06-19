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


@bot.command(name="확인")
async def _check_ko(ctx):
    tgt_role = ctx.guild.get_role(723438324777353226)
    if tgt_role in ctx.author.roles:
        return await ctx.send("❌ 이미 역할을 받으셨습니다.")
    await ctx.send("✅ 호덕 디스코드 서버에 오신 것을 환영합니다!")
    await ctx.author.add_roles(tgt_role)


@bot.command(name="confirm", aliases=["check"])
async def _check_en(ctx):
    tgt_role = ctx.guild.get_role(721002110883201184)
    if tgt_role in ctx.author.roles:
        return await ctx.send("❌ You already got the role.")
    await ctx.send("✅ Welcome to HoDeok Discord Server!")
    await ctx.author.add_roles(tgt_role)


bot.run(loop.run_until_complete(hochanic_db.get_from_table("bot_settings", "key", "token"))[0][1])
