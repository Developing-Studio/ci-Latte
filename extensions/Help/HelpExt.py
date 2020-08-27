from discord.ext import commands
from core import Latte, parse_doc
from utils import get_cog_name_in_ext, EmbedFactory


class HelpCog(commands.Cog):
    def __init__(self, bot: Latte):
        self.bot = bot
        self.doc_package = parse_doc(root=self.bot.config["documents_root"])
        print(f"[HelpExt] parsed documents data :\n{self.doc_package}")

    @commands.command(
        name="help",
        aliases=["commands", "도움말", "도움", "명령어"],
        description="",
        help=""
    )
    async def help(self, ctx: commands.Context):
        await ctx.send(
            embed=EmbedFactory.LOG_EMBED(
                title="도움말 명령어는 현재 준비중입니다!",
                description="조만간 업데이트 될 예정이니 조금만 기다려주세요 :D"
            )
        )

    @commands.command(
        name="sample",
        aliases=["샘플"],
        description="",
        help=""
    )
    async def sample(self, ctx: commands.Context):
        await ctx.send(
            embed=EmbedFactory.LOG_EMBED(
                title="Opened `docs/sample.md`",
                description="```md\n"
                            f"{self.doc_package.get_doc('sample.md').get_content()}\n"
                            "```"
            )
        )

    @commands.command(
        name="intro",
        aliases=["인트로"],
        description="",
        help=""
    )
    async def test_intro(self, ctx: commands.Context):
        await ctx.send(
            embed=EmbedFactory.LOG_EMBED(
                title="Opened `docs/ko-kr/intro.md`",
                description="```md\n"
                            f"{self.doc_package.get_doc('ko-kr/intro.md').get_content()}\n"
                            "```"
            )
        )

    
def setup(bot: Latte):
    cog = HelpCog(bot)
    bot.get_logger().info(
        msg="[BotInfoExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=HelpCog.__module__)
    bot.add_cog(cog)