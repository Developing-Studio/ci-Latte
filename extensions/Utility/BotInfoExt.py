from typing import Dict

from discord.ext import commands
import discord
from core import Latte
from utils import EmbedFactory, get_cog_name_in_ext


class BotInfoCog(commands.Cog):
    status_dict: Dict[str, str] = {
        discord.Status.online: "온라인",
        discord.Status.offline: "오프라인",
        discord.Status.idle: "자리비움",
        discord.Status.do_not_disturb: "방해금지"
    }

    def __init__(self, bot: Latte):
        self.bot = bot

    # Commands
    @commands.command(
        name="ping",
        aliases=["핑"],
        description="봇의 응답 지연시간을 보여줍니다. 핑퐁!",
        help="`라떼야 핑`"
    )
    async def ping(self, ctx: commands.Context):
        await ctx.send(f"Pong! ({round(self.bot.latency * 1000)}ms)")

    @commands.command(
        name="invite-url",
        aliases=["초대", "invite"],
        description="봇을 서버에 초대할 수 있는 링크를 생성합니다.",
        help=""
    )
    async def get_invite_url(self, ctx: commands.Context):
        """
        봇 초대링크를 생성, 전송합니다.
        """
        bot_invite_url: str = discord.utils.oauth_url(client_id=str(self.bot.user.id)) + "&permissions=8"
        await ctx.send(f"> 초대 링크입니다! → {bot_invite_url}")

    @commands.command(
        name="report",
        aliases=["제보"],
        description="건의사항이나 버그 내용을 메세지로 받아 개발자들에게 전달합니다. 혹은 메세지 없이 사용해 공식 커뮤니티 제보 채널로 연결합니다.",
        help=""
    )
    async def report(self, ctx: commands.Context, report_type='', *, report_content: str = ''):
        print(f"{ctx.message.content}")
        print(f"report_type == {report_type}")
        print(f"report_content == {report_content}")

        if report_type == '' and report_content == '':
            await ctx.send(
                content=f"> 봇 공식 커뮤니티에서 버그를 제보해주세요!\n"
                        f"{self.bot.discord_base_invite + self.bot.bug_report_invite}"
            )
        elif report_content != '' and report_type in ["건의", "버그"]:

            bug_embed_factory = EmbedFactory(
                title=f"[ 라떼봇 제보 ]!",
                color=EmbedFactory.error_color,
                author={
                    "name": f"{ctx.author} ({ctx.author.id})",
                    "icon_url": ctx.author.avatar_url
                },
                fields=[
                    {
                        "name": "제보 유형",
                        "value": report_type,
                        "inline": False
                    },
                    {
                        "name": "제보 내용",
                        "value": report_content,
                        "inline": False
                    },
                    {
                        "name": "제보한 곳",
                        "value": f"서버 : {ctx.guild.name}\n 서버 주인 : {ctx.guild.owner} ({ctx.guild.owner.id})\n채널 : {ctx.channel.name}",
                        "inline": False
                    }
                ]
            )
            await bug_embed_factory.add_field(name="제보 유형", value=report_type, inline=False)
            await bug_embed_factory.add_field(name="제보 내용", value=report_content, inline=False)

            for dev_id in self.bot.owner_id:
                developer_user: discord.User = self.bot.get_user(dev_id)
                await developer_user.send(embed=await bug_embed_factory.build())

            await ctx.send("> 개발자들에게 해당 사항을 제보했습니다!")
            await ctx.send(
                content=f"> 추가적인 버그 및 봇 업데이트는 봇 공식 커뮤니티에서 확인해주세요!\n"
                        f"{self.bot.discord_base_invite + self.bot.official_community_invite}"
            )

        else:
            await ctx.send("> 잘못된 양식입니다!")

    @commands.command(
        name='bot-info',
        description='봇의 정보를 보여줍니다.',
        aliases=["봇정보", "봇", "bi", "botinfo"]
    )
    async def get_bot_info(self, ctx: commands.Context):
        # Create an Embed which contains member's information
        caller_info = EmbedFactory.get_command_caller(user=ctx.author)
        user_count = len(list(filter(lambda u: not u.bot, self.bot.users)))
        created = self.bot.user.created_at

        embed_factory = EmbedFactory(
            title="라떼봇 정보",
            description=f"현재 **`{len(self.bot.guilds)}`**개의 서버에서 사용중이며, **`{user_count}`**명의 유저들과 소통중입니다.",
            color=EmbedFactory.default_color,
            author={
                "name": f"{EmbedFactory.get_user_info(user=self.bot.user, contain_id=True)}",
                "icon_url": self.bot.user.avatar_url
            },
            footer={
                "text": f"{caller_info['text']}",
                "icon_url": f"{caller_info['icon_url']}"
            },
            thumbnail_url=self.bot.user.avatar_url,
            fields=[
                {
                    "name": "**개발자**",
                    "value": "sleepylapis#1608",
                    "inline": False
                },
                {
                    "name": "**봇 운영 기간**",
                    "value": f"{created.year}년 {created.month}월 {created.day}일 ~ 현재",
                    "inline": True
                },
                {
                    "name": "**라떼봇에 기여해주신 분들 - 코드 부분**",
                    "value": "BGM (Github : khk4912) : 라떼봇의 로그 문제를 해결해 주셨습니다!\n"
                             "라고솔로가말했습니다 (Github : SaidBySolo) : 라떼봇의 코드 안에 잔재하던 오타들을 수정해 주셨습니다!\n",
                    "inline": False
                },
                {
                    "name": "**라떼봇에 기여해주신 분들 - 그래픽 부분**",
                    "value": "Star_Pixeller : 라떼봇의 프로필 이미지를 만들어 주셨습니다!\n",
                    "inline": False
                },
                {
                    "name": "**라떼봇에 기여해주신 분들 - 테스트 부분**",
                    "value": "HOREON : 수많은 테스트를 통해 버그를 찾아내는걸 도와주셨습니다 :D",
                    "inline": False
                }
            ]
        )

        await ctx.send(embed=await embed_factory.build())


def setup(bot: Latte):
    cog = BotInfoCog(bot)
    bot.get_logger().info(
        msg="[BotInfoExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=BotInfoCog.__module__)
    bot.add_cog(cog)
