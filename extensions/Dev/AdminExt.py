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
        name="module",
        aliases=["모듈", "m","extension", "확장", "ext"],
        description="",
        help=""
    )
    async def module_cmd(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            embedfactory = EmbedFactory(
                title="[ Admin Extension - Module Commands ]",
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
    @module_cmd.command(
        name="load",
        aliases=["로드", "불러오기"],
        description="",
        help=""
    )
    async def module_load_cmd(self, ctx: commands.Context, *, params_raw: str):
        params = params_raw.split(' ')
        self.bot.get_logger().info(
            msg=f"[AdminExt] User {ctx.author.name}#{ctx.author.discriminator} used `module.load` command with "
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
                    description="Module commands must be used with cli-style arguments to define module to load!"
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