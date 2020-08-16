import logging

from discord.ext import commands
from core import Latte, ExtensionManager
from utils import EmbedFactory
from typing import Dict, List, Optional


class AdminCog(commands.Cog):

    def __init__(self, bot: Latte):
        self.bot = bot

    @commands.is_owner()
    @commands.group(
        name="ext",
        aliases=["확장", "extension", "모듈", "m", "module"],
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
                    "text": f"{ctx.author.name}#{ctx.author.discriminator} 님이 사용한 명령어의 결과입니다!",
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
        params = params_raw.split(' ')
        self.bot.get_logger().info(
            msg=f"[AdminExt] User {ctx.author.name}#{ctx.author.discriminator} used `ext.load` command with "
                f"following arguments : {params} "
        )

        params = await self.parse_params(params)

        category: str = params.pop("category") if "category" in params.keys() else ''
        name: str = params.pop("name") if "name" in params.keys() else ''
        dir: str = params.pop("dir") if "dir" in params.keys() else ''

        if category != '' and name != '':
            self.bot.ext.load_ext(bot=self.bot, ext_category=category, ext_name=name)
        elif dir != '':
            self.bot.ext.load_ext(bot=self.bot, ext_dir=dir)
        else:
            await ctx.send(
                embed=EmbedFactory.WARN_EMBED(
                    title="Invalid usage!",
                    description="Module commands must be used with cli-style arguments to define module to load!\n"
                                "usage: `ext load -c (category) -n (name)` or `ext load -d (dir)`"
                )
            )


    @commands.is_owner()
    @ext_cmd.command(
        name="unload",
        aliases=["언로드", "제거하기"],
        description="",
        help=""
    )
    async def ext_unload_cmd(self, ctx: commands.Context, *, params_raw: str):
        params = params_raw.split(' ')
        self.bot.get_logger().info(
            msg=f"[AdminExt] User {ctx.author.name}#{ctx.author.discriminator} used `ext.unload` command with "
                f"following arguments : {params} "
        )

        params = await self.parse_params(params)

        category: str = params.pop("category") if "category" in params.keys() else ''
        name: str = params.pop("name") if "name" in params.keys() else ''
        dir: str = params.pop("dir") if "dir" in params.keys() else ''

        if category != '' and name != '':
            self.bot.ext.unload_ext(bot=self.bot, ext_category=category, ext_name=name)
        elif dir != '':
            self.bot.ext.unload_ext(bot=self.bot, ext_dir=dir)
        else:
            await ctx.send(
                embed=EmbedFactory.WARN_EMBED(
                    title="Invalid usage!",
                    description="Module commands must be used with cli-style arguments to define module to load!\n"
                                "usage: `ext unload -c (category) -n (name)` or `ext unload -d (dir)`"
                )
            )

    @commands.is_owner()
    @ext_cmd.command(
        name="reload",
        aliases=["리로드", "다시불러오기"],
        description="",
        help=""
    )
    async def module_reload_cmd(self, ctx: commands.Context, *, params_raw: str):
        params = params_raw.split(' ')
        self.bot.get_logger().info(
            msg=f"[AdminExt] User {ctx.author.name}#{ctx.author.discriminator} used `ext.reload` command with "
                f"following arguments : {params} "
        )

        params = await self.parse_params(params)

        category: str = params.pop("category") if "category" in params.keys() else ''
        name: str = params.pop("name") if "name" in params.keys() else ''
        dir: str = params.pop("dir") if "dir" in params.keys() else ''

        if category != '' and name != '':
            self.bot.ext.reload_ext(bot=self.bot, ext_category=category, ext_name=name)
        elif dir != '':
            self.bot.ext.reload_ext(bot=self.bot, ext_dir=dir)
        else:
            await ctx.send(
                embed=EmbedFactory.WARN_EMBED(
                    title="Invalid usage!",
                    description="Module commands must be used with cli-style arguments to define module to load!\n"
                                "usage: `ext reload -c (category) -n (name)` or `ext reload -d (dir)`"
                )
            )

    async def parse_params(self, params: List[str]) -> Dict[str, str]:
        parsed: Dict[str, str] = {}
        for param in params:
            if param.startswith('-c'):
                # Category param
                parsed["category"] = param.replace('-c', '')
                self.bot.get_logger().info(
                    msg=f"[AdminExt] Caught parameter `category` with value {parsed['category']}"
                )
            elif param.startswith('-n'):
                # Name param
                parsed["name"] = param.replace('-n', '')
                self.bot.get_logger().info(
                    msg=f"[AdminExt] Caught parameter `name` with value {parsed['name']}"
                )
            elif param.startswith('-d'):
                parsed["dir"] = param.replace('-d', '')
                self.bot.get_logger().info(
                    msg=f"[AdminExt] Caught parameter `dir` with value {parsed['dir']}"
                )
        return parsed


def setup(bot: Latte):
    bot.add_cog(AdminCog(bot))