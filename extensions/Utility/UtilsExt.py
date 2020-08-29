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
        name="user-info",
        aliases=["유저정보", "ui", "userinfo"],
        description="호출한 유저의 정보를 보여줍니다. [Can be updated]",
        help=""
    )
    async def get_user_info(self, ctx: commands.Context, member: discord.Member = None):
        if member is None:
            member = ctx.author

        # Create an Embed which contains member's information
        embed_factory = EmbedFactory(
            title=f"{EmbedFactory.get_user_info(user=member, contain_id=False)} 님의 정보입니다!",
            color=EmbedFactory.default_color,
            author={
                "name": EmbedFactory.get_user_info(user=self.bot.user, contain_id=True),
                "icon_url": self.bot.user.avatar_url
            },
            footer=EmbedFactory.get_command_caller(user=ctx.author),
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
        info_embed.add_field('Hypesquad 여부', user_profile.hypesquad, False)
        if user_profile.hypesquad:
            info_embed.add_field('소속된 Hypesquad house', user_profile.hypesquad_houses, True)

        info_embed.add_field('메일 인증 사용여부', member.verified, False)
        info_embed.add_field('2단계 인증 사용여부', member.mfa_enabled, True)
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
            await embed_factory.add_field(name="활동 정보가 없습니다!", value="현재 진행중인 활동이 없습니다.", inline=False)
            return await ctx.send(embed=await embed_factory.build())
        else:
            count: int = 1
            for ac in member.activities:
                await embed_factory.add_field(name='\u200b', value='\u200b', inline=False)  # 공백 개행을 만든다.
                self.bot.get_logger().info(
                    msg=f"[UtilsExt.useractivity] 활동 {count} : {type(ac)}, .type = {ac.type}"
                )
                try:
                    await embed_factory.add_field(f"**활동 {count} 이름**", ac.name, False)
                    if ac.type == discord.ActivityType.playing:
                        await embed_factory.add_field(f"활동 {count} 유형", "플레이 중", False)
                        if type(ac) != discord.Game and ac.large_image_url is not None:
                            await embed_factory.add_field("활동 이미지", '\u200b', False)
                            embed_factory.image_url = ac.large_image_url
                    elif ac.type == discord.ActivityType.streaming:
                        await embed_factory.add_field(f"활동 {count} 유형", "방송 중", False)
                        if type(ac) == discord.Streaming:
                            await embed_factory.add_field(f"**방송 정보**", '\u200b', False)
                            await embed_factory.add_field(f"방송 플랫폼", ac.platform, False)
                            if ac.twitch_name is not None:
                                await embed_factory.add_field(f"트위치 이름", ac.twitch_name, True)
                            await embed_factory.add_field("방송 주소", ac.url, False)
                            if ac.game is not None:
                                await embed_factory.add_field("방송중인 게임", ac.game, False)

                    elif ac.type == discord.ActivityType.listening:
                        await embed_factory.add_field(f"활동 {count} 이름", ac.name, False)
                        await embed_factory.add_field(f"활동 {count} 유형", "듣는 중", False)

                    elif ac.type == discord.ActivityType.watching:
                        await embed_factory.add_field(f"활동 {count} 이름", ac.name, False)
                        await embed_factory.add_field(f"활동 {count} 유형", "시청 중", False)

                    elif ac.type == discord.ActivityType.custom:
                        ac_extra = ''
                        if ac.emoji is not None:
                            ac_extra += ac.emoji.name
                        await embed_factory.add_field(f"활동 {count} 이름", ac_extra + ac.name, False)
                        await embed_factory.add_field(f"활동 {count} 유형", "사용자 지정 활동", False)

                    elif ac.type == discord.ActivityType.unknown:
                        await embed_factory.add_field(f"활동 {count} 이름", "알 수 없는 활동입니다!", False)
                    else:
                        await embed_factory.add_field(f"요청하신 사용자의 활동을 파악하지 못했습니다!", "유효한 활동 유형이 아닙니다 :(", False)
                except Exception as e:
                    await embed_factory.add_field(f"오류 발생!", "활동 정보를 불러오지 못했습니다 :(", False)
                    await embed_factory.add_field(f"오류 내용", str(e.with_traceback(e.__traceback__)), False)

                count += 1

        await ctx.send(embed=await embed_factory.build())


def setup(bot: Latte):
    cog = UtilsCog(bot)
    bot.get_logger().info(
        msg="[UtilsExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=UtilsCog.__module__)
    bot.add_cog(cog)
