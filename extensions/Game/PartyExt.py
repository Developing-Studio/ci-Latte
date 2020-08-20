from discord.ext import commands
from core import Latte
from utils import get_cog_name_in_ext


class PartyCog(commands.Cog):
    def __init__(self, bot: Latte):
        self.bot = bot


def setup(bot: Latte):
    cog = PartyCog(bot)
    bot.get_logger().info(
        msg="[GameExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=PartyCog.__module__)
    bot.add_cog(cog)
