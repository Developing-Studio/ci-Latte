from typing import NoReturn, Dict, List, Any, overload, Tuple, Union, Optional
import discord, re
from .design_patterns import Factory
from discord import Embed, Colour, User


class EmbedCheck:
    @staticmethod
    def check_title(value) -> bool:
        return type(value) == str

    @staticmethod
    def check_desc(value) -> bool:
        return type(value) == str

    @staticmethod
    def check_color(value) -> bool:
        return isinstance(value, (Colour,))

    @staticmethod
    def check_author(value) -> bool:
        return type(value) == dict and "name" in value and "icon_url" in value

    @staticmethod
    def check_footer(value) -> bool:
        return type(value) == dict and "text" in value and "icon_url" in value

    @staticmethod
    def check_url(value) -> bool:
        return type(value) == str and re.compile(r"http").match(value)

    @staticmethod
    def check_fields(value) -> bool:
        return type(value) == list and [type(item) for item in value] == [dict] * len(value) \
               and [("name" in item and "value" in item) for item in value] == [True] * len(value)


class EmbedFactory(Factory):
    # Log colors
    default_color: Colour = Colour.from_rgb(236, 202, 179)  # latte color
    warning_color: Colour = Colour.gold()
    error_color: Colour = Colour.red()

    def __init__(self, **attrs):
        self.target_cls = Embed.__class__
        self._title: str = attrs.pop("title") if "title" in attrs.keys() and EmbedCheck.check_title(
            attrs["title"]) else ""
        self._description: str = attrs.pop("description") if "description" in attrs.keys() and EmbedCheck.check_desc(
            attrs["description"]) else ""
        self._color: Colour = attrs.pop("color") if "color" in attrs.keys() and EmbedCheck.check_color(
            attrs["color"]) else self.default_color
        self._author: Dict[str, str] = attrs.pop("author") if "author" in attrs.keys() and EmbedCheck.check_author(
            attrs["author"]) else {"name": "", "icon_url": ""}
        self._footer: Dict[str, str] = attrs.pop("footer") if "footer" in attrs.keys() and EmbedCheck.check_footer(
            attrs["footer"]) else {"text": "", "icon_url": ""}
        # self._thumbnail_url: str = attrs.pop("thumbnail_url") if "thumbnail_url" in attrs.keys() and EmbedCheck.check_url(attrs["thumbnail_url"]) else ""
        self._thumbnail_url: str = attrs.pop("thumbnail_url") if "thumbnail_url" in attrs.keys() else ""
        self._image_url: str = attrs.pop("image_url") if "image_url" in attrs.keys() and EmbedCheck.check_url(
            attrs["image_url"]) else ""
        self._fields: List[Dict[str, str]] = attrs.pop(
            "fields") if "fields" in attrs.keys() and EmbedCheck.check_fields(attrs["fields"]) else []

        print(attrs)

        if attrs:
            raise UnexpectedKwargsError(embed_factory=self, unexpected_kwargs=attrs)

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> NoReturn:
        # Type Check & Value Assign
        self._title = value if type(value) == str else str(value)

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> NoReturn:
        # Type Check & Value Assign
        self._description = value if type(value) == str else str(value)

    @property
    def color(self) -> Colour:
        return self._color

    @color.setter
    def color(self, value: Colour) -> NoReturn:
        # Type Check
        if isinstance(value, (Colour,)):
            # Value Assign
            self._color = value
        else:
            raise InvalidColorError(embed_factory=self)

    @property
    def author(self) -> Dict[str, str]:
        return self._author

    @author.setter
    def author(self, value: Dict[str, str]) -> NoReturn:
        # Type Check
        if isinstance(value, (dict,)):
            TypeError("New data must be a dictionary which contains string keys and string values.")

        # Attribute Check
        if not ("name" in value.keys() and "icon_url" in value.keys()):
            raise AttributeError(f"Invalid data is passed in author property. : {value}")

        # Value Assign
        self._author = {"name": value["name"],
                        "icon_url": value["icon_url"]}

    @property
    def footer(self) -> Dict[str, str]:
        return self._footer

    @footer.setter
    def footer(self, value: Dict[str, str]) -> NoReturn:
        # Type Check
        if isinstance(value, (dict,)):
            TypeError("New data must be a dictionary which contains string keys and string values.")

        # Attribute Check
        if not ("text" in value.keys() and "icon_url" in value.keys()):
            raise AttributeError(f"Invalid data is passed in footer property. : {value}")

        # Value Assign
        self._author = {"text": value["text"],
                        "icon_url": value["icon_url"]}

    @property
    def thumbnail_url(self) -> str:
        return self._thumbnail_url

    @thumbnail_url.setter
    def thumbnail_url(self, value: str) -> NoReturn:
        # Type Check & Value Assign
        self._thumbnail_url = value if type(value) == str else str(value)

    @property
    def image_url(self) -> str:
        return self._image_url

    @image_url.setter
    def image_url(self, value: str) -> NoReturn:
        # Type Check & Value Assign
        self._image_url = value if type(value) == str else str(value)

    @property
    def fields(self) -> list:
        return self._fields

    @fields.setter
    def fields(self, value: List[Dict[str, str]]) -> NoReturn:
        # Type Check
        if not isinstance(value, (list, tuple)):
            raise TypeError("New data to assign fields property must be a list or tuple instance.")

        for item in value:
            if not isinstance(item, (dict,)):
                raise ValueError("New field to assign in fields property must be a Dictionary instance"
                                 " contains string key and string value.")
            if "name" not in item.keys() or "value" not in item.keys():
                raise AttributeError("Each field must contain `name` and `value` keys.")

        # Value Assign
        self._fields.extend(value)

    # @overload
    # async def add_field(self, args: Tuple[str, str, bool]):
    #     name = args[0]
    #     value = args[1]
    #     inline = args[2]
    #     if type(name) != str or type(value) != str or type(inline) != bool:
    #         raise TypeError("Invalid type of parameter was passed in method : "
    #                         "EmbedFactory.add_field(Tuple[str, str, bool]")
    #     self.fields.append({"name": name, "value": value, "inline": inline})
    #
    # @overload
    # async def add_field(self, field: Dict[str, Union[str, bool]]):
    #     if "name" in field.keys() and "value" in field.keys():
    #         self.fields.append(field)
    #     else:
    #         raise InvalidFieldError(embed_factory=self, invalid_field=field)
    #
    # async def add_field(self, any: Any):
    #     print(f"Passed arguments :\n{any}")
    #     raise NotImplementedError("Unexpected Overloaded method called : "
    #                               "EmbedFactory.add_field(any)")

    async def add_field(self, name: str, value: str, inline: bool = False):
        if type(name) != str or type(value) != str or type(inline) != bool:
            raise TypeError("Invalid type of parameter was passed in method : "
                            "EmbedFactory.add_field(Tuple[str, str, bool]")
        self.fields.append({"name": name, "value": value, "inline": inline})

    async def add_fields(self, *fields: Dict[str, Union[str, bool]]) -> NoReturn:
        for field in fields:
            if "name" in field.keys() and "value" in field.keys():

                # Instead of appending `field` itself, append values using "name" and "value" key
                # to prevent unexpected key in field.
                await self.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field["inline"] if "inline" in field.keys() else False
                )
            else:
                raise InvalidFieldError(embed_factory=self, invalid_field=field)

    async def build(self) -> Embed:
        embed = Embed(
            title=self.title,
            description=self.description,
            color=self.color
        )

        if self.thumbnail_url != "":
            embed.set_thumbnail(url=self.thumbnail_url)

        if self.image_url != "":
            embed.set_image(url=self.image_url)

        if self.author["name"] != "" and self.author["icon_url"] != "":
            embed.set_author(name=self.author["name"], icon_url=self.author["icon_url"])

        for field in self.fields:
            embed.add_field(name=field["name"], value=field["value"],
                            inline=bool(field["inline"]) if "inline" in field else False)

        if self.footer["text"] != "" and self.footer["icon_url"] != "":
            embed.set_footer(text=self.footer["text"], icon_url=self.footer["icon_url"])

        return embed

    @classmethod
    def get_user_info(cls, user: User, contain_id: bool = True) -> Optional[str]:
        if user is None:
            return None
        return f"{user.name}#{user.discriminator}" + f" ({user.id})" if contain_id else ''

    @classmethod
    def get_command_caller(cls, user: User) -> Dict[str, str]:
        return {
            "text": f"command executed by {cls.get_user_info(user=user)}",
            "icon_url": user.avatar_url
        }

    @classmethod
    def LOG_EMBED(cls, title: str, description: str) -> Embed:
        return Embed(
            title=title,
            description=description,
            colour=cls.default_color
        )

    @classmethod
    def COMMAND_LOG_EMBED(cls, title: str, description: str, user: discord.User) -> Embed:
        embed = cls.LOG_EMBED(title=title, description=description)
        command_caller_info: Dict[str, str] = cls.get_command_caller(user)
        embed.set_footer(text=command_caller_info["text"], icon_url=command_caller_info["icon_url"])
        return embed

    @classmethod
    def WARN_EMBED(cls, title: str, description: str) -> Embed:
        return Embed(
            title=title,
            description=description,
            colour=cls.error_color
        )

    @classmethod
    def ERROR_EMBED(cls, e: Exception) -> Embed:
        return Embed(
            title="오류가 발생했습니다!",
            description=f"Error content : \n{e.with_traceback(e.__traceback__)}",
            colour=cls.error_color
        )


class EmbedFactoryException(Exception):
    @property
    def msg(self) -> str:
        return self._msg

    @property
    def embed_factory(self) -> EmbedFactory:
        return self._embed_factory

    def __init__(self, embed_factory, *args, **kwargs):
        self._embed_factory = embed_factory
        self._e = kwargs.pop("exception") if "exception" in kwargs.keys() else None
        self._msg = kwargs.pop("msg") if "msg" in kwargs.keys() \
            else "An exception was occurred during EmbedFactory operations."
        super().__init__(*args)

    def __str__(self) -> str:
        return self.msg

    def __repr__(self) -> str:
        return self.__str__()


class UnexpectedKwargsError(EmbedFactoryException):
    def __init__(self, embed_factory: EmbedFactory, unexpected_kwargs: Dict[str, Any], *args, **kwargs):
        if "msg" in kwargs.keys():
            kwargs.pop("msg")
        self.kwargs = unexpected_kwargs
        import json
        msg = f"`EmbedFactory.__init__()` caught unexpected keyword arguments! : {json.dumps(obj=self.kwargs, indent=4, ensure_ascii=False)}"
        super().__init__(embed_factory, *args, msg=msg, **kwargs)


class InvalidColorError(EmbedFactoryException):
    def __init__(self, embed_factory, invalid_color, *args, **kwargs):
        self.color = invalid_color
        if "msg" in kwargs.keys():
            kwargs.pop("msg")
        super().__init__(
            embed_factory,
            *args,
            msg="Embed color must be an instance of `discord.Colour`! : ",
            **kwargs
        )


class InvalidFieldError(EmbedFactoryException):
    def __init__(self, embed_factory, invalid_field, *args, **kwargs):
        self.field = invalid_field
        if "msg" in kwargs.keys():
            kwargs.pop("msg")
        super().__init__(embed_factory, *args,
                         msg="Embed field must have structure of `{'name': name, 'value': value}`",
                         **kwargs)
