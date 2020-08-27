import discord, json, traceback
from discord.ext import commands
from core import Latte, BadExtArguments, Config
from utils import EmbedFactory, get_cog_name_in_ext
from typing import Dict, List, Type


class AdminCog(commands.Cog):

    def __init__(self, bot: Latte):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        command_name: str = f"{ctx.cog.qualified_name if ctx.cog is not None else 'bot'}:{ctx.command.name if ctx.command is not None else 'UNKNOWN'}"
        self.bot.get_logger().info(
            msg=f"[AdminExt.on_command] User {EmbedFactory.get_user_info(user=ctx.author)} used `{command_name}` "
                f"command with following arguments : \n{ctx.args, json.dumps(ctx.kwargs, indent=4, ensure_ascii=False)} "
        )
        if self.bot.config.is_loaded() and self.bot.config.config_type == Config.Types.JSON:
            log_channel: discord.TextChannel = self.bot.get_channel(self.bot.config["admin_log"])
            print(log_channel)
            args = ('\n'.join([f"{arg_num} : {arg}" for arg_num, arg in enumerate(ctx.args)])) if len(
                ctx.args) > 0 else "[]"
            if log_channel is not None:
                owner_info = f"{ctx.guild.owner.name}#{ctx.guild.owner.discriminator}" if ctx.guild.owner is not None else "UNKNOWN"
                await log_channel.send(
                    embed=await EmbedFactory(
                        title="[AdminExt.on_command]",
                        description=f"`{command_name}` 명령어가 사용되었습니다.",
                        author={
                            "name": EmbedFactory.get_user_info(user=self.bot.user, contain_id=True),
                            "icon_url": self.bot.user.avatar_url
                        },
                        footer=EmbedFactory.get_command_caller(ctx.author),
                        color=EmbedFactory.default_color,
                        fields=[
                            {
                                "name": "명령어 파라미터 - 위치 인자 (*args)",
                                "value": args,
                                "inline": False
                            },
                            {
                                "name": "명령어 파라미터 - 키워드 인자 (**kwargs)",
                                "value": json.dumps(ctx.kwargs, indent=4, ensure_ascii=False),
                                "inline": False
                            },
                            {
                                "name": "명령어가 사용된 서버 정보",
                                "value": f"이름 : {ctx.guild.name}\nid : {ctx.guild.id}\n주인 : {owner_info} ({ctx.guild.owner_id})",
                                "inline": False
                            }
                        ]
                    ).build()
                )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Type[Exception]):
        command_name: str = f"{ctx.cog.qualified_name if ctx.cog is not None else 'bot'}:{ctx.command.name if ctx.command is not None else 'UNKNOWN'}"
        self.bot.get_logger().error(
            msg=f"[AdminExt.on_command] User {EmbedFactory.get_user_info(user=ctx.author)} used `{command_name}` "
                f"command with following arguments : \n{ctx.args, json.dumps(ctx.kwargs, indent=4, ensure_ascii=False)}\n"
                f", and error :\n{error}"
        )
        self.bot.get_logger().error(
            msg=f"type of the error : {error}"
        )
        await ctx.channel.send(
            embed=await EmbedFactory(
                title=f"[라떼봇 베타] An error occurred during executing command `{command_name}`\n> {error}"
            ).build()
        )
        if self.bot.config.is_loaded() and self.bot.config.config_type == Config.Types.JSON:
            log_channel: discord.TextChannel = self.bot.get_channel(self.bot.config["admin_log"])
            if log_channel is not None:
                owner_info = f"{ctx.guild.owner.name}#{ctx.guild.owner.discriminator}" if ctx.guild.owner is not None else "UNKNOWN"
                tracebacks: list = traceback.format_exception(type(error.__cause__), error.__cause__, error.__cause__.__traceback__)
                await log_channel.send(
                    content=f"{self.bot.get_user(self.bot.owner_id).mention}",
                    embed=await EmbedFactory(
                        title="[AdminExt.on_command] command error detected",
                        description=f"`{command_name}` 명령어가 사용되었습니다.",
                        color=EmbedFactory.error_color,
                        author={
                            "name": EmbedFactory.get_user_info(user=self.bot.user, contain_id=True),
                            "icon_url": self.bot.user.avatar_url
                        },
                        footer=EmbedFactory.get_command_caller(ctx.author),
                        fields=[
                            {
                                "name": "오류가 발생한 서버 정보",
                                "value": f"이름 : {ctx.guild.name}\nid : {ctx.guild.id}\n주인 : {owner_info} ({ctx.guild.owner_id})"
                            },
                            {
                                "name": "명령어 실행 도중 발생한 오류 정보",
                                "value": "```css\n"
                                         f"{''.join(tracebacks)}\n```"
                            },
                            {
                                "name": "명령어 파라미터 - 위치 인자 (*args)",
                                "value": '\n'.join([f"{arg_num} : {arg}" for arg_num, arg in enumerate(ctx.args)])
                            },
                            {
                                "name": "명령어 파라미터 - 키워드 인자 (**kwargs)",
                                "value": json.dumps(ctx.kwargs, indent=4, ensure_ascii=False)
                            },
                        ]
                    ).build()
                )

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        owner_info = f"{guild.owner.name}#{guild.owner.discriminator}" if guild.owner is not None else "UNKNOWN"
        await self.bot.get_channel(self.bot.config["admin_log"]).send(
            embed=await EmbedFactory(
                title="[EVENT] 라떼봇이 새로운 서버에 참여했습니다!",
                description="event : on_guild_join",
                author={
                    "name": EmbedFactory.get_user_info(user=self.bot.user, contain_id=True),
                    "icon_url": self.bot.user.avatar_url
                },
                footer=EmbedFactory.get_command_caller(guild.owner) if guild.owner is not None else {
                    "text": "UNKNOWN",
                    "icon_url": self.bot.user.avatar_url},
                fields=[
                    {
                        "name": "참여한 서버 정보",
                        "value": f"이름 : {guild.name}\nid : {guild.id}\n주인 : {owner_info} ({guild.owner_id})"
                    }
                ]
            ).build()
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        owner_info = f"{guild.owner.name}#{guild.owner.discriminator}" if guild.owner is not None else "UNKNOWN"
        await self.bot.get_channel(self.bot.config.config["admin_log"]).send(
            embed=await EmbedFactory(
                title="[EVENT] 라떼봇이 서버에서 떠났습니다!",
                description="event : on_guild_remove",
                author={
                    "name": EmbedFactory.get_user_info(user=self.bot.user, contain_id=True),
                    "icon_url": self.bot.user.avatar_url
                },
                footer=EmbedFactory.get_command_caller(guild.owner) if guild.owner is not None else {
                    "text": "UNKNOWN",
                    "icon_url": self.bot.user.avatar_url},
                fields=[
                    {
                        "name": "떠난 서버 정보",
                        "value": f"이름 : {guild.name}\nid : {guild.id}\n주인 : {owner_info} ({guild.owner_id})"
                    }
                ]
            ).build()
        )

    @commands.is_owner()
    @commands.command(
        name="stop",
        aliases=["종료", 's', "shutdown"],
        description="",
        help=""
    )
    async def stop(self, ctx: commands.Context):
        embed = EmbedFactory.COMMAND_LOG_EMBED(
            title="[ Command Result ]",
            description="봇을 종료합니다!",
            user=ctx.author
        )
        await ctx.send(embed=embed)
        self.bot.get_logger().info("[AdminExt] bot stop command detected. stopping bot...")
        self.bot.do_reboot = False
        await self.bot.close()

    @commands.is_owner()
    @commands.command(
        name="restart",
        aliases=["재시작", 'r', "reboot"],
        description="",
        help=""
    )
    async def restart(self, ctx: commands.Context):
        embed = EmbedFactory.COMMAND_LOG_EMBED(
            title="[ Command Result ]",
            description="봇을 재시작합니다!",
            user=ctx.author
        )
        await ctx.send(embed=embed)
        self.bot.get_logger().info("[AdminExt] bot restart command detected. stopping bot...")
        self.bot.do_reboot = True
        await self.bot.close()

    @commands.is_owner()
    @commands.command(
        name="eval",
        aliases=["interprete", "code", "코드"],
        description="evaluate python code. OWNER ONLY!!!"
    )
    async def evaluate_code(self, ctx: commands.Context, *, code_raw: str):
        # Assume that code starts with ```py and endes with ``` (code block)
        if not code_raw.startswith("```py") or not code_raw.endswith("```"):
            raise ValueError("Code to evaluate must starts with ```py and endswith ```")
        code_content: str = code_raw.replace("```", '')[2:]
        try:
            result = eval(code_content)
        except Exception as e:
            result = e
        await ctx.send(
            embed=EmbedFactory.COMMAND_LOG_EMBED(
                title="[ ADMIN COMMAND : EVAL ] 실행 결과",
                description=str(result),
                user=ctx.author
            )
        )

    @commands.is_owner()
    @commands.command(
        name="notice",
        aliases=["공지"],
        description="띄어쓰기 대신 `_`로 띄어쓰기를 표현해주세요. 각 파라미터는 띄어쓰기로 구분됩니다.",
        help="`l;notice` to use."
    )
    async def notice(self, ctx: commands.Context, title: str, desc: str, *, content: str):
        title = title.replace('_', ' ')
        desc = desc.replace('_', ' ')
        embed = await EmbedFactory(
            title=title,
            description=desc,
            author={
                "name": EmbedFactory.get_user_info(self.bot.user, contain_id=False),
                "icon_url": self.bot.user.avatar_url
            },
            footer=EmbedFactory.get_command_caller(ctx.author),
            color=EmbedFactory.default_color,
            fields=[
                {
                    "name": "상세한 내용",
                    "value": content,
                    "inline": False
                }
            ]
        ).build()
        for guild in self.bot.guilds:
            if guild.system_channel is not None:
                await guild.system_channel.send(embed=embed)
            else:
                target_channels: List[discord.TextChannel] = [ch for ch in guild.text_channels if
                                                              ch.topic is not None and "공지" in ch.topic]
                if len(target_channels) > 0:
                    await target_channels[0].send(embed=embed)
                else:
                    from random import choice
                    await choice(guild.text_channels).send(embed=embed)

    @commands.is_owner()
    @commands.group(
        name="extension",
        aliases=["확장", "ext", "모듈", 'm', "module"],
        description="",
        help=""
    )
    async def ext(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:

            fields: List[Dict[str, str]] = []
            for ext_category, exts in self.bot.ext.ext_map.items():
                field: Dict[str, str] = {
                    "name": f"카테고리 {ext_category}"
                }
                value: str = ""
                for ext_name, ext_path in exts.items():
                    value += f"**이름** : {ext_name}\n **경로** : {ext_path}\n\n"
                field["value"] = value
                fields.append(field)

            await ctx.send(
                embed=await EmbedFactory(
                    title="[ Admin Extension - Extension Commands ]",
                    description="This is an admin-only extension to manage Latte`s extensions in discord chat.",
                    color=EmbedFactory.default_color,
                    author={
                        "name": f"라떼봇 v{self.bot.bot_version}",
                        "icon_url": self.bot.user.avatar_url
                    },
                    footer={
                        "text": f"command executed by {EmbedFactory.get_user_info(user=ctx.author)}",
                        "icon_url": ctx.author.avatar_url
                    },
                    fields=fields
                ).build()
            )

    @commands.is_owner()
    @ext.command(
        name="load",
        aliases=["로드", "불러오기"],
        description="",
        help=""
    )
    async def ext_load(self, ctx: commands.Context, *, params_raw: str):
        if params_raw.startswith("all"):
            self.bot.ext.load_all(self.bot)
            return await ctx.send(
                embed=EmbedFactory.COMMAND_LOG_EMBED(
                    title="[ Successfully Unloaded Extension ]",
                    description=f"ext_args : {params_raw}",
                    user=ctx.author
                )
            )
        params = await self.parse_params(params_raw)

        category: str = params.pop("category") if "category" in params.keys() else ''
        name: str = params.pop("name") if "name" in params.keys() else ''
        dir: str = params.pop("dir") if "dir" in params.keys() else ''

        if (dir == '' and (category == '' or name == '')) or ((category == '' and name == '') and dir == ''):
            await ctx.send(
                embed=EmbedFactory.WARN_EMBED(
                    title="Invalid usage!",
                    description="Module commands must be used with cli-style arguments to define module to load!\n"
                                "usage: `ext load -c (category) -n (name)` or `ext load -d (dir)`"
                )
            )
        else:
            try:
                self.bot.ext.load_ext(bot=self.bot, ext_category=category, ext_name=name, ext_dir=dir)
            except BadExtArguments as e:
                error_embed = EmbedFactory.ERROR_EMBED(e)
                await ctx.send(embed=error_embed)
            else:
                result_embed = EmbedFactory.COMMAND_LOG_EMBED(
                    title="[ Successfully Loaded Extension ]",
                    description=f"ext_args : {params_raw}",
                    user=ctx.author
                )
                await ctx.send(embed=result_embed)

                if category == "Utility" and name == "invites":
                    # During reloading / loading module again, InvitesExt extension lose it`s trackin data.
                    # So we need to call update() method and re-track invites data.
                    # But, discord.Guild.invites() method is a coroutine,
                    # it can`t be called in __init__ method while bot is running.
                    # So, we need to call update() method manually right after reloading/loading extension again.
                    await self.bot.get_cog(name).update()

    @commands.is_owner()
    @ext.command(
        name="unload",
        aliases=["언로드", "제거하기"],
        description="",
        help=""
    )
    async def ext_unload(self, ctx: commands.Context, *, params_raw: str):
        if params_raw.startswith("all"):
            self.bot.ext.unload_all(self.bot)
            return await ctx.send(
                embed=EmbedFactory.COMMAND_LOG_EMBED(
                    title="[ Successfully Unloaded Extension ]",
                    description=f"ext_args : {params_raw}",
                    user=ctx.author
                )
            )
        params = await self.parse_params(params_raw)

        category: str = params.pop("category") if "category" in params.keys() else ''
        name: str = params.pop("name") if "name" in params.keys() else ''
        dir: str = params.pop("dir") if "dir" in params.keys() else ''

        if (dir == '' and (category == '' or name == '')) or ((category == '' and name == '') and dir == ''):
            await ctx.send(
                embed=EmbedFactory.WARN_EMBED(
                    title="Invalid usage!",
                    description="Module commands must be used with cli-style arguments to define module to load!\n"
                                "usage: `ext unload -c (category) -n (name)` or `ext unload -d (dir)`"
                )
            )
        else:
            try:
                self.bot.ext.unload_ext(bot=self.bot, ext_category=category, ext_name=name, ext_dir=dir)
            except BadExtArguments as e:
                error_embed = EmbedFactory.ERROR_EMBED(e)
                await ctx.send(embed=error_embed)
            else:
                result_embed = EmbedFactory.COMMAND_LOG_EMBED(
                    title="[ Successfully Unloaded Extension ]",
                    description=f"ext_args : {params_raw}",
                    user=ctx.author
                )
                await ctx.send(embed=result_embed)

    @commands.is_owner()
    @ext.command(
        name="reload",
        aliases=["리로드", "다시불러오기"],
        description="",
        help=""
    )
    async def ext_reload(self, ctx: commands.Context, *, params_raw: str):
        if params_raw.startswith("all"):
            self.bot.ext.reload_all(self.bot)
            return await ctx.send(
                embed=EmbedFactory.COMMAND_LOG_EMBED(
                    title="[ Successfully Reloaded Extension ]",
                    description=f"ext_args : {params_raw}",
                    user=ctx.author
                )
            )
        params = await self.parse_params(params_raw)

        category: str = params.pop("category") if "category" in params.keys() else ''
        name: str = params.pop("name") if "name" in params.keys() else ''
        dir: str = params.pop("dir") if "dir" in params.keys() else ''

        if (dir == '' and (category == '' or name == '')) or ((category == '' and name == '') and dir == ''):
            await ctx.send(
                embed=EmbedFactory.WARN_EMBED(
                    title="Invalid usage!",
                    description="Module commands must be used with cli-style arguments to define module to load!\n"
                                "usage: `ext reload -c (category) -n (name)` or `ext reload -d (dir)`"
                )
            )
        else:
            try:
                self.bot.ext.reload_ext(bot=self.bot, ext_category=category, ext_name=name, ext_dir=dir)
            except BadExtArguments as e:
                error_embed = EmbedFactory.ERROR_EMBED(e)
                await ctx.send(embed=error_embed)
            else:
                result_embed = EmbedFactory.COMMAND_LOG_EMBED(
                    title="[ Successfully Reloaded Extension ]",
                    description=f"ext_args : {params_raw}",
                    user=ctx.author
                )
                await ctx.send(embed=result_embed)

                if category == "Utility" and name == "invites":
                    # During reloading / loading module again, InvitesExt extension lose it`s trackin data.
                    # So we need to call update() method and re-track invites data.
                    # But, discord.Guild.invites() method is a coroutine,
                    # it can`t be called in __init__ method while bot is running.
                    # So, we need to call update() method manually right after reloading/loading extension again.
                    await self.bot.get_cog(name).update()

    async def parse_params(self, params_raw: str) -> Dict[str, str]:
        params = params_raw.split('-')
        print(params)
        parsed: Dict[str, str] = {}
        for param in params:
            if param.startswith('c'):
                # Category param
                parsed["category"] = param[1:].replace(' ', '')
                self.bot.get_logger().info(
                    msg=f"[AdminExt] Caught parameter `category` with value {parsed['category']}"
                )
            elif param.startswith('n'):
                # Name param
                parsed["name"] = param[1:].replace(' ', '')
                self.bot.get_logger().info(
                    msg=f"[AdminExt] Caught parameter `name` with value {parsed['name']}"
                )
            elif param.startswith('d'):
                parsed["dir"] = param[1:].replace(' ', '')
                self.bot.get_logger().info(
                    msg=f"[AdminExt] Caught parameter `dir` with value {parsed['dir']}"
                )
        return parsed


def setup(bot: Latte):
    cog = AdminCog(bot)
    bot.get_logger().info(
        msg="[AdminExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=AdminCog.__module__)
    bot.add_cog(cog)
