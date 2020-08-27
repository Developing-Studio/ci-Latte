from typing import Any, Union, Callable, Optional, List, Dict


class ConfigException(Exception):
    """
    Base exception for Config class to indicate errors occured during managing configs.
    """
    def __init__(self, alert: str):
        self.alert = alert

    def __str__(self) -> str:
        return f"[ConfigException] {self.alert}"

    def __repr__(self):
        return self.__str__()


class ConfigNotFound(ConfigException):
    """
    An exception which indicates config file is not found.
    """
    def __init__(self):
        super(ConfigNotFound, self).__init__(alert="Config not found!")

    
class ConfigAlreadyLoaded(ConfigException):
    """
    An exception which indicates config is already loaded, so can`t load again.
    """
    def __init__(self):
        super(ConfigAlreadyLoaded, self).__init__(alert="Config is already loaded!")


class ConfigNotLoaded(ConfigException):
    """
    An exception which indicates config is already unloaded, so can`t unload again.
    """
    def __init__(self):
        super(ConfigNotLoaded, self).__init__(alert="Config is not loaded!")


class ConfigMethodNotSupported(ConfigException):
    """
    An exception which indicates certain config method is not supported on the current config type.
    """
    def __init__(self, method_name: str, config_type):
        super(ConfigMethodNotSupported, self).__init__(alert=f"Config method `{method_name}` is not supported in config type `{config_type}`!")


class Config:
    class Types:
        JSON: str = "file/json"
        TOML: str = "file/toml"
        YML: str = "file/yml"

        @classmethod
        def CHECK(cls, value) -> bool:
            """
            Check type of given value
            :param value: an instance to check if this is a Types enum.
            :return: boolean value which indicates if the given :param value: is a Types enum or not.
            """
            return value in [cls.JSON, cls.TOML, cls.YML]

    config: Optional[Union[Dict[str, Union[Dict[str, Any], int, str, bool]], str]] = None

    def __init__(self, config_type: str, config_dir: str, text_processor: Callable[[str], Any] = lambda x: x):
        # Type Check
        if not self.Types.CHECK(config_type):
            raise TypeError("Config Type must be a Config.Types enum value!")
        self.config_type = config_type
        self.config_dir = config_dir

        if config_type == self.Types.TOML and text_processor is None:
            raise ValueError("`TEXT` type config requires ")
        self.text_processor = text_processor

    def read(self, encoding: str = "utf-8") -> str:
        try:
            print("[Config.read] Opening config file ...")
            with open(
                    file=self.config_dir,
                    mode="rt",
                    encoding=encoding
            ) as config_file:
                print("[Config.read] Reading config file data and return it ...")
                return config_file.read()
        except FileNotFoundError:
            print("[Config.read] Config file does not exist! Raising ConfigNotFound exception...")
            raise ConfigNotFound()

    def process(self, raw_content: str):
        print("[Config.process] Processing config file data ...")
        if self.config_type == self.Types.JSON:
            print("[Config.process] Config type is defined as JSON. Try to load config file data as dictionary ...")
            if type(raw_content) != str:
                print("[Config.process] Processing config file data ...")
                raise ValueError("JSON-type config file must be loaded using string value (text).")
            import json
            return json.loads(raw_content)
        else:
            return self.text_processor(raw_content)

    def load(self):
        print("[Config.load] Loading config ...")
        if not self.is_loaded():
            print("[Config.load] Config is not loaded. Reading & Processing config file ...")
            self.config = self.process(self.read())
            print("[Config.load] Done!")
        else:
            print("[Config.load] Config is already loaded! Raising ConfigAlreadyLoaded exception ...")
            raise ConfigAlreadyLoaded()

    def is_loaded(self) -> bool:
        """
        :return: if the config is loaded
        """
        return self.config is not None

    def write(self, content: str, encoding: str = "utf-8"):
        print("[Config.write] Opening config file as a write-text mode ...")
        try:
            with open(
                    file=self.config_dir,
                    mode="wt",
                    encoding=encoding
            ) as config_file:
                print("[Config.save] Checking config type ...")
                if self.config_type == self.Types.JSON:
                    print("[Config.save] Found JSON type config! Checking type of stored config content ...")
                    if type(self.config) != dict:
                        print("[Config.save] Config should store dictionary type content if it is a JSON type! "
                              "raising TypeError ...")
                        raise TypeError("Type of the config content does not match with config_type attribute!")

                    print("[Config.save] Config contains dictionary content. Dumping dictionary into config file ...")
                    import json
                    json.dump(obj=content, fp=config_file, indent=4, ensure_ascii=False)
                    print("[Config.save] Finished dumping dictionary!")

                else:
                    config_file.write(content)
                print("[Config.save] Finished writing down config into config file!")

        except FileNotFoundError:
            raise ConfigNotFound()

    def save(self):
        print("[Config.save] Writing config content on config file ...")
        self.write(content=self.config)
        print("[Config.save] Successfully wrote config content on config file!")

    def unload(self):
        print("[Config.unload] Unloading config...")
        if self.is_loaded():
            print("[Config.unload] Found loaded config. Saving...")
            self.save()
            print("[Config.unload] Saved loaded config! Clearing config attribute ...")
            self.config = None
            print("[Config.unload] Successfully cleared config attribute!")
        else:
            print("[Config.unload] Cannot found any loaded config. Raising ConfigNotLoaded exception!")
            raise ConfigNotLoaded()

    def reload(self):
        print("[Config.reload] Reloading config...")
        self.unload()
        self.load()
        print("[Config.reload] Successfully reloaded config!")

    def get(self, key_phrase: str) -> Any:
        if self.config_type != self.Types.JSON:
            keys: List[str] = key_phrase.split('.')
            item: Any = self.config[keys[0]]
            for key in keys[1:]:
                item = item[key]
            return item
        else:
            raise ConfigMethodNotSupported(method_name=self.get.__name__, config_type=self.config_type)

    def __getitem__(self, key) -> Any:
        return self.config[key]

