import json
import asyncio
import discord
from discord.ext import commands

cafe_id = "29376261"
base_cafe_url = "https://cafe.naver.com/kerbalforum/"


async def refresh_sql_table(sql):
    await sql.execute('DROP TABLE IF EXISTS daily')
    await sql.execute('CREATE TABLE daily(id INTEGER NOT NULL PRIMARY KEY, count INTEGER)')
    await sql.commit()


async def delta_sql_table(sql, delta, ident):
    await sql.execute('UPDATE daily SET count = count + ? WHERE id = ?', (delta, ident))
    await sql.commit()


async def add_sql_table(sql, ident):
    await sql.execute('INSERT INTO daily VALUES(?, 0)', (ident,))
    await sql.commit()


async def top_sql_table(sql, num):
    return await (await sql.execute('SELECT * FROM daily ORDER BY count DESC LIMIT ?', (num,))).fetchall()


def get_bot_setting(key):
    with open("bot_settings.json", "r", encoding="UTF-8") as f:
        settings = json.load(f)
    try:
        return settings[key]
    except KeyError:
        update_bot_setting(key, None)
        return None


def update_bot_setting(key, val):
    with open("bot_settings.json", "r", encoding="UTF-8") as f:
        settings = json.load(f)
    settings[key] = val
    with open("bot_settings.json", "w", encoding="UTF-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)


async def confirm(bot: commands.Bot, ctx: commands.Context, msg: discord.Message, time: int = 30):
    emoji_list = ["⭕", "❌"]
    await msg.add_reaction("⭕")
    await msg.add_reaction("❌")

    def check(reaction, user):
        return str(reaction.emoji) in emoji_list and user == ctx.author

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=time, check=check)
        if str(reaction.emoji) == emoji_list[0]:
            return True
        elif str(reaction.emoji) == emoji_list[1]:
            return False
    except asyncio.TimeoutError:
        return None
