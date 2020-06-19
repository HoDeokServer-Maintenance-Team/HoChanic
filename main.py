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
    await hochanic_db.create_table("daily", "INTEGER", id=False, count="0")


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


@bot.command(name="스샷채널추가")
async def _add_new_screenshot_channel(ctx, channel: discord.TextChannel):
    channel_list = ((await hochanic_db.get_from_table("bot_settings", "key", "screenshot_channel"))[0][1]).split(", ")
    if channel.id in channel_list:
        return await ctx.send("이미 등록된 채널입니다.")
    channel_list.append(channel.id)
    channel_list = ", ".join([str(x) for x in channel_list])
    await hochanic_db.update_db("bot_settings", "value", channel_list, "key", "screenshot_channel")
    await ctx.send(f"{channel.mention} 추가 완료")


@bot.event
async def on_message(message):
    channel_id = message.channel.id
    channel_list = ((await hochanic_db.get_from_table("bot_settings", "key", "screenshot_channel"))[0][1]).split(", ")
    channel_list = [int(x) for x in channel_list]
    if channel_id not in channel_list:
        return await bot.process_commands(message)
    if message.attachments == [] or message.attachments is None or str(message.attachments) == "[]" or len(message.attachments) == 0:
        return await bot.process_commands(message)
    await message.add_reaction("🔼")
    await hochanic_db.insert_table("daily", is_int=True, id=str(message.id))
    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
    channel_list = ((await hochanic_db.get_from_table("bot_settings", "key", "screenshot_channel"))[0][1]).split(", ")
    channel_list = [int(x) for x in channel_list]
    channel_id = payload.channel_id
    message_id = payload.message_id
    emoji = payload.emoji
    if not str(emoji) == "🔼" or channel_id not in channel_list or payload.user_id == 641260499924811797:
        return
    try:
        curr_count = int((await hochanic_db.get_from_table("daily", "id", message_id, is_int=True))[0][1])
    except IndexError:
        return
    await hochanic_db.update_db("daily", "count", str(curr_count + 1), "id", str(message_id), is_int=True)


@bot.event
async def on_raw_reaction_remove(payload):
    channel_list = ((await hochanic_db.get_from_table("bot_settings", "key", "screenshot_channel"))[0][1]).split(", ")
    channel_list = [int(x) for x in channel_list]
    channel_id = payload.channel_id
    message_id = payload.message_id
    emoji = payload.emoji
    if not str(emoji) == "🔼" or channel_id not in channel_list or payload.user_id == 641260499924811797:
        return
    try:
        curr_count = int((await hochanic_db.get_from_table("daily", "id", message_id, is_int=True))[0][1])
    except IndexError:
        return
    await hochanic_db.update_db("daily", "count", str(curr_count - 1), "id", str(message_id), is_int=True)


bot.run(loop.run_until_complete(hochanic_db.get_from_table("bot_settings", "key", "token"))[0][1])
