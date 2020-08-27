from discord.ext import commands
from utils import get_cog_name_in_ext


class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    cog = TestCog(bot)
    bot.get_logger().info(
        msg="[FeatureTestExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=TestCog.__module__)
    bot.add_cog(cog)