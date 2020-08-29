from typing import List

from discord.ext import commands
from core import Latte, BadExtArguments, ConfigNotFound, ConfigNotLoaded, ConfigAlreadyLoaded, ExtensionManager
from utils import EmbedFactory, get_cog_name_in_ext


class ConfigCog(commands.Cog):

    def __init__(self, bot: Latte):
        self.bot = bot

    @commands.is_owner()
    @commands.group(
        name="config",
        aliases=["cfg", "컨피그", "콘피그"],
        description="",
        help=""
    )
    async def config(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            embedfactory = EmbedFactory(
                title="[ Admin Extension - Config Commands ]",
                description="This is an admin-only extension to manage Latte`s config in discord chat.",
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
            await ctx.send(
                embed=await embedfactory.build()
            )

    @commands.is_owner()
    @config.command(
        name="load",
        aliases=["로드", "불러오기"],
        description="",
        help=""
    )
    async def config_load(self, ctx: commands.Context):
        description: str = "UNDEFINED"  # Set some default text to prevent empty embed error.
        try:
            self.bot.config.load()
        except ConfigAlreadyLoaded as e:
            description = str(e)
        except ConfigNotFound as e:
            description = str(e)
        else:
            description = "Config successfully loaded :D"

        await ctx.send(
            embed=EmbedFactory.LOG_EMBED(
                title="[ Admin Extension - Config Load Result ]",
                description=description
            )
        )

    @commands.is_owner()
    @config.command(
        name="unload",
        aliases=["언로드", "제거하기"],
        description="",
        help=""
    )
    async def config_unload(self, ctx: commands.Context):
        description: str = "UNDEFINED"  # Set some default text to prevent empty embed error.
        try:
            self.bot.config.unload()
        except ConfigNotLoaded as e:
            description = str(e)
        else:
            description = "Config successfully unloaded :D"

        await ctx.send(
            embed=EmbedFactory.LOG_EMBED(
                title="[ Admin Extension - Config Unload Result ]",
                description=description
            )
        )

    @commands.is_owner()
    @config.command(
        name="reload",
        aliases=["리로드", "다시불러오기"],
        description="",
        help="`l;"
    )
    async def config_reload(self, ctx: commands.Context):
        description: str = "UNDEFINED"  # Set some default text to prevent empty embed error.
        try:
            self.bot.config.reload()
        except ConfigNotLoaded as e:
            description = str(e)
        except ConfigNotFound as e:
            description = str(e)
        else:
            description = "Config successfully reloaded :D"

        await ctx.send(
            embed=EmbedFactory.LOG_EMBED(
                title="[ Admin Extension - Config Reload Result ]",
                description=description
            )
        )

    @commands.is_owner()
    @config.command(
        name="show",
        aliases=["보기"],
        description="",
        help="`l;"
    )
    async def config_show(self, ctx: commands.Context):
        import json
        # config instance is json type, so it only have primitive values.
        copied = self.bot.config.config.copy()
        copied.pop("api")
        copied.pop("token")
        copied.pop("test")
        copied.pop("lavalink")
        copied.pop("database")
        config_lines: List[str] = json.dumps(obj=copied, ensure_ascii=False, indent=4).split('\n')
        await ctx.author.send(content=": Start of stored config content :")
        for line_num, line in enumerate(config_lines):
            await ctx.author.send(
                content=f"> [{line_num}]  {line}"
            )
        await ctx.author.send(content=": End of stored config content :")

    @commands.group(
        name="ext-config",
        aliases=[""],
        description="",
        help=""
    )
    async def ext_config(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            pass

    @ext_config.command(
        name="reload",
        aliases=["다시불러오기", "리로드"],
        description="",
        help=""
    )
    async def ext_config_reload(self, ctx: commands.Context):
        self.bot.config.reload()
        self.bot.ext = ExtensionManager(extensions_config=self.config["ext"])


def setup(bot: Latte):
    cog = ConfigCog(bot)
    bot.get_logger().info(
        msg="[ConfigExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=ConfigCog.__module__)
    bot.add_cog(cog)
