import discord
import asyncio
import aiosqlite
import nest_asyncio
from discord.ext import commands
from modules import modules
nest_asyncio.apply()

bot = commands.Bot(command_prefix="!")
loop = asyncio.get_event_loop()
sql = loop.run_until_complete(aiosqlite.connect('database.db'))


# 레거시 코드 수정 필요
def is_authorized(ctx):
    return bot.get_guild(518791611048525852).get_role(
        721776076430377142) in ctx.author.roles or ctx.author.id == 278170182227066880


@bot.event
async def on_ready():
    print("running")
    await bot.change_presence(activity=discord.Game(modules.get_bot_setting("presence")))
    await modules.refresh_sql_table(sql)


@bot.command(name="사진리셋")
@commands.check(is_authorized)
async def _reset_photo_db(ctx):
    msg = await ctx.send("정말로 사진 DB를 리셋할까요?")
    res = await modules.confirm(bot, ctx, msg)
    if res is not True:
        return await msg.edit(content="사진 DB 리셋을 취소했습니다.")
    await modules.refresh_sql_table(sql)
    await msg.edit(content="사진 DB 리셋 완료")


@bot.command(name="DB확인")
@commands.check(is_authorized)
async def _check_db(ctx, num=5):
    res = await modules.top_sql_table(sql, num)
    await ctx.send(res)


@bot.command(name="스샷채널추가")
@commands.check(is_authorized)
async def _add_new_screenshot_channel(ctx, channel: discord.TextChannel):
    channel_list = modules.get_bot_setting("screenshot_channel")
    if channel.id in channel_list:
        return await ctx.send("이미 등록된 채널입니다.")
    channel_list.append(channel.id)
    modules.update_bot_setting("screenshot_channel", channel_list)
    await ctx.send(f"{channel.mention} 추가 완료")


@bot.event
async def on_message(message):
    channel_id = message.channel.id
    channel_list = modules.get_bot_setting("screenshot_channel")
    if channel_id not in channel_list:
        return await bot.process_commands(message)
    if message.attachments == [] or message.attachments is None or str(message.attachments) == "[]" or len(
            message.attachments) == 0:
        return await bot.process_commands(message)
    await message.add_reaction("🔼")
    await modules.add_sql_table(sql, message.id)
    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
    channel_list = modules.get_bot_setting("screenshot_channel")
    channel_id = payload.channel_id
    message_id = payload.message_id
    emoji = payload.emoji
    if not str(emoji) == "🔼" or channel_id not in channel_list:
        return
    await modules.delta_sql_table(sql, 1, message_id)


@bot.event
async def on_raw_reaction_remove(payload):
    channel_list = modules.get_bot_setting("screenshot_channel")
    channel_id = payload.channel_id
    message_id = payload.message_id
    emoji = payload.emoji
    if not str(emoji) == "🔼" or channel_id not in channel_list:
        return
    await modules.delta_sql_table(sql, -1, message_id)

bot.run(modules.get_bot_setting("token"))
