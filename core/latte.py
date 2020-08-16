import asyncio
import logging
from core import UserDB, GuildDB, ExtensionManager
from dataclasses import dataclass
from typing import List, Tuple, Any, Dict, NoReturn, Callable, Union
import discord
from discord.ext.commands import AutoShardedBot
import sqlite3


class Config:
    class Types:
        JSON: str = "file/json"
        TEXT: str = "file/text"
        BYTES: str = "file/bites"

        @classmethod
        def CHECK(cls, value) -> bool:
            """
            Check type of given value
            :param value: an instance to check if this is a Types enum.
            :return: boolean value which indicates if the given :param value: is a Types enum or not.
            """
            return value in [cls.JSON, cls.TEXT, cls.BYTES]

    config = None

    def __init__(self, config_type: str, config_dir: str, text_processor: Callable[[str], Any] = None):
        # Type Check
        if not self.Types.CHECK(config_type):
            raise TypeError("Config Type must be a ")
        self.config_type = config_type
        self.config_dir = config_dir

        if config_type == self.Types.TEXT and text_processor is None:
            raise ValueError("`TEXT` type config requires ")
        self.text_processor = text_processor

    def read(self, encoding: str = "utf-8") -> Any:
        with open(
                file=self.config_dir,
                mode='r' + 'b' if self.config_type == self.Types.BYTES else 't',
                encoding=encoding
        ) as config_file:
            return config_file.read()

    def process(self, raw_content: Any):
        if self.config_type == self.Types.JSON:
            if type(raw_content) != str:
                raise ValueError("JSON-type config file must be loaded using string value (text).")
            import json
            return json.loads(raw_content)
        elif self.config_type == self.Types.TEXT:
            return self.text_processor(raw_content)

    def load(self):
        self.config = self.process(self.read())

    def is_loaded(self) -> bool:
        """
        :return: if the config is loaded
        """
        return self.config is not None

    def write(self, content: str, encoding: str = "utf-8"):
        with open(
                file=self.config_dir,
                mode='w' + 'b' if self.config_type == self.Types.BYTES else 't',
                encoding=encoding
        ) as config_file:
            config_file.write(content)

    def save(self):
        self.write(content=str(self.config))


class Latte(AutoShardedBot):
    """
    class Latte:
    class for latte, the discord bot. It extends :class:`discord.ext.commands.AutoShardedBot` to automatically perform sharding.
    This class not only stores several configuration datas, but also add some features into bot
    so developers can develop this bot in convinient ways.
    """

    # Bot Info
    bot_version: str = "1.0.0"

    # Bot Configuration
    bot_config_dir = "./config.json"
    bot_config: Config = Config(config_dir=bot_config_dir, config_type=Config.Types.JSON)

    # Database
    db_dirs: Dict[str, str] = {
        "user": "./DB/users.db",
        "guild": "./DB/guilds.db"
    }
    user_db: UserDB = UserDB(db_dir=db_dirs["user"])
    guild_db: GuildDB = GuildDB(db_dir=db_dirs["guild"])

    # Extensions
    ext: ExtensionManager = None

    # Flags
    test_mode: bool = False  # a flag value which indicates bot`s current mode (release / test)
    do_reboot: bool = False

    # Music Client ( library : lavalink or wavelink )
    # lavalink: LavalinkClient = None
    # lavalink_host: asyncio.subprocess.Process = None
    # lavalink_logger: logging.Logger = logging.getLogger("lavalink-host")

    presence_msg_list: List[str] = []
    discord_base_invite: str = "https://discord.gg/"
    official_community_invite: str = "duYnk96"
    bug_report_invite: str = "t6vVSYX"

    def __init__(self, command_prefix, test_mode: bool = False, **options):
        """
        Initialize `Latte` instance.
        :param test_mode: boolean value which indicates whether latte should run as test mode.
        :param args: arguments which is required to call superclass`s __init__() method.
        :param kwargs: keyword-arguments which is required to call superclass`s __init__() method.
        """
        if "command_prefix" in options.keys():
            options.pop("command_prefix")
        if "help_command" in options.keys():
            options.pop("help_command")
        super().__init__(command_prefix=";", help_command=None, **options)

        # Set bot`s test mode
        self.test_mode = test_mode

        # Set discord & bot`s logger
        self._set_logger(level=logging.INFO)
        self.logger = self.get_logger()

        # Setup bot
        self._setup()
        super().__init__(command_prefix, **options)

    def _opt_out_token(self, args: Tuple[Any], kwargs: Dict[str, Any]) \
            -> Tuple[Tuple[Tuple[Any], ...], Dict[str, Dict[str, Any]]]:
        # Token is provided in Latte Class`s overrided run method, so pop token arg in args/kwargs
        # Argument pass => run(*args, **kwargs)
        # -> start(*args, **kwargs)
        # -> login(token, *, bot=True) & connect(reconnect=reconnect)

        # Keyword arguments :
        # [ bot: bool (run -> start -> login) / reconnect: bool (run -> start -> connect) ]
        # Additional Keyword arguments are not used in run() process, but I want to make it clear taht `token` is not
        # in kwargs.
        if "token" in kwargs.keys():
            kwargs.pop("token")

        # Positional arguments :
        # [ token: str (run -> start -> login) ]
        # We can pop all str args to remove token in positional args,
        # because run() method only require one string arguement, token.
        for arg in args:
            if type(arg) == str:
                del args[args.index(arg)]

        return args, kwargs

    """
    SETUP PHASE
    """

    def _setup(self):
        """
        Setup latte.
        :raise: Exception occured during setup phase
        """
        self.logger.info(msg="[SETUP] Setup Phase Started :")

        self.logger.info(msg="[SETUP] Loading bot config")
        self.bot_config.load()

        self.logger.info(msg="[SETUP] Connecting databases.")
        self.user_db.connect()
        self.guild_db.connect()

        self.logger.info(msg="[SETUP] Preparing ExtensionManager.")
        self.ext = ExtensionManager(extensions_config=self.bot_config.config["ext"])
        self.ext.load_all(bot=self)

        self.logger.info(msg="[SETUP] Setup Phase Finished.")

    def _init(self):
        """
        Initialize latte.
        :raise: Exception occured during initialization phase.
        """
        self.logger.info(msg="Initialization Phase Started :")
        self.event(coro=self.on_ready)
        self.presence_msg_list: List[str] = [
            "'라떼야 도움말' 로 라떼봇을 이용해보세요!",
            "라떼봇은 라떼를 좋아하는 개발자가 개발했습니다 :P",
            "라떼봇 개발자 : sleepylapis#1608",
            "라떼봇은 현재 개발중입니다!",
            "버그 제보는 언제나 환영이에요 :D"
        ]

        # self.lavalink = LavalinkClient(user_id=self.user.id if self.user is not None else self.bot_config["id"])

        self.logger.info(msg="Initialization Phase Finished")

    async def _save(self):
        """
        save bot`s datas.
        """
        self.logger.info(msg="Save Phase :")
        self.bot_config.save()

    def run(self, *args, **kwargs):
        """
        Run latte.
        :param args: arguments which is required to call superclass`s run() method.
        :param kwargs: keyword-arguments which is required to call superclass`s run() method.
        """

        args, kwargs = self._opt_out_token(args, kwargs)

        # Initialize Bot
        self._init()

        # Start Lavalink server
        # self.lavalink_host: subprocess.Popen = subprocess.Popen("java -jar Lavalink.jar")

        # Run bot using Super-class (discord.ext.commands.AutoSharedBot).
        if self.test_mode:
            self.command_prefix = self.bot_config["test"]["prefix"]
            super().run(self.bot_config["test"]["token"], *args, **kwargs)

        else:
            self.command_prefix = self.bot_config["prefix"]
            super().run(self.bot_config["token"], *args, **kwargs)

        # Save Datas
        self._save()

    def get_logger(self) -> logging.Logger:
        """
        Get latte`s logger. Simpler command of `logging.getLogger(name="discord")
        :return: logging.Logger instance which latte uses as logger.
        """
        return logging.getLogger(name="discord")

    def _set_logger(self, level=logging.INFO):
        """
        Set some options of latte`s loggeer.
        """
        logging.getLogger("discord.gateway").setLevel(logging.WARNING)
        logger: logging.Logger = self.get_logger()
        logger.setLevel(level=level)

        import sys
        console_handler: logging.Handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(hdlr=console_handler)

        from pytz import timezone, utc
        import datetime

        KST = timezone("Asia/Seoul")
        current_dt_KST: datetime.datetime = utc.localize(datetime.datetime.now()).astimezone(KST)
        current_dt_KST_month: str = '0' + (
            str(current_dt_KST.month) if (0 < current_dt_KST.month < 10) else str(current_dt_KST.month)
        )
        log_filedir = f"./logs/Latte/{current_dt_KST.tzname()}%"
        log_filedir += f"{current_dt_KST.year}-{current_dt_KST_month}-{current_dt_KST.day}%"
        log_filedir += f"{current_dt_KST.hour}-{current_dt_KST.minute}-{current_dt_KST.second}.txt"
        file_handler: logging.Handler = logging.FileHandler(filename=log_filedir, mode="x", encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(hdlr=file_handler)

        import os
        log_files: List[str] = os.listdir("./logs/Latte")
        if len(log_files) > 7:
            """
            If logs files are stored more than 7, latte will automatically delete logs except recent 7 ones.
            """
            logger.info(msg="Too many logs files are stored! Deleting except recent 7 logs...")
            for log_file in sorted(log_files, reverse=True)[7:]:
                logger.info(msg=f"Deleting lof file ./logs/Latte/{log_file}")
                os.remove(path=f'./logs/Latte/{log_file}')

    async def presence_loop(self):
        """
        Change bot`s presence info using asyncio event loop
        """
        await self.wait_until_ready()
        while not self.is_closed():
            import random
            msg: str = random.choice(self.presence_msg_list)
            # 봇이 플레이중인 게임을 설정할 수 있습니다.
            await self.change_presence(
                status=discord.Status.online, activity=discord.Game(name=msg, type=1)
            )
            await asyncio.sleep(30)

    async def on_ready(self):
        """
        event listener for latte`s on_ready event.
        """
        self.logger.info("라떼봇 온라인!")

        # 봇의 상태메세지를 지속적으로 변경합니다.
        self.loop.create_task(self.presence_loop())
