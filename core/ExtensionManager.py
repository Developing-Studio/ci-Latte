from typing import Type, Dict, List, Tuple, Union, overload, Callable, NoReturn
from discord.ext.commands import Cog
from discord.ext.commands.errors import *
from core import Latte


EXT_CONFIG = Dict[str, Union[str, Dict[str, Dict[str, str]]]]
EXT_MAP = Dict[str, Dict[str, str]]


class ExtensionManager:
    ext_map: EXT_MAP
    ext_storage: Dict[str, Type[Cog]]

    def __init__(self, extensions_config: EXT_CONFIG):
        self.ext_map = self.map(extensions_config)

    def map(self, extensions_config: EXT_CONFIG) -> EXT_MAP:
        """
        Process extensions config into category-extension map.
        :param extensions_config: extensions config
        :return: processed category-extension map
        """

        if not self._validate_config(extensions_config):
            raise ValueError("Invalid extension config had been passed, resulted failure in type check.")

        ext_map: Dict[str, Dict[str]] = {}

        base_dir: str = extensions_config["base_dir"]
        if base_dir.endswith('/') or base_dir.endswith('\\'):
            base_dir = base_dir[:-2]

        for category, exts in extensions_config["extensions"].items():
            if category.endswith('/') or category.endswith('\\'):
                category = category[:-2]
            ext_map[category] = {}
            for name, ext_file in exts.items():
                if ext_file.endswith(".py"):
                    ext_file = ext_file.replace(".py", '')
                ext_map[category][name] = f"{base_dir}/{category}/{ext_file}"

        return ext_map

    def _validate_config(self, extensions_config: EXT_CONFIG) -> bool:
        if "base_dir" not in extensions_config.keys() or "extensions" not in extensions_config.keys():
            return False

        if type(extensions_config["base_dir"]) != str or type(extensions_config["extensions"]) != dict:
            return False

        for category, exts in extensions_config["extensions"].items():
            if type(category) != str or type(exts) != dict:
                return False
            for name, dir in exts.items():
                if type(name) != str or type(dir) != str:
                    return False

    def load_ext(self, bot: Latte, **options):
        """
        Load extension into bot
        :param bot:
        :param ext_dir:
        :return:
        """

        ext_category: str = options.pop("ext_category") if "ext_category" in options.keys() else None
        ext_name: str = options.pop("ext_name") if "ext_name" in options.keys() else None
        ext_dir: str = options.pop("ext_dir") if "ext_dir" in options.keys() else None

        if ext_category is None and ext_name is None and ext_dir is None:
            raise BadArgument("None of the arguments can be used in loading extension!")

        try:
            if ext_category is not None and ext_name is not None:
                self._load_ext_by_name(ext_category, ext_name)
            elif ext_dir is not None:
                bot.load_extension(ext_dir)

        except ExtensionNotFound as e:
            if ext_name is not None:
                msg = f"Extension name `{ext_name}` not found in extension map. " \
                      f"Are you sure it is included in extension map?"
            else:
                msg = f"discord.py extension not found in {ext_dir}!"
            bot.logger.error(
                msg=msg,
                exc_info=e
            )
        except ExtensionAlreadyLoaded as e:
            if ext_name is not None:
                msg = f"Extension `{ext_name}` is already loaded!"
            else:
                msg = f"Extension in `{ext_dir}` is already loaded!"
            bot.logger.error(
                msg=msg,
                exc_info=e
            )
        except NoEntryPointError as e:
            if ext_name is not None:
                msg = f"Extension `{ext_name}` does not have setup() function!"
            else:
                msg = f"Extension in `{ext_dir}` does not have setup() function!"
            bot.logger.error(
                msg=msg,
                exc_info=e
            )
        except ExtensionFailed as e:
            if ext_name is not None:
                msg = f"Extension `{ext_name}` raised Exception! Maybe in __init__ function?"
            else:
                msg = f"Extension in `{ext_dir}` raised Exception! Maybe in __init__ function?"
            bot.logger.error(
                msg=msg,
                exc_info=e

            )
        # Does Not catch Exception to except any other exceptions.
        # Exceptions not in try~except clause is critical to bot`s system, so it will not be caught/

    def _load_ext_by_name(self, bot: Latte, ext_category: str, ext_name: str):
        if ext_category not in self.ext_map.keys():
            raise BadArgument(f"Given extension category `{ext_category}` does not exist!")
        elif ext_name not in self.ext_map[ext_category].keys():
            raise BadArgument(f"Given extension name `{ext_name}` does not exist in category `{ext_name}`!")

        bot.load_extension(self.ext_map[ext_category][ext_name])

    def unload_ext(self, bot: Latte, **options):
        """
        Unload extension into bot
        :param bot:
        :param cog_dir:
        :return:
        """

        ext_category: str = options.pop("ext_category") if "ext_category" in options.keys() else None
        ext_name: str = options.pop("ext_name") if "ext_name" in options.keys() else None
        ext_dir: str = options.pop("ext_dir") if "ext_dir" in options.keys() else None

        if ext_category is None and ext_name is None and ext_dir is None:
            raise BadArgument("None of the arguments can be used in loading extension!")

        try:
            if ext_category is not None and ext_name is not None:
                self._unload_ext_by_name(ext_category, ext_name)
            elif ext_dir is not None:
                bot.unload_extension(ext_dir)

        except ExtensionNotLoaded as e:
            if ext_name is not None:
                msg = f"Extension name `{ext_name}` is not loaded into bot. Are you sure it is already loaded?"
            else:
                msg = f"Extension in {ext_dir} is not loaded into bot. Are you sure it is already loaded?"
            bot.logger.error(
                msg=msg,
                exc_info=e
            )
        # Does Not catch Exception to except any other exceptions.
        # Exceptions not in try~except clause is critical to bot`s system, so it will not be caught/

    def _unload_ext_by_name(self, bot: Latte, ext_category: str, ext_name: str):
        if ext_category not in self.ext_map.keys():
            raise BadArgument(f"Given extension category `{ext_category}` does not exist!")
        elif ext_name not in self.ext_map[ext_category].keys():
            raise BadArgument(f"Given extension name `{ext_name}` does not exist in category `{ext_name}`!")

        bot.unload_extension(self.ext_map[ext_category][ext_name])

    def reload_ext(self, bot: Latte, **options):
        """
        Unload extension into bot
        :param bot:
        :param cog_dir:
        :return:
        """

        ext_category: str = options.pop("ext_category") if "ext_category" in options.keys() else None
        ext_name: str = options.pop("ext_name") if "ext_name" in options.keys() else None
        ext_dir: str = options.pop("ext_dir") if "ext_dir" in options.keys() else None

        if ext_category is None and ext_name is None and ext_dir is None:
            raise BadArgument("None of the arguments can be used in loading extension!")

        try:
            if ext_category is not None and ext_name is not None:
                self._reload_ext_by_name(ext_category, ext_name)
            elif ext_dir is not None:
                bot.reload_extension(ext_dir)

        except ExtensionNotLoaded as e:
            if ext_name is not None:
                msg = f"Extension name `{ext_name}` is not loaded into bot. Are you sure it is already loaded?"
            else:
                msg = f"Extension in {ext_dir} is not loaded into bot. Are you sure it is already loaded?"
            bot.logger.error(
                msg=msg,
                exc_info=e
            )

        except ExtensionNotFound as e:
            if ext_name is not None:
                msg = f"Extension name `{ext_name}` not found in extension map. " \
                      f"Are you sure it is included in extension map?"
            else:
                msg = f"discord.py extension not found in {ext_dir}!"
            bot.logger.error(
                msg=msg,
                exc_info=e
            )
        except NoEntryPointError as e:
            if ext_name is not None:
                msg = f"Extension `{ext_name}` does not have setup() function!"
            else:
                msg = f"Extension in `{ext_dir}` does not have setup() function!"
            bot.logger.error(
                msg=msg,
                exc_info=e
            )
        except ExtensionFailed as e:
            if ext_name is not None:
                msg = f"Extension `{ext_name}` raised Exception! Maybe in __init__ function?"
            else:
                msg = f"Extension in `{ext_dir}` raised Exception! Maybe in __init__ function?"
            bot.logger.error(
                msg=msg,
                exc_info=e

            )
        # Does Not catch Exception to except any other exceptions.
        # Exceptions not in try~except clause is critical to bot`s system, so it will not be caught/

    def _reload_ext_by_name(self, bot: Latte, ext_category: str, ext_name: str):
        if ext_category not in self.ext_map.keys():
            raise BadArgument(f"Given extension category `{ext_category}` does not exist!")
        elif ext_name not in self.ext_map[ext_category].keys():
            raise BadArgument(f"Given extension name `{ext_name}` does not exist in category `{ext_name}`!")

        bot.reload_extension(self.ext_map[ext_category][ext_name])

    def load_all(self, bot: Latte):
        for ext_name, ext_dir in self.ext_map.items():
            self.load_ext(bot=bot, ext_dir=ext_dir)

    def unload_all(self, bot: Latte):
        for ext_name, ext_dir in self.ext_map.items():
            self.unload_ext(bot=bot, ext_dir=ext_dir)

    def reload_all(self, bot: Latte):
        for ext_name, ext_dir in self.ext_map.items():
            self.reload_ext(bot=bot, ext_dir=ext_dir)

    def convert_dir(self, dir: str) -> str:
        """
        Convert directory string into python module location string.
        :param dir: normal directory string to convert.
        :return: converted python module location string.
        """

        if dir.startswith('.'):
            dir = dir[1:]

        if ".py" in dir:
            dir = dir.replace(".py", '')

        return dir.replace('/', '.') if '/' in dir else dir
