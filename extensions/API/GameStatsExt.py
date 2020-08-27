from discord.ext import commands
from core import Latte
from utils import get_cog_name_in_ext


class LOL_API:
    def __init__(self, token: str):
        self.token = token


class PUBG_API:
    def __init__(self, token: str):
        self.token = token


class R6S_API:
    def __init__(self, token: str):
        self.token = token


class GameStatsCog(commands.Cog):
    def __init__(self, bot: Latte):
        self.bot = bot
        self.lol = LOL_API(bot.config.config["api"])
        self.pubg = PUBG_API(bot.config.config["api"])
        self.r6s = R6S_API(bot.config.config["api"])


def setup(bot: Latte):
    cog = GameStatsCog(bot)
    bot.get_logger().info(
        msg="[GameExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=GameStatsCog.__module__)
    bot.add_cog(cog)
