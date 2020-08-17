from discord.ext import commands
import discord
from core import Latte
from utils import EmbedFactory


class UtilsCog(commands.Cog):

    def __init__(self, bot: Latte):
        self.bot = bot

    # Commands
    @commands.command(
        name="ping",
        aliases=["핑"],
        description="봇의 응답 지연시간을 보여줍니다. 핑퐁!",
        help="`라떼야 핑` "
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
        self.bot.get_logger().info(
            msg=f"[UtilsExt.invite_url] bot_invite_url : {bot_invite_url}"
        )
        await ctx.send(f"> 초대 링크입니다! → {bot_invite_url}")

    @commands.command(
        name="report",
        description="건의사항이나 버그 내용을 메세지로 받아 개발자들에게 전달합니다. 혹은 메세지 없이 사용해 공식 커뮤니티 제보 채널로 연결합니다.",
        aliases=["제보"]
    )
    async def report(self, ctx: commands.Context, report_type='', *, report_content: str = ''):
        print(f"{ctx.message.content}")
        print(f"report_type == {report_type}")
        print(f"report_content == {report_content}")

        if report_type=='' and report_content == '':
            await ctx.send(
                content=f"> 봇 공식 커뮤니티에서 버그를 제보해주세요!\n"
                        f"{self.bot.discord_base_invite + self.bot.bug_report_invite}"
            )
        elif report_content != '' and report_type in ["건의", "버그"]:

            bug_embed_factory = EmbedFactory(
                title=f"{ctx.author.name} 님의 제보입니다!"
            )
            await bug_embed_factory.add_field(name="제보 유형", value=report_type)
            await bug_embed_factory.add_field(name="제보 내용", value=report_content)

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
        name="user-info",
        description="호출한 유저의 정보를 보여줍니다. [Can be updated]",
        aliases=["유저정보", "ui", "userinfo"]
    )
    async def get_user_info(self, ctx: commands.Context, member: discord.Member):
        # Create an Embed which contains member's information
        info_embed: discord.Embed = discord.Embed(
            colour=discord.Colour.blue(),
            author=f'{self.bot.user.name}',
            title=f'{member.display_name}',
            description=f'{member.display_name} 님의 프로필 정보입니다!')
        info_embed.set_thumbnail(url=member.avatar_url)
        info_embed.set_footer(text=f'{ctx.author.name} 님이 요청하셨습니다!', icon_url=ctx.author.avatar_url)

        info_embed.add_field(name="이름", value=f"{member.name}#{member.discriminator}", inline=False)
        info_embed.add_field(name='유저 상태', value=self.status_dict[member.status], inline=True)

        info_embed.add_field(name='Discord 가입 년도', value=member.created_at, inline=False)
        info_embed.add_field(name='서버 참여 날짜', value=member.joined_at, inline=True)

        is_nitro: bool = bool(member.premium_since)
        info_embed.add_field(name='프리미엄(니트로) 여부', value=str(is_nitro), inline=False)
        if is_nitro:
            info_embed.add_field(name='프리미엄 사용 시작 날짜', value=member.premium_since, inline=True)
        """
        info_embed.add_field(name='Hypesquad 여부', value=user_profile.hypesquad, inline=False)
        if user_profile.hypesquad:
            info_embed.add_field(name='소속된 Hypesquad house', value=user_profile.hypesquad_houses, inline=True)

        info_embed.add_field(name='메일 인증 사용여부', value=member.verified, inline=False)
        info_embed.add_field(name='2단계 인증 사용여부', value=member.mfa_enabled, inline=True)
        """
        info_embed.add_field(name='모바일 여부', value=member.is_on_mobile(), inline=False)

        await ctx.send(embed=info_embed)


def setup(bot: Latte):
    bot.add_cog(UtilsCog(bot))
