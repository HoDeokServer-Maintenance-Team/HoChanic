import discord
import asyncio
import nest_asyncio
import datetime
from discord.ext import commands
from modules import bot_db

nest_asyncio.apply()

bot = commands.Bot(command_prefix="!")
loop = asyncio.get_event_loop()
hochanic_db = bot_db.HoChanicDB("database.db")


async def reset_daily_db():
    await bot.wait_for("ready")
    while True:
        guild = bot.get_guild(518791611048525852)
        upvote_channel = guild.get_channel(int((await hochanic_db.get_from_table("bot_settings", "key", "upvote_channel"))[0][1]))
        current_time = datetime.datetime.now()
        if current_time.hour == 0 and current_time.minute == 0:
            res = await hochanic_db.res_sql("SELECT * FROM daily ORDER BY count DESC")
            current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
            embed = discord.Embed(title="업보트 랭크", color=discord.Colour.from_rgb(225, 225, 225))
            embed.set_footer(text=current_time)
            lvl = 1
            count = 0
            for y in res:
                if y[1] == 0:
                    continue
                try:
                    msg = await (guild.get_channel(int(y[2]))).fetch_message(int(y[0]))
                    if msg is None:
                        continue
                except discord.NotFound:
                    continue
                if count == 5:
                    embed.add_field(name="...", value=f"+{len(res) - count}", inline=False)
                    break
                embed.add_field(name=str(lvl) + f": {msg.author}",
                                value=f"[바로가기]({msg.jump_url})\n업보트 수: {y[1]}",
                                inline=False)
                count += 1
                lvl += 1
            if count is 0:
                embed.add_field(name="없음", value="업보트 없음")
            await upvote_channel.send(embed=embed)
            await hochanic_db.run_sql(f'DROP TABLE IF EXISTS daily')
            await hochanic_db.run_sql("""CREATE TABLE "daily" (
                    "id"    INTEGER NOT NULL,
                    "count"    INTEGER NOT NULL DEFAULT 0,
                    "text_channel"    INTEGER NOT NULL,
                    PRIMARY KEY("id")
                )""")
        await asyncio.sleep(60)


async def get_hall_of_fame(msg: discord.Message):
    posted = await hochanic_db.get_table("posted")
    posted = [x[0] for x in posted]
    if msg.id in posted:
        return
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    guild = bot.get_guild(518791611048525852)
    hall_of_fame_channel = guild.get_channel(724423310573699072)
    img_url = [a.url for a in msg.attachments]
    embed = discord.Embed(title="5+ 업보트", description=f"[바로가기]({msg.jump_url})")
    embed.set_author(name=msg.author.display_name + f" ({msg.author})", icon_url=msg.author.avatar_url)
    embed.set_footer(text=current_time)
    if len(img_url) != 0:
        embed.set_image(url=img_url[0])
    if bool(msg.content) is not False:
        embed.add_field(name="메시지 내용", value=msg.content)
    await hall_of_fame_channel.send(embed=embed)
    await hochanic_db.insert_table("posted", is_int=True, msg_id=str(msg.id))


@bot.event
async def on_ready():
    print("Bot Ready.")
    await bot.change_presence(activity=discord.Game((await hochanic_db.get_from_table("bot_settings", "key", "presence"))[0][1]))


@bot.command(name="확인")
async def _check_ko(ctx):
    tgt_role = ctx.guild.get_role(723438324777353226)
    if tgt_role in ctx.author.roles:
        return await ctx.send(f"{ctx.author.mention} ❌ 이미 역할을 받으셨습니다.", delete_after=5)
    await ctx.author.add_roles(tgt_role)
    await ctx.send(f"{ctx.author.mention} ✅ 호덕 디스코드 서버에 오신 것을 환영합니다!", delete_after=5)


@bot.command(name="confirm", aliases=["check"])
async def _check_en(ctx):
    tgt_role = ctx.guild.get_role(721002110883201184)
    if tgt_role in ctx.author.roles:
        return await ctx.send(f"{ctx.author.mention} ❌ You already got the role.", delete_after=5)
    await ctx.author.add_roles(tgt_role)
    await ctx.send(f"{ctx.author.mention} ✅ Welcome to HoDeok Discord Server!", delete_after=5)


@bot.command(name="스샷채널추가")
async def _add_new_screenshot_channel(ctx, channel: discord.TextChannel):
    channel_list = ((await hochanic_db.get_from_table("bot_settings", "key", "screenshot_channel"))[0][1]).split(", ")
    if channel.id in channel_list:
        return await ctx.send("이미 등록된 채널입니다.")
    channel_list.append(channel.id)
    channel_list = ", ".join([str(x) for x in channel_list])
    await hochanic_db.update_db("bot_settings", "value", channel_list, "key", "screenshot_channel")
    await ctx.send(f"{channel.mention} 추가 완료")


@bot.command(name="업보트", aliases=["upvote", "rank", "랭크"])
async def _rank(ctx):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    res = await hochanic_db.res_sql("SELECT * FROM daily ORDER BY count DESC")
    embed = discord.Embed(title="업보트 랭크", color=discord.Colour.from_rgb(225, 225, 225))
    embed.set_footer(text=current_time)
    lvl = 1
    count = 0
    for y in res:
        if y[1] == 0:
            continue
        try:
            msg = await (ctx.guild.get_channel(int(y[2]))).fetch_message(int(y[0]))
            if msg is None:
                continue
        except discord.NotFound:
            continue
        if count == 5:
            embed.add_field(name="...", value=f"+{len(res) - count}", inline=False)
            break
        embed.add_field(name=str(lvl) + f": {msg.author}",
                        value=f"[바로가기]({msg.jump_url})\n업보트 수: {y[1]}",
                        inline=False)
        count += 1
        lvl += 1
    if count is 0:
        embed.add_field(name="없음", value="업보트 없음")
    await ctx.send(embed=embed)


@bot.command(name="수동명정")
async def _manual_hof(ctx, msg: discord.Message):
    await get_hall_of_fame(msg)


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    to_prohibit = bot.get_channel(721001176413241424)
    protected = [278170182227066880, 330286426044235776, 292275669008646154, 288302173912170497]
    if message.channel == to_prohibit and message.author.id not in protected:
        await message.delete()
    channel_id = message.channel.id
    channel_list = ((await hochanic_db.get_from_table("bot_settings", "key", "screenshot_channel"))[0][1]).split(", ")
    channel_list = [int(x) for x in channel_list]
    if channel_id not in channel_list:
        return await bot.process_commands(message)
    if message.attachments == [] or message.attachments is None or str(message.attachments) == "[]" or len(
            message.attachments) == 0:
        return await bot.process_commands(message)
    emoji = bot.get_emoji(733227223670063176)
    #emoji2 = bot.get_emoji(733227206133678160)
    await message.add_reaction(emoji)
    #await message.add_reaction(emoji2)
    await hochanic_db.insert_table("daily", is_int=True, id=str(message.id), text_channel=str(message.channel.id))
    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
    channel_list = ((await hochanic_db.get_from_table("bot_settings", "key", "screenshot_channel"))[0][1]).split(", ")
    channel_list = [int(x) for x in channel_list]
    channel_id = payload.channel_id
    message_id = payload.message_id
    emoji = payload.emoji
    guild = bot.get_guild(518791611048525852)
    msg = await (guild.get_channel(channel_id)).fetch_message(message_id)
    if emoji.id != 733227223670063176 or channel_id not in channel_list or payload.user_id == 641260499924811797:
        return
    try:
        curr_count = int((await hochanic_db.get_from_table("daily", "id", message_id, is_int=True))[0][1])
    except IndexError:
        await hochanic_db.insert_table("daily", is_int=True, id=str(message_id), text_channel=str(channel_id))
        curr_count = int((await hochanic_db.get_from_table("daily", "id", message_id, is_int=True))[0][1])
    await hochanic_db.update_db("daily", "count", str(curr_count + 1), "id", str(message_id), is_int=True)
    if curr_count + 1 >= 3:
        await get_hall_of_fame(msg)


@bot.event
async def on_raw_reaction_remove(payload):
    channel_list = ((await hochanic_db.get_from_table("bot_settings", "key", "screenshot_channel"))[0][1]).split(", ")
    channel_list = [int(x) for x in channel_list]
    channel_id = payload.channel_id
    message_id = payload.message_id
    emoji = payload.emoji
    if emoji.id != 733227223670063176 or channel_id not in channel_list or payload.user_id == 641260499924811797:
        return
    try:
        curr_count = int((await hochanic_db.get_from_table("daily", "id", message_id, is_int=True))[0][1])
    except IndexError:
        return
    await hochanic_db.update_db("daily", "count", str(curr_count - 1), "id", str(message_id), is_int=True)


@bot.event
async def on_member_join(member):
    tgt_roles = [member.guild.get_role(723438324777353226), member.guild.get_role(737999344950575204)]
    await member.add_roles(*tgt_roles)


loop.create_task(reset_daily_db())
bot.run(loop.run_until_complete(hochanic_db.get_from_table("bot_settings", "key", "token"))[0][1])
