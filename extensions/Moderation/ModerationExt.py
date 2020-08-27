from discord.ext import commands
import discord
from core import Latte
from utils import get_cog_name_in_ext, EmbedFactory


class ModerationCog(commands.Cog):
    def __init__(self, bot: Latte):
        self.bot = bot

    @commands.has_guild_permissions(administrator=True)
    @commands.group(
        name="moderation",
        aliases=["management", "관리"],
        description="",
        help=""
    )
    async def moderation(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            pass

    @moderation.command(
        name="kick",
        aliases=["expel", "추방"],
        description="kick a member from the server.",
        help="`l; moderation kick @member (reason)` to use."
    )
    async def kick(self, ctx: commands.Context, target_member: discord.Member, *, reason: str = ""):
        await target_member.kick(reason=reason)

    @moderation.command(
        name="ban",
        aliases=["차단", "밴"],
        description="kick a member from the server.",
        help="`l; moderation ban @member (reason)` to use."
    )
    async def ban(self, ctx: commands.Context, target_member: discord.Member, *, reason: str = ""):
        await target_member.ban(reason=reason)

    @moderation.command(
        name="unban",
        aliases=["pardon", "용서", "언밴"],
        description="kick a member from the server.",
        help="`l; moderation unban @member (reason)` to use."
    )
    async def unban(self, ctx: commands.Context, target_id: int, *, reason: str = ""):
        target_ban_entry: discord.guild.BanEntry = discord.utils.find(lambda be: be.user.id == id, await ctx.guild.bans())
        await ctx.guild.unban(target_ban_entry.user, reason=reason)
        unban_embed = EmbedFactory
        unban_embed = discord.Embed(title="**언밴**", description=f"*{target_ban_entry.user.mention} 님이 밴 해제 처리되었습니다.*")
        unban_embed.add_field(name="**사유**", value=f"*{reason}*", inline=False)

        await ctx.send(embed=unban_embed)

    @moderation.command(
        name="clearchat",
        aliases=["chatclear", "채팅청소", "메세지청소"],
        description="Remove certain number of messages from channel.",
        help="`l; moderation clearchat (count=3)` to use."
    )
    async def clearchat(self, ctx: commands.Context, amount: int = 5):
        if amount < 1:
            return await ctx.send(f"{amount} 는 너무 적습니다!")
        await ctx.channel.purge(limit=amount+1)     # Add 1 to :param amout: to delete command message.


def setup(bot: Latte):
    cog = ModerationCog(bot)
    bot.get_logger().info(
        msg="[ModerationExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=ModerationCog.__module__)
    bot.add_cog(cog)