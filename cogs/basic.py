import discord
import datetime
from discord.ext import commands


class Basic(commands.Cog):
    """
    매우 기본적인 명령어들이 있는 Cog 입니다.
    """
    def __init__(self, bot):
        self.bot = bot

    def is_channel_correct(self, channel_id: int):
        if channel_id in self.bot.screenshot_channels:
            return True
        return False

    @staticmethod
    def get_kst_datetime():
        return datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9)))

    @commands.command(name="핑", aliases=["ping", "vld", "ㅔㅑㅜㅎ"])
    async def ping(self, ctx: commands.Context):
        """
        매우 기본적인 핑 명령어입니다.
        """
        await ctx.send(f":ping_pong: 퐁! ({round(self.bot.latency * 1000)}ms)")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if len(message.attachments) == 0:
            return
        attachments = [x for x in message.attachments if [".png", ".jpg", ".jpeg", ".gif"] in x.filename]
        if len(attachments) == 0:
            return
        await message.add_reaction("<:prograde:733227223670063176>")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        with open("hof.txt", "r", encoding="UTF-8") as f:
            if payload.message_id in f.readlines():
                return
        channel_id = payload.channel_id
        if not self.is_channel_correct(channel_id):
            return
        msg: discord.Message = await self.bot.get_channel(channel_id).fetch_message(payload.message_id)
        emoji = [x for x in msg.reactions if str(x) == "<:prograde:733227223670063176>"]
        if len(emoji) == 0:
            return
        count = emoji[0].count
        if self.bot.user.id in [x.id for x in await emoji[0].users().flatten()]:
            count -= 1
        if count >= 3:
            hof_channel = self.bot.get_hof_channel()
            embed = discord.Embed(title="3+ 업보트", description=f"[사진으로 바로가기]({msg.jump_url})", timestamp=self.get_kst_datetime())
            embed.set_author(name=msg.author.name + f" ({str(msg.author)})", icon_url=msg.author.avatar_url)
            img = [x for x in msg.attachments if [".png", ".jpg", ".jpeg", ".gif"] in x.filename]
            if len(img) != 0:
                embed.set_image(url=img[0].url)
            await hof_channel.send(embed=embed)
            with open("hof.txt", "a", encoding="UTF-8") as f:
                f.write(f"{payload.message_id}\n")


def setup(bot):
    bot.add_cog(Basic(bot))
