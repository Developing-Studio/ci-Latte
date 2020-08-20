from discord.ext import commands
import discord
from core import Latte
from utils import get_cog_name_in_ext


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
        aliases=["expel", "추방"],
        description="kick a member from the server.",
        help="`l; moderation kick @member (reason)` to use."
    )
    async def ban(self, ctx: commands.Context, target_member: discord.Member, *, reason: str = ""):
        await target_member.ban(reason=reason)

    @moderation.command(
        name="kick",
        aliases=["expel", "추방"],
        description="kick a member from the server.",
        help="`l; moderation kick @member (reason)` to use."
    )
    async def kick(self, ctx: commands.Context, target_member: discord.Member, *, reason: str = ""):
        await target_member.unban(reason=reason)


def setup(bot: Latte):
    cog = ModerationCog(bot)
    bot.get_logger().info(
        msg="[GameExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=ModerationCog.__module__)
    bot.add_cog(cog)