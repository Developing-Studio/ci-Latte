from typing import List

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
        return await ctx.send(
            embed=await EmbedFactory(
                title="[ 관리 ] 멤버를 추방했습니다!",
                footer=EmbedFactory.get_command_caller(ctx.author),
                color=EmbedFactory.default_color,
                fields=[
                    {
                        "name": "추방한 멤버",
                        "value": EmbedFactory.get_user_info(target_member),
                        "inline": False
                    },
                    {
                        "name": "추방 사유",
                        "value": reason,
                        "inline": False
                    }
                ]
            ).build()
        )

    @moderation.command(
        name="ban",
        aliases=["차단", "밴"],
        description="kick a member from the server.",
        help="`l; moderation ban @member (reason)` to use."
    )
    async def ban(self, ctx: commands.Context, target_member: discord.Member, *, reason: str = ""):
        await target_member.ban(reason=reason)
        return await ctx.send(
            embed=await EmbedFactory(
                title="[ 관리 ] 멤버를 차단했습니다!",
                footer=EmbedFactory.get_command_caller(ctx.author),
                color=EmbedFactory.default_color,
                fields=[
                    {
                        "name": "차단한 멤버",
                        "value": EmbedFactory.get_user_info(target_member),
                        "inline": False
                    },
                    {
                        "name": "차단 사유",
                        "value": reason,
                        "inline": False
                    }
                ]
            ).build()
        )

    @moderation.command(
        name="unban",
        aliases=["pardon", "용서", "언밴"],
        description="kick a member from the server.",
        help="`l; moderation unban @member (reason)` to use."
    )
    async def unban(self, ctx: commands.Context, target_id: int, *, reason: str = ""):
        target_ban_entry: discord.guild.BanEntry = discord.utils.find(lambda be: be.user.id == target_id, await ctx.guild.bans())
        if target_ban_entry is None:
            return await ctx.send("해당 유저는 차단되지 않았습니다!")
        await ctx.guild.unban(target_ban_entry.user, reason=reason)
        return await ctx.send(
            embed=await EmbedFactory(
                title="[ 관리 ] 멤버를 차단 해제했습니다!",
                footer=EmbedFactory.get_command_caller(ctx.author),
                color=EmbedFactory.default_color,
                fields=[
                    {
                        "name": "차단한 멤버",
                        "value": EmbedFactory.get_user_info(target_ban_entry.user),
                        "inline": False
                    },
                    {
                        "name": "차단 해제 사유",
                        "value": reason,
                        "inline": False
                    },
                    {
                        "name": "이 유저가 차단되었던 사유",
                        "value": target_ban_entry.reason,
                        "inline": False
                    }
                ]
            ).build()
        )

    @moderation.command(
        name="clearchat",
        aliases=["chatclear", "채팅청소", "메세지청소"],
        description="Remove certain number of messages from channel.",
        help="`l; moderation clearchat (count=3)` to use."
    )
    async def clearchat(self, ctx: commands.Context, amount: int = 5):
        if amount < 1:
            return await ctx.send(f"{amount} 는 너무 적습니다!")
        deleted: List[discord.Message] = await ctx.channel.purge(limit=amount+1)     # Add 1 to :param amout: to delete command message.
        return await ctx.send(
            embed=EmbedFactory.COMMAND_LOG_EMBED(
                title="메세지 청소 결과",
                description=f"{len(deleted)-1}개의 메세지를 청소했습니다!",
                user=ctx.author
            )
        )


def setup(bot: Latte):
    cog = ModerationCog(bot)
    bot.get_logger().info(
        msg="[ModerationExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=ModerationCog.__module__)
    bot.add_cog(cog)