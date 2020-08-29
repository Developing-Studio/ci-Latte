import asyncio, logging, discord, koreanbots
from .ExtensionManager import ExtensionManager
from .config import *
from .DB import DBWrapper
from typing import List, Tuple, Any, Dict, NoReturn, Callable, Union
from discord.ext.commands import AutoShardedBot


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
    config: Config = None

    # Database
    # TODO : Work on ORM Structure using sqlalchemy & mysql
    db: DBWrapper = None

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
    official_community_invite: str = "taVq6rw"
    bug_report_invite: str = "aC4wngr"

    def __init__(self, test_mode: bool = False, **options):
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

        # Set bot`s test mode
        self.test_mode = test_mode

        # Set discord & bot`s logger
        self._set_logger(discord_level=logging.INFO)
        self.logger = self.get_logger()

        # Initialize bot`s service instance
        # self.service = LatteService(bot=self)

        # Setup bot
        self._setup()
        super(Latte, self).__init__(command_prefix=self.get_guild_prefix, help_command=None, **options)

        self.db = DBWrapper(
            id=self.config["database"]["id"],
            pw=self.config["database"]["pw"],
            host=self.config["database"]["host"],
            port=self.config["database"]["port"]
        )
        self.koreanbot = koreanbots.Client(self, self.config.config["api"]["koreanbots"], postCount=True)

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
        self.config = Config(config_dir=self.bot_config_dir, config_type=Config.Types.JSON)
        self.config.load()

        self.logger.info(msg="[SETUP] Connecting databases.")

        self.logger.info(msg="[SETUP] Preparing ExtensionManager.")
        self.ext = ExtensionManager(extensions_config=self.config["ext"])

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

        self.ext.load_all(bot=self)
        self.db.create_engine()
        # self.lavalink = LavalinkClient(user_id=self.user.id if self.user is not None else self.bot_config["id"])

        self.logger.info(msg="Initialization Phase Finished")

    def _save(self):
        """
        save bot`s datas.
        """
        self.logger.info(msg="Save Phase :")
        self.config.save()

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
            super().run(self.config.config["test"]["token"], *args, **kwargs)

        else:
            super().run(self.config.config["token"], *args, **kwargs)

        # Save Datas
        self._save()

    def check_reboot(self) -> bool:
        return self.do_reboot and self.is_closed()

    def get_logger(self, name="latte") -> logging.Logger:
        """
        Get latte`s logger. Simpler command of `logging.getLogger(name="discord")
        :return: logging.Logger instance which latte uses as logger.
        """
        return logging.getLogger(name=name)

    def _set_logger(self, discord_level=logging.INFO, latte_level=logging.DEBUG):
        """
        Set some options of latte`s loggeer.
        """
        logging.getLogger("discord.gateway").setLevel(logging.WARNING)
        discord_logger = logging.getLogger("discord")
        discord_logger.setLevel(level=discord_level)
        latte_logger = self.get_logger()
        latte_logger.setLevel(level=latte_level)

        # Set console logger

        import sys
        console_handler: logging.Handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
        )
        discord_logger.addHandler(hdlr=console_handler)
        latte_logger.addHandler(hdlr=console_handler)

        from pytz import timezone, utc
        import datetime

        tz = timezone("Asia/Seoul")
        current_dt_KST: datetime.datetime = utc.localize(datetime.datetime.now()).astimezone(tz)
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
        discord_logger.addHandler(hdlr=file_handler)
        latte_logger.addHandler(hdlr=file_handler)

        import os
        log_files: List[str] = sorted(os.listdir("./logs/Latte"))
        if len(log_files) > 7:
            """
            If logs files are stored more than 7, latte will automatically delete logs except recent 7 ones.
            """
            latte_logger.info(msg="Too many logs files are stored! Deleting except recent 7 logs...")
            for log_file in log_files[:len(log_files)-7]:
                latte_logger.info(msg=f"Deleting lof file ./logs/Latte/{log_file}")
                os.remove(path=f'./logs/Latte/{log_file}')

    def get_guild_prefix(self, message: discord.Message) -> List[str]:
        """
        Return guild specific prefix.
        :param message: Message to define command prefix.
        :return: command prefix (List[str] or str)
        """
        # guild_prefix: str = self.db.get(message.guild.id)
        # return guild_prefix
        return self.config["test"]["prefix"] if self.test_mode else self.config["prefix"]

    async def api_get(self, api_url: str, response_type: str = "json") -> Union[Dict[str, Any], str, bytes]:
        import aiohttp
        base_url = "https://discord.com/api"
        if not api_url.startswith('/'):
            raise ValueError("Invalid API url!")

        url = base_url + api_url
        headers: dict = {
            "Authorization": f"Bot {self.config['token']}"
        }
        async with aiohttp.request(method="get", url=url, headers=headers) as response:
            if response_type == "json":
                return await response.json()
            elif response_type == "text":
                return await response.text()
            elif response_type == "bytes":
                return await response.read()
            else:
                raise ValueError("Unexpected respomse type!")

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
        self.get_logger().info(
            msg=f"loaded cogs :"
        )
        for item in self.cogs:
            print(item, ":", self.cogs[item])
