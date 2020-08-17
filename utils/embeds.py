from typing import NoReturn, Dict, List, Any, overload

import discord

from .design_patterns import Factory
from discord import Embed, Colour, User


class EmbedFactory(Factory):

    # Log colors
    default_color: Colour = Colour.from_rgb(236, 202, 179)    # latte color
    warning_color: Colour = Colour.gold()
    error_color: Colour = Colour.red()

    def __init__(self, **attrs):
        self.target_cls = Embed.__class__
        self._title: str = attrs.pop("title") if "title" in attrs.keys() else ""
        self._description: str = attrs.pop("description") if "description" in attrs.keys() else ""
        self._color: Colour = attrs.pop("color") if "color" in attrs.keys() else self.default_color
        self._author: Dict[str, str] = attrs.pop("author") if "author" in attrs.keys() else {"name": "", "icon_url": ""}
        self._footer: Dict[str, str] = attrs.pop("footer") if "footer" in attrs.keys() else {"text": "", "icon_url": ""}
        self._thumbnail_url: str = attrs.pop("thumbnail_url") if "thumbnail_url" in attrs.keys() else ""
        self._image_url: str = attrs.pop("image_url") if "image_url" in attrs.keys() else ""
        self._fields: List[Dict[str, str]] = attrs.pop("fields") if "fields" in attrs.keys() else []

        if attrs:
            raise UnexpectedKwargsError(embed_factory=self)

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
        if isinstance(value, (dict, )):
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
        if isinstance(value, (dict, )):
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
            if not isinstance(item, (dict, )):
                raise ValueError("New field to assign in fields property must be a Dictionary instance"
                                 " contains string key and string value.")
            if "name" not in item.keys() or "value" not in item.keys():
                raise AttributeError("Each field must contain `name` and `value` keys.")

        # Value Assign
        self._fields.extend(value)

    @overload
    async def add_field(self, name: str, value: str):
        if type(name) != str or type(value) != str:
            raise TypeError("Field name and value must be a str!")
        self.fields.append({"name": name, "value": value})

    @overload
    async def add_field(self, field: Dict[str, str]):
        if "name" in field.keys() and "value" in field.keys():
            self.fields.append(field)
        else:
            raise InvalidFieldError(embed_factory=self, invalid_field=field)

    async def add_field(self, any: Any):
        raise NotImplementedError("Unexpected Overloaded method called : EmbedFactory.add_field")

    async def add_fields(self, *fields: Dict[str, str]) -> NoReturn:
        for field in fields:
            if "name" in field.keys() and "value" in field.keys():

                # Instead of appending `field` itself, append values using "name" and "value" key
                # to prevent unexpected key in field.
                await self.add_field(name=field["name"], value=field["value"])
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
            embed.add_field(name=field["name"], value=field["value"])

        if self.footer["text"] != "" and self.footer["icon_url"] != "":
            embed.set_footer(text=self.footer["text"], icon_url=self.footer["icon_url"])

        return embed

    @classmethod
    def get_user_info(cls, user: User) -> str:
        return f"{user.name}#{user.discriminator} ({user.id})"

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
        embed.set_footer(text=f"command executed by {cls.get_user_info(user=user)}", icon_url=user.avatar_url)
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

