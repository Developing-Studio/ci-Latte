from discord.ext import commands
from core import Latte, LatteParty, LatteUser
from utils import get_cog_name_in_ext


class PartyCog(commands.Cog):
    def __init__(self, bot: Latte):
        self.bot = bot
        
    @commands.group(
        name="party",
        aliases=["파티"],
        description="",
        help=""
    )
    async def party(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            pass

    @party.command(
        name="create",
        aliases=["생성"],
        description="",
        help=""
    )
    async def create(self, ctx: commands.Context, *, params_raw: str):
        params = params_raw.split(":")
        name = params[0]
        desc = params[1]


def setup(bot: Latte):
    cog = PartyCog(bot)
    bot.get_logger().info(
        msg="[GameExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=PartyCog.__module__)
    bot.add_cog(cog)
