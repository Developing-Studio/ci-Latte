from typing import Type, Dict, List, Tuple, Union, overload, Callable, NoReturn, Any, Optional
from discord.ext.commands import Cog
from discord.ext.commands.errors import *
from .exceptions import BadExtArguments

EXT_CONFIG = Dict[str, Union[str, Dict[str, List[Dict[str, str]]]]]
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
            for ext in exts:
                ext_path = f"{base_dir}/{category}/{ext['ext_file']}"
                ext_map[category][ext["ext_name"]] = self.convert_dir(ext_path)

        import json
        print("[ExtensionManager.map] mapped extension_config :\n" + json.dumps(obj=ext_map, indent=4,
                                                                                ensure_ascii=False))
        return ext_map

    def _validate_config(self, extensions_config: EXT_CONFIG) -> bool:
        import json
        print(json.dumps(obj=extensions_config, indent=4, ensure_ascii=False))
        if "base_dir" not in extensions_config.keys() or "extensions" not in extensions_config.keys():
            print("[ExtensionManager.validate] extensions_config must contain keys (base_dir, extensions).")
            return False

        if type(extensions_config["base_dir"]) != str or type(extensions_config["extensions"]) != dict:
            print("[ExtensionManager.validate] extensions_config base_dir, extensions must have a string value.")
            print(type(extensions_config["base_dir"]), type(extensions_config["extensions"]))
            return False

        for category, exts in extensions_config["extensions"].items():
            if type(category) != str or type(exts) != list:
                print(
                    "[ExtensionManager.validate] extensions_config category and exts(List[Dict[str, str]]) must be a string, list.")
                print(type(category), type(exts))
                return False
            for ext in exts:
                if type(ext) != dict:
                    print(
                        "[ExtensionManager.validate] extensions_config extension in exts(List[Dict[str, str]]) must be a dictionary.")
                    print(type(ext))
                    return False
                elif "ext_name" not in ext.keys() or "ext_file" not in ext.keys():
                    print("[ExtensionManager.validate] extensions_config must contain keys (ext_name, ext_file)")
                    print(json.dumps(obj=ext))
                    return False
                elif type(ext["ext_name"]) != str or type(ext["ext_file"]) != str:
                    print(
                        "[ExtensionManager.validate] extensions_config keys (ext_name, ext_file) must contain string values.")

        return True

    def load_ext(self, bot, **options):
        """
        Load extension into bot
        :param bot:
        :param ext_dir:
        :return:
        """

        ext_category, ext_name, ext_dir = self.parse_params(options)

        bot.get_logger().info(
            msg=f"[ExtensionManager.load_ext] loading extension with options :\n ext_category : {ext_category}, ext_name : {ext_name}, ext_dir : {ext_dir}"
        )

        if ext_category == '' and ext_name == '' and ext_dir == '':
            raise BadExtArguments("None of the arguments can be used in loading extension!", ext_category=ext_category,
                                  ext_name=ext_name, ext_dir=ext_dir)

        try:
            if ext_category != '' and ext_name != '':
                self._load_ext_by_name(bot=bot, ext_category=ext_category, ext_name=ext_name)
            elif ext_dir != '':
                bot.load_extension(ext_dir)

        except ExtensionNotFound as e:
            if ext_name != '':
                msg = f"[ExtensionManager.load_ext] Extension name `{ext_name}` not found in extension map. " \
                      f"Are you sure it is included in extension map?"
            else:
                msg = f"[ExtensionManager.load_ext] discord.py extension not found in {ext_dir}!"
            bot.get_logger().error(
                msg=msg,
                exc_info=e
            )
        except ExtensionAlreadyLoaded as e:
            if ext_name != '':
                msg = f"[ExtensionManager.load_ext] Extension `{ext_name}` is already loaded!"
            else:
                msg = f"[ExtensionManager.load_ext] Extension in `{ext_dir}` is already loaded!"
            bot.get_logger().error(
                msg=msg,
                exc_info=e
            )
        except NoEntryPointError as e:
            if ext_name != '':
                msg = f"[ExtensionManager.load_ext] Extension `{ext_name}` does not have setup() function!"
            else:
                msg = f"[ExtensionManager.load_ext] Extension in `{ext_dir}` does not have setup() function!"
            bot.get_logger().error(
                msg=msg,
                exc_info=e
            )
        except ExtensionFailed as e:
            if ext_name != '':
                msg = f"[ExtensionManager.load_ext] Extension `{ext_name}` raised Exception! Maybe in __init__ function?"
            else:
                msg = f"[ExtensionManager.load_ext] Extension in `{ext_dir}` raised Exception! Maybe in __init__ function?"
            bot.get_logger().error(
                msg=msg,
                exc_info=e

            )

        # Does Not catch Exception to except any other exceptions.
        # Exceptions not in try~except clause is critical to bot`s system, so it will not be caught

        bot.get_logger().info(
            msg="[ExtensionManager.load_ext] successfully loaded extension!"
        )

    def _load_ext_by_name(self, bot, ext_category: str, ext_name: str):
        if ext_category not in self.ext_map.keys():
            raise BadExtArguments(f"Given extension category `{ext_category}` does not exist!",
                                  ext_category=ext_category, ext_name=ext_name)
        elif ext_name not in self.ext_map[ext_category].keys():
            raise BadExtArguments(f"Given extension name `{ext_name}` does not exist in category `{ext_name}`!",
                                  ext_category=ext_category, ext_name=ext_name)

        bot.load_extension(self.ext_map[ext_category][ext_name])

    def unload_ext(self, bot, **options):
        """
        Unload extension into bot
        :param bot:
        :param cog_dir:
        :return:
        """

        ext_category, ext_name, ext_dir = self.parse_params(options)

        bot.get_logger().info(
            msg=f"[ExtensionManager.unload_ext] unloading extension with options :\n ext_category : {ext_category}, ext_name : {ext_name}, ext_dir : {ext_dir}"
        )

        if ext_category == '' and ext_name == '' and ext_dir == '':
            raise BadArgument("None of the arguments can be used in loading extension!")

        try:
            if ext_category != '' and ext_name != '':
                self._unload_ext_by_name(bot=bot, ext_category=ext_category, ext_name=ext_name)
            elif ext_dir != '':
                bot.unload_extension(ext_dir)

        except ExtensionNotLoaded as e:
            if ext_name != '':
                msg = f"[ExtensionManager.unload_ext] Extension name `{ext_name}` is not loaded into bot. Are you sure it is already loaded?"
            else:
                msg = f"[ExtensionManager.unload_ext] Extension in {ext_dir} is not loaded into bot. Are you sure it is already loaded?"
            bot.logger.error(
                msg=msg,
                exc_info=e
            )
        # Does Not catch Exception to except any other exceptions.
        # Exceptions not in try~except clause is critical to bot`s system, so it will not be caught

        bot.get_logger().info(
            msg="[ExtensionManager.unload_ext] successfully unloaded extension!"
        )

    def _unload_ext_by_name(self, bot, ext_category: str, ext_name: str):
        if ext_category not in self.ext_map.keys():
            raise BadExtArguments(f"Given extension category `{ext_category}` does not exist!",
                                  ext_category=ext_category, ext_name=ext_name)
        elif ext_name not in self.ext_map[ext_category].keys():
            raise BadExtArguments(f"Given extension name `{ext_name}` does not exist in category `{ext_name}`!",
                                  ext_category=ext_category, ext_name=ext_name)

        bot.unload_extension(self.ext_map[ext_category][ext_name])

    def reload_ext(self, bot, **options):
        """
        Unload extension into bot
        :param bot:
        :param cog_dir:
        :return:
        """

        ext_category, ext_name, ext_dir = self.parse_params(options)

        bot.get_logger().info(
            msg=f"[ExtensionManager.reload_ext] reloading extension with options :\n ext_category : {ext_category}, ext_name : {ext_name}, ext_dir : {ext_dir}"
        )

        if ext_category == '' and ext_name == '' and ext_dir == '':
            raise BadArgument("None of the arguments can be used in loading extension!")

        try:
            if ext_category != '' and ext_name != '':
                self._reload_ext_by_name(bot=bot, ext_category=ext_category, ext_name=ext_name)
            elif ext_dir != '':
                bot.reload_extension(ext_dir)

        except ExtensionNotLoaded as e:
            if ext_name != '':
                msg = f"[ExtensionManager.reload_ext] Extension name `{ext_name}` is not loaded into bot. Are you sure it is already loaded?"
            else:
                msg = f"[ExtensionManager.reload_ext] Extension in {ext_dir} is not loaded into bot. Are you sure it is already loaded?"
            bot.logger.error(
                msg=msg,
                exc_info=e
            )

        except ExtensionNotFound as e:
            if ext_name != '':
                msg = f"[ExtensionManager.reload_ext] Extension name `{ext_name}` not found in extension map. " \
                      f"Are you sure it is included in extension map?"
            else:
                msg = f"[ExtensionManager.reload_ext] discord.py extension not found in {ext_dir}!"
            bot.logger.error(
                msg=msg,
                exc_info=e
            )
        except NoEntryPointError as e:
            if ext_name != '':
                msg = f"[ExtensionManager.reload_ext] Extension `{ext_name}` does not have setup() function!"
            else:
                msg = f"[ExtensionManager.reload_ext] Extension in `{ext_dir}` does not have setup() function!"
            bot.logger.error(
                msg=msg,
                exc_info=e
            )
        except ExtensionFailed as e:
            if ext_name != '':
                msg = f"[ExtensionManager.reload_ext] Extension `{ext_name}` raised Exception! Maybe in __init__ function?"
            else:
                msg = f"[ExtensionManager.reload_ext] Extension in `{ext_dir}` raised Exception! Maybe in __init__ function?"
            bot.logger.error(
                msg=msg,
                exc_info=e

            )

        # Does Not catch Exception to except any other exceptions.
        # Exceptions not in try~except clause is critical to bot`s system, so it will not be caught

        bot.get_logger().info(
            msg="[ExtensionManager.reload_ext] successfully reloaded extension!"
        )

    def _reload_ext_by_name(self, bot, ext_category: str, ext_name: str):
        if ext_category not in self.ext_map.keys():
            raise BadExtArguments(f"Given extension category `{ext_category}` does not exist!",
                                  ext_category=ext_category, ext_name=ext_name)
        elif ext_name not in self.ext_map[ext_category].keys():
            raise BadExtArguments(f"Given extension name `{ext_name}` does not exist in category `{ext_name}`!",
                                  ext_category=ext_category, ext_name=ext_name)

        bot.reload_extension(self.ext_map[ext_category][ext_name])

    def load_all(self, bot):
        bot.get_logger().info(
            msg="[ExtensionManager.load_all] loading all extensions in map..."
        )
        for ext_category, exts in self.ext_map.items():
            print("EXT CATEGORY :", ext_category)
            for ext_name, ext_path in exts.items():
                print("EXT NAME :", ext_name)
                print("EXT PATH :", ext_path)
                self.load_ext(bot=bot, ext_category=ext_category, ext_name=ext_name, ext_dir=ext_path)
        bot.get_logger().info(
            msg="[ExtensionManager.load_all] successfully loaded all extensions in map!"
        )

    def unload_all(self, bot):
        bot.get_logger().info(
            msg="[ExtensionManager.unload_all] unloading all extensions in map..."
        )
        for ext_category, exts in self.ext_map.items():
            print("EXT CATEGORY :", ext_category)
            for ext_name, ext_path in exts.items():
                print("EXT NAME :", ext_name)
                print("EXT PATH :", ext_path)
                if (ext_category == "Dev" and ext_name == "admin") or ext_path == "extensions.Dev.AdminExt":
                    # To load extensions again, we should not unload "Dev.admin" extension
                    # But for some excuses, we should let manual-unload for "Dev.admin" extension can be possible.
                    continue
                self.unload_ext(bot=bot, ext_category=ext_category, ext_name=ext_name, ext_dir=ext_path)
        bot.get_logger().info(
            msg="[ExtensionManager.unload_all] successfully unloaded all extensions in map!"
        )

    def reload_all(self, bot):
        bot.get_logger().info(
            msg="[ExtensionManager.reload_all] reloading all extensions in map..."
        )
        for ext_category, exts in self.ext_map.items():
            print("EXT CATEGORY :", ext_category)
            for ext_name, ext_path in exts.items():
                print("EXT NAME :", ext_name)
                print("EXT PATH :", ext_path)
                self.reload_ext(bot=bot, ext_category=ext_category, ext_name=ext_name, ext_dir=ext_path)
        bot.get_logger().info(
            msg="[ExtensionManager.reload_all] successfully reloaded all extensions in map!"
        )

    def convert_dir(self, dir: str) -> str:
        """
        Convert directory string into python module location string.
        :param dir: normal directory string to convert.
        :return: converted python module location string.
        """
        if dir.startswith('.'):
            dir = dir[1:]
        if dir.startswith('/'):
            dir = dir[1:]
        if ".py" in dir:
            dir = dir.replace(".py", '')
        return dir.replace('/', '.') if '/' in dir else dir

    def parse_params(self, params: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        ext_category: str = params.pop("ext_category") if "ext_category" in params.keys() else ''
        ext_name: str = params.pop("ext_name") if "ext_name" in params.keys() else ''
        ext_dir: str = params.pop("ext_dir") if "ext_dir" in params.keys() else ''
        return ext_category, ext_name, ext_dir
