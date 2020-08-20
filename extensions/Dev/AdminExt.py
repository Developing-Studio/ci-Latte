from discord.ext import commands
import json
from core import Latte, BadExtArguments
from utils import EmbedFactory, get_cog_name_in_ext
from typing import Dict, List, Optional, Type


class AdminCog(commands.Cog):

    def __init__(self, bot: Latte):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        msg = f"[AdminExt.on_command] User {EmbedFactory.get_user_info(user=ctx.author)} used `{ctx.cog.qualified_name if ctx.cog is not None else 'bot'}:{ctx.command.name}` command with "\
              f"following arguments : \n{ctx.args, json.dumps(ctx.kwargs, indent=4, ensure_ascii=False)} "
        self.bot.get_logger().info(
            msg=f"[AdminExt.on_command] User {EmbedFactory.get_user_info(user=ctx.author)} used `{ctx.cog.qualified_name if ctx.cog is not None else 'bot'}:{ctx.command.name}` command with "
                f"following arguments : \n{ctx.args, json.dumps(ctx.kwargs, indent=4, ensure_ascii=False)} "
        )
        await self.bot.get_channel(self.bot.bot_config.config["admin_log"]).send(
            content="command executed 시발"
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Type[Exception]):
        self.bot.get_logger().error(
            msg=f"[AdminExt.on_command] User {EmbedFactory.get_user_info(user=ctx.author)} used `{ctx.cog.qualified_name if ctx.cog is not None else 'bot'}:{ctx.command.name}` command with "
                f"following arguments : \n{ctx.args, json.dumps(ctx.kwargs, indent=4, ensure_ascii=False)}\n, and error :\n{error}"
        )
        await ctx.channel.send(
            content=f"An error occured during executing command `{ctx.cog.qualified_name if ctx.cog is not None else 'bot'}:{ctx.command.name}`\n> {error}"
        )

    @commands.is_owner()
    @commands.command(
        name="stop",
        aliases=["종료", 's', "shutdown"],
        description="",
        help=""
    )
    async def stop(self, ctx: commands.Context):
        embed = EmbedFactory.COMMAND_LOG_EMBED(
                title="[ Command Result ]",
                description="봇을 종료합니다!",
                user=ctx.author
        )
        await ctx.send(embed=embed)
        self.bot.get_logger().info("[AdminExt] bot stop command detected. stopping bot...")
        self.bot.do_reboot = False
        await self.bot.close()

    @commands.is_owner()
    @commands.command(
        name="restart",
        aliases=["재시작", 'r', "reboot"],
        description="",
        help=""
    )
    async def restart(self, ctx: commands.Context):
        embed = EmbedFactory.COMMAND_LOG_EMBED(
                title="[ Command Result ]",
                description="봇을 재시작합니다!",
            user=ctx.author
        )
        await ctx.send(embed=embed)
        self.bot.get_logger().info("[AdminExt] bot restart command detected. stopping bot...")
        self.bot.do_reboot = True
        await self.bot.close()

    @commands.is_owner()
    @commands.group(
        name="extension",
        aliases=["확장", "ext", "모듈", 'm', "module"],
        description="",
        help=""
    )
    async def ext_cmd(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            embedfactory = EmbedFactory(
                title="[ Admin Extension - Extension Commands ]",
                description="This is an admin-only extension to manage Latte`s extensions in discord chat.",
                color=EmbedFactory.default_color,
                author={
                    "name": f"라떼봇 v{self.bot.bot_version}",
                    "icon_url": self.bot.user.avatar_url
                },
                footer={
                    "text": f"command executed by {EmbedFactory.get_user_info(user=ctx.author)}",
                    "icon_url": ctx.author.avatar_url
                }
            )

    @commands.is_owner()
    @ext_cmd.command(
        name="load",
        aliases=["로드", "불러오기"],
        description="",
        help=""
    )
    async def ext_load_cmd(self, ctx: commands.Context, *, params_raw: str):
        params = await self.parse_params(params_raw)

        category: str = params.pop("category") if "category" in params.keys() else ''
        name: str = params.pop("name") if "name" in params.keys() else ''
        dir: str = params.pop("dir") if "dir" in params.keys() else ''

        if (dir == '' and (category == '' or name == '')) or ((category == '' and name == '') and dir == ''):
            await ctx.send(
                embed=EmbedFactory.WARN_EMBED(
                    title="Invalid usage!",
                    description="Module commands must be used with cli-style arguments to define module to load!\n"
                                "usage: `ext load -c (category) -n (name)` or `ext load -d (dir)`"
                )
            )
        else:
            try:
                self.bot.ext.load_ext(bot=self.bot, ext_category=category, ext_name=name, ext_dir=dir)
            except BadExtArguments as e:
                error_embed = EmbedFactory.ERROR_EMBED(e)
                await ctx.send(embed=error_embed)
            else:
                result_embed = EmbedFactory.COMMAND_LOG_EMBED(
                    title="[ Successfully Reloaded Extension ]",
                    description=f"ext_args : {params_raw}",
                    user=ctx.author
                )
                await ctx.send(embed=result_embed)

                if category == "Utility" and name == "invites":
                    # During reloading / loading module again, InvitesExt extension lose it`s trackin data.
                    # So we need to call update() method and re-track invites data.
                    # But, discord.Guild.invites() method is a coroutine,
                    # it can`t be called in __init__ method while bot is running.
                    # So, we need to call update() method manually right after reloading/loading extension again.
                    await self.bot.get_cog(name).update()

    @commands.is_owner()
    @ext_cmd.command(
        name="unload",
        aliases=["언로드", "제거하기"],
        description="",
        help=""
    )
    async def ext_unload_cmd(self, ctx: commands.Context, *, params_raw: str):
        params = await self.parse_params(params_raw)

        category: str = params.pop("category") if "category" in params.keys() else ''
        name: str = params.pop("name") if "name" in params.keys() else ''
        dir: str = params.pop("dir") if "dir" in params.keys() else ''

        if (dir == '' and (category == '' or name == '')) or ((category == '' and name == '') and dir == ''):
            await ctx.send(
                embed=EmbedFactory.WARN_EMBED(
                    title="Invalid usage!",
                    description="Module commands must be used with cli-style arguments to define module to load!\n"
                                "usage: `ext unload -c (category) -n (name)` or `ext unload -d (dir)`"
                )
            )
        else:
            try:
                self.bot.ext.unload_ext(bot=self.bot, ext_category=category, ext_name=name, ext_dir=dir)
            except BadExtArguments as e:
                error_embed = EmbedFactory.ERROR_EMBED(e)
                await ctx.send(embed=error_embed)
            else:
                result_embed = EmbedFactory.COMMAND_LOG_EMBED(
                    title="[ Successfully Reloaded Extension ]",
                    description=f"ext_args : {params_raw}",
                    user=ctx.author
                )
                await ctx.send(embed=result_embed)

    @commands.is_owner()
    @ext_cmd.command(
        name="reload",
        aliases=["리로드", "다시불러오기"],
        description="",
        help=""
    )
    async def module_reload_cmd(self, ctx: commands.Context, *, params_raw: str):
        params = await self.parse_params(params_raw)

        category: str = params.pop("category") if "category" in params.keys() else ''
        name: str = params.pop("name") if "name" in params.keys() else ''
        dir: str = params.pop("dir") if "dir" in params.keys() else ''

        if (dir == '' and (category == '' or name == '')) or ((category == '' and name == '') and dir == ''):
            await ctx.send(
                embed=EmbedFactory.WARN_EMBED(
                    title="Invalid usage!",
                    description="Module commands must be used with cli-style arguments to define module to load!\n"
                                "usage: `ext reload -c (category) -n (name)` or `ext reload -d (dir)`"
                )
            )
        else:
            try:
                self.bot.ext.reload_ext(bot=self.bot, ext_category=category, ext_name=name, ext_dir=dir)
            except BadExtArguments as e:
                error_embed = EmbedFactory.ERROR_EMBED(e)
                await ctx.send(embed=error_embed)
            else:
                result_embed = EmbedFactory.COMMAND_LOG_EMBED(
                    title="[ Successfully Reloaded Extension ]",
                    description=f"ext_args : {params_raw}",
                    user=ctx.author
                )
                await ctx.send(embed=result_embed)

                if category == "Utility" and name == "invites":
                    # During reloading / loading module again, InvitesExt extension lose it`s trackin data.
                    # So we need to call update() method and re-track invites data.
                    # But, discord.Guild.invites() method is a coroutine,
                    # it can`t be called in __init__ method while bot is running.
                    # So, we need to call update() method manually right after reloading/loading extension again.
                    await self.bot.get_cog(name).update()

    async def parse_params(self, params_raw: str) -> Dict[str, str]:
        params = params_raw.split('-')
        print(params)
        parsed: Dict[str, str] = {}
        for param in params:
            if param.startswith('c'):
                # Category param
                parsed["category"] = param[1:].replace(' ', '')
                self.bot.get_logger().info(
                    msg=f"[AdminExt] Caught parameter `category` with value {parsed['category']}"
                )
            elif param.startswith('n'):
                # Name param
                parsed["name"] = param[1:].replace(' ', '')
                self.bot.get_logger().info(
                    msg=f"[AdminExt] Caught parameter `name` with value {parsed['name']}"
                )
            elif param.startswith('d'):
                parsed["dir"] = param[1:].replace(' ', '')
                self.bot.get_logger().info(
                    msg=f"[AdminExt] Caught parameter `dir` with value {parsed['dir']}"
                )
        return parsed


def setup(bot: Latte):
    cog = AdminCog(bot)
    bot.get_logger().info(
        msg="[AdminExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=AdminCog.__module__)
    bot.add_cog(cog)