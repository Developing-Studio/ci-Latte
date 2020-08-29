from discord.ext import commands
from core import Latte
from utils import get_cog_name_in_ext


class EconomyCog(commands.Cog):
    def __init__(self, bot: Latte):
        self.bot = bot

    @commands.group(
        name="economy",
        aliases=["경제"],
        description="group command for economy features",
        help="`l; economy` to use."
    )
    async def economy_cmd(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            # Do something when any subcommands are not called.
            pass

    @economy_cmd.command(
        name="wallet",
        aliases=["지갑"],
        description="Show your current information on economy feature.",
        help=""
    )
    async def wallet(self, ctx: commands.Context):
        pass


def setup(bot: Latte):
    cog = EconomyCog(bot)
    bot.get_logger().info(
        msg="[EconomyExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=EconomyCog.__module__)
    bot.add_cog(cog)
