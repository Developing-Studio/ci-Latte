from discord.ext import commands
from utils import get_cog_name_in_ext


class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="tsi",
        description="VoiceRegion enum does not have `south-korea` region, so we made PR to add it."
    )
    async def testserverinfo(self, ctx: commands.Context):
        await ctx.send(content=f"> Your server region is : {ctx.guild.region}. type : {type(ctx.guild.region)}")

    @commands.command(
        name="hellothisisverification",
        description="Verification command for adding Latte on koreanbots.",
        help="`l; hellothisisverification` to use."
    )
    async def koreanbots_verfy(self, ctx: commands.Context):
        await ctx.send(content="")

    @commands.command(
        name="개발자바보",
        description="유저 HOREON이 많은 양의 테스트를 수행해준 노고에 대한 보답으로 건의받은 명령어"
    )
    async def lapisbabo(self, ctx: commands.Context):
        await ctx.send(content="라피스 바보")


def setup(bot):
    cog = TestCog(bot)
    bot.get_logger().info(
        msg="[FeatureTestExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=TestCog.__module__)
    bot.add_cog(cog)