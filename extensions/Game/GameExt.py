from discord.ext import commands

from core import Latte
from utils import EmbedFactory, get_cog_name_in_ext


class GameCog(commands.Cog):
    def __init__(self, bot: Latte):
        self.bot: Latte = bot
        super(GameCog, self).__init__()

    @commands.command(
        name="dice",
        description="6면짜리 주사위를 던져요!",
        aliases=["주사위"]
    )
    async def roll_the_dice(self, ctx: commands.Context, start: int = 1, end: int = 6):
        if start > end:
            start, end = end, start
        import random
        result = random.randint(start, end)
        result_embed_factory = EmbedFactory(
            title="🎲 주사위를 던졌어요!",
            description=f"결과 : {result}",
            color=EmbedFactory.default_color,
            author={
                "name": self.bot.user.display_name,
                "icon_url": self.bot.user.avatar_url
            },
            footer={
                "text": f"command executed by {EmbedFactory.get_user_info(user=ctx.author)}",
                "icon_url": ctx.author.avatar_url
            }
        )
        await ctx.send(embed=await result_embed_factory.build())


def setup(bot: Latte):
    cog = GameCog(bot)
    bot.get_logger().info(
        msg="[GameExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=GameCog.__module__)
    bot.add_cog(cog)
