from typing import Dict

from discord.ext import commands
import discord
from core import Latte
from utils import EmbedFactory, get_cog_name_in_ext


class UtilsCog(commands.Cog):
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
        self.bot.get_logger().info(
            msg=f"[UtilsExt.invite_url] bot_invite_url : {bot_invite_url}"
        )
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
        aliases=["유저정보", "ui", "userinfo"],
        description="호출한 유저의 정보를 보여줍니다. [Can be updated]",
        help=""
    )
    async def get_user_info(self, ctx: commands.Context, member: discord.Member = None):
        if member is None:
            member = ctx.author

        # Create an Embed which contains member's information
        caller_info = EmbedFactory.get_command_caller(user=ctx.author)
        embed_factory = EmbedFactory(
            title=f"{EmbedFactory.get_user_info(user=member, contain_id=False)} 님의 정보입니다!",
            color=EmbedFactory.default_color,
            author={
                "name": f"{EmbedFactory.get_user_info(user=self.bot.user, contain_id=True)}",
                "icon_url": self.bot.user.avatar_url
            },
            footer={
                "text": f"{caller_info['text']}",
                "icon_url": f"{caller_info['icon_url']}"
            },
            thumbnail_url=member.avatar_url,
            fields=[
                {
                    "name": "이름",
                    "value": f"{EmbedFactory.get_user_info(user=member, contain_id=False)}",
                    "inline": False
                },
                {
                    "name": "유저 상태",
                    "value": self.status_dict[member.status],
                    "inline": True
                },
                {
                    "name": "Discord 가입 연도",
                    "value": member.created_at,
                    "inline": False
                },
                {
                    "name": "서버 참여 날짜",
                    "value": member.joined_at,
                    "inline": True
                },
                {
                    "name": "모바일 여부",
                    "value": str(member.is_on_mobile()),
                    "inline": True
                }
            ]
        )

        is_nitro: bool = bool(member.premium_since)
        await embed_factory.add_field(name="프리미엄(니트로) 여부", value=str(is_nitro), inline=False)
        if is_nitro:
            await embed_factory.add_field(name="프리미엄 사용 시작 날짜", value=str(member.premium_since), inline=True)
        """
        info_embed.add_field(name='Hypesquad 여부', value=user_profile.hypesquad, inline=False)
        if user_profile.hypesquad:
            info_embed.add_field(name='소속된 Hypesquad house', value=user_profile.hypesquad_houses, inline=True)

        info_embed.add_field(name='메일 인증 사용여부', value=member.verified, inline=False)
        info_embed.add_field(name='2단계 인증 사용여부', value=member.mfa_enabled, inline=True)
        """

        await ctx.send(embed=await embed_factory.build())

    @commands.command(
        name="server-info",
        aliases=["서버정보", "si", "serverinfo"],
        description="명령어가 사용된 서버의 정보를 보여줍니다.",
        help=""
    )
    async def get_server_info(self, ctx: commands.Context):
        # Create an Embed which contains member's information
        caller_info = EmbedFactory.get_command_caller(user=ctx.author)

        # Because discord.py does not provide region "south-korea" but discord api does,
        # we need to request to discord api directly to get proper region info.

        response = await self.bot.api_get(api_url=f"/guilds/{ctx.guild.id}", response_type="json")

        embed_factory = EmbedFactory(
            title=f"{ctx.guild.name} 서버 정보입니다!",
            color=EmbedFactory.default_color,
            author={
                "name": f"{EmbedFactory.get_user_info(user=self.bot.user, contain_id=False)}",
                "icon_url": self.bot.user.avatar_url
            },
            footer={
                "text": f"{caller_info['text']}",
                "icon_url": f"{caller_info['icon_url']}"
            },
            thumbnail_url=ctx.guild.icon_url,
            fields=[
                {
                    "name": "서버 주인",
                    "value": ctx.guild.owner.mention,
                    "inline": False
                },
                {
                    "name": "서버 생성 날짜",
                    "value": str(ctx.guild.created_at),
                    "inline": True
                },
                {
                    "name": "서버 지역",
                    "value": response["region"],
                    "inline": True
                },
                {
                    "name": "서버 멤버 수",
                    "value": str(len(ctx.guild.members)),
                    "inline": False
                },
                {
                    "name": "서버 채널 수",
                    "value": f"total : {len(ctx.guild.channels)} | category : {len(ctx.guild.categories)} | text : {len(ctx.guild.text_channels)} | voice : {len(ctx.guild.voice_channels)}",
                    "inline": True
                },
                {
                    "name": "서버 역할들",
                    "value": str([role.mention for role in ctx.guild.roles]),
                    "inline": False
                }
            ]
        )

        await ctx.send(
            embed=await embed_factory.build(),
            allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False)
        )

    @commands.command(
        name="activity-info",
        description="호출한 유저의 현재 활동정보를 보여줍니다.",
        aliases=["활동정보", "activityinfo", "ai"]
    )
    async def get_user_activity(self, ctx: commands.Context, member: discord.Member = None):
        # Create an Embed which contains member's information
        if member is None:
            member = ctx.author
        caller_info = EmbedFactory.get_command_caller(user=ctx.author)

        embed_factory = EmbedFactory(
            title=f"{member.display_name} 님의 활동 정보입니다!",
            color=EmbedFactory.default_color,
            author={
                "name": f"{EmbedFactory.get_user_info(user=self.bot.user, contain_id=True)}",
                "icon_url": self.bot.user.avatar_url
            },
            footer={
                "text": f"{caller_info['text']}",
                "icon_url": f"{caller_info['icon_url']}"
            },
            thumbnail_url=member.avatar_url
        )

        if len(member.activities) == 0:
            await embed_factory.add_field(name=f"활동 정보가 없습니다!", value="현재 진행중인 활동이 없습니다.", inline=False)
            return await ctx.send(embed=await embed_factory.build())
        else:
            count: int = 1
            for ac in member.activities:
                await embed_factory.add_field(name='\u200b', value='\u200b', inline=False)  # 공백 개행을 만든다.
                self.bot.get_logger().info(
                    msg=f"[UtilsExt.useractivity] 활동 {count} : {type(ac)}, .type = {ac.type}"
                )
                try:
                    await embed_factory.add_field(name=f"**활동 {count} 이름**", value=ac.name, inline=False)
                    if ac.type == discord.ActivityType.playing:
                        await embed_factory.add_field(name=f"활동 {count} 유형", value="플레이 중", inline=False)
                        if type(ac) != discord.Game and ac.large_image_url is not None:
                            await embed_factory.add_field(name="활동 이미지", value='\u200b', inline=False)
                            embed_factory.image_url = ac.large_image_url
                    elif ac.type == discord.ActivityType.streaming:
                        await embed_factory.add_field(name=f"활동 {count} 유형", value="방송 중", inline=False)
                        if type(ac) == discord.Streaming:
                            await embed_factory.add_field(name=f"**방송 정보**", value='\u200b', inline=False)
                            await embed_factory.add_field(name=f"방송 플랫폼", value=ac.platform, inline=False)
                            if ac.twitch_name is not None:
                                await embed_factory.add_field(name=f"트위치 이름", value=ac.twitch_name, inline=True)
                            await embed_factory.add_field(name="방송 주소", value=ac.url, inline=False)
                            if ac.game is not None:
                                await embed_factory.add_field(name="방송중인 게임", value=ac.game, inline=False)

                    elif ac.type == discord.ActivityType.listening:
                        await embed_factory.add_field(name=f"활동 {count} 이름", value=ac.name, inline=False)
                        await embed_factory.add_field(name=f"활동 {count} 유형", value="듣는 중", inline=False)

                    elif ac.type == discord.ActivityType.watching:
                        await embed_factory.add_field(name=f"활동 {count} 이름", value=ac.name, inline=False)
                        await embed_factory.add_field(name=f"활동 {count} 유형", value="시청 중", inline=False)

                    elif ac.type == discord.ActivityType.custom:
                        ac_extra = ''
                        if ac.emoji is not None:
                            ac_extra += ac.emoji.name
                        await embed_factory.add_field(name=f"활동 {count} 이름", value=ac_extra + ac.name, inline=False)
                        await embed_factory.add_field(name=f"활동 {count} 유형", value="사용자 지정 활동", inline=False)

                    elif ac.type == discord.ActivityType.unknown:
                        await embed_factory.add_field(name=f"활동 {count} 이름", value="알 수 없는 활동입니다!", inline=False)
                    else:
                        await embed_factory.add_field(name=f"요청하신 사용자의 활동을 파악하지 못했습니다!", value="유효한 활동 유형이 아닙니다 :(", inline=False)
                except Exception as e:
                    await embed_factory.add_field(name=f"오류 발생!", value="활동 정보를 불러오지 못했습니다 :(", inline=False)
                    await embed_factory.add_field(name=f"오류 내용", value=str(e.with_traceback(e.__traceback__)), inline=False)

                count += 1

        await ctx.send(embed=await embed_factory.build())

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
                }

            ]
        )

        await ctx.send(embed=await embed_factory.build())


def setup(bot: Latte):
    cog = UtilsCog(bot)
    bot.get_logger().info(
        msg="[UtilsExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=UtilsCog.__module__)
    bot.add_cog(cog)
