import discord, logging, aiohttp, json
from discord.ext import commands
from xml.etree.ElementTree import Element, ElementTree, fromstring
from typing import List, Optional, Mapping, Dict, Tuple
from core import Latte
from utils import get_cog_name_in_ext, EmbedFactory
from .SearchAPIExceptions import *


class NaverSearch:
    client_id: str = ""
    client_secret: str = ""
    # request url base.
    # supported search types : [
    #   blog, -> https://developers.naver.com/docs/search/blog
    #   news, -> https://developers.naver.com/docs/search/news
    #   book, -> https://developers.naver.com/docs/search/book
    #   adult, -> https://developers.naver.com/docs/search/adult
    #   encyc, -> https://developers.naver.com/docs/search/encyclopedia
    #   movie, -> https://developers.naver.com/docs/search/movie
    #   cafearticle, -> https://developers.naver.com/docs/search/cafearticle
    #   kin, -> https://developers.naver.com/docs/search/kin
    #   local, -> https://developers.naver.com/docs/search/local
    #   webkr, -> https://developers.naver.com/docs/search/web
    #   image, -> https://developers.naver.com/docs/search/image
    #   shop, -> https://developers.naver.com/docs/search/shopping
    #   doc -> https://developers.naver.com/docs/search/doc
    # ]
    supported_categories: Dict[str, Tuple[str]] = {
        "blog": ("xml", "json"),
        "news": ("xml", "json"),
        "book": ("xml", "json"),
        "book_adv": ("json"),
        "adult": ("xml", "json"),
        "encyc": ("xml", "json"),
        "movie": ("xml", "json"),
        "cafearticle": ("xml", "json"),
        "kin": ("xml", "json"),
        "local": ("xml", "json"),
        "webkr": ("xml", "json"),
        "image": ("xml", "json"),
        "shop": ("xml", "json"),
        "doc": ("xml", "json")
    }
    category_map: Dict[Tuple[str], str] = {
        ("블로그", "blog"): "blog",
        ("뉴스", "news"): "news",
        ("도서", "책", "서적", "book"): "book",
        ("도서상세", "책상세", "서적상세", "book_adv"): "book_adv",
        ("성인여부", "adult"): "adult",
        ("백과", "백과사전", "encyc"): "encyc",
        ("영화", "movie"): "movie",
        ("카페", "카페글", "cafearticle"): "cafearticle",
        ("지식인", "지식in", "지식iN", "kin"): "kin",
        ("지역", "local"): "local",
        ("웹문서", "웹사이트", "webkr"): "webkr",
        ("이미지", "사진", "image"): "image",
        ("쇼핑", "shop"): "shop",
        ("전문자료", "doc"): "doc"

    }
    request_url_base: str = "https://openapi.naver.com/v1/search"
    logger: logging.Logger = logging.getLogger("Latte.NaverSearch")
    logger.setLevel(logging.DEBUG)
    import sys
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
    )
    logger.addHandler(handler)

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    async def search(self, category: str, query: str, response_format: str = "xml", count: int = 3) -> Optional[dict]:
        """
        Try HTTP "GET" request to Naver Search API and return the response in processed dictionary.
        :param category: Category value of the Naver Search API
        :param query: Query text to search
        :param response_format: Response format to retrieve from Naver Search API
        :param count: How many results do you want to retrieve?
        :return: Dictionary value which contains processed data of the response
        """
        for category_tuple in self.category_map:
            if category in category_tuple:
                category = self.category_map[category_tuple]
        if category not in self.supported_categories.keys():
            self.logger.error(msg=f"Category {category} is not supported in Naver Search API!")
            raise NaverSearch_CategoryNotSupported(query=query, category=category, response_format=response_format)
        if response_format not in self.supported_categories[category]:
            self.logger.error(msg=f"Response format {response_format} is not supported in category {category}!")
            raise NaverSearch_CategoryNotSupported(query=query, category=category, response_format=response_format)

        async with aiohttp.ClientSession() as session:
            headers: Mapping[str, str] = {"X-Naver-Client-Id": f"{self.client_id}",
                                          "X-Naver-Client-Secret": f"{self.client_secret}"}
            async with session.request(method="GET",
                                       url=f"{self.request_url_base}/{category}.{response_format}?query={query}&display={count}",
                                       headers=headers) as response:
                response_str: str = await response.text(encoding="utf-8")
                self.logger.debug(msg=f"response_str = {response_str}")
                if response_format == "xml":
                    parsed_response: Element = ElementTree(fromstring(response_str)).getroot()
                    parsed_items: List[Optional[Element]] = parsed_response.find("channel").findall("item")

                    total_result = {}
                    if len(parsed_items) > 0:
                        for item in parsed_items:
                            item_result = {
                                "title": await self.parse_content(item=item, tag="title"),
                                "link": await self.parse_content(item=item, tag="link"),
                                "description": await self.parse_content(item=item, tag="description")
                            }
                            if category == "blog":
                                item_result["postdate"] = await self.parse_content(item=item, tag="postdate")
                                item_result["author"] = await self.parse_content(item=item, tag="bloggername")
                            elif category == "cafearticle":
                                item_result["cafename"] = await self.parse_content(item=item, tag="cafename")
                                item_result["cafeurl"] = await self.parse_content(item=item, tag="cafeurl")

                            total_result[item_result["title"]] = item_result
                    else:
                        total_result = {"result":"No Search Result"}
                    return total_result

                elif response_format == "json":
                    content: dict = await response.json(encoding="utf-8")
                    self.logger.debug(msg=f"final parsed response = {json.dumps(obj=content, indent=4, ensure_ascii=False)}")

    async def parse_content(self, item: Element, tag: str):
        return ("".join(list(item.find(tag).itertext()))).replace("<b>", '__**').replace("</b>", '**__').replace("&quot;", '"')


class GoogleSearch:
    def __init__(self):
        pass

    async def search(self, query: str, response_format: str = "json") -> dict:
        pass


class SearchAPICog(commands.Cog):
    def __init__(self, bot: Latte):
        self.bot: Latte = bot
        self.naverSearch = NaverSearch(
            client_id=bot.config["api"]["naver"]["client_id"],
            client_secret=bot.config["api"]["naver"]["client_secret"]
        )
        self.googleSearch = GoogleSearch()
        self.bot.logger.info("[SearchAPIExt.init] SearchAPI module have been initialized.")

    def cog_unload(self):
        self.bot.logger.info("[SearchAPIExt.unload] SearchAPI module have been unloaded.")

    @commands.group(
        name="search",
        aliases=["검색"],
        description="검색엔진 API를 활용해 검색 결과를 반환합니다.",
        help=""
    )
    async def search(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            return

    @search.command(
        name="naver",
        aliases=["네이버"],
        description="네이버 검색엔진 API를 활용해 검색 결과를 반환합니다.",
        help=""
    )
    async def search_naver(self, ctx: commands.Context, category: str, count: int = 3, *, query: str):
        if count <= 0:
            count = 3
        result: dict = await self.naverSearch.search(category=category, query=query, response_format="xml", count=count)

        search_embeds: List[discord.Embed] = []
        for item in result.values():
            fields: List[Dict[str, str]] = [
                {
                    "name": "글 제목",
                    "value": item["title"]
                },
                {
                    "name": "글 내용",
                    "value": item["description"]
                },
                {
                    "name": "글 바로가기",
                    "value": f"[클릭]({item['link']})"
                }
            ]
            if category == "blog":
                fields.extend([
                    {
                        "name": "글 작성자",
                        "value": item["author"]
                    },
                    {
                        "name": "글 작성 일자",
                        "value": item["postdate"]
                    }
                ])
            elif category == "cafearticle":
                fields.extend([
                    {
                        "name": "카페 이름",
                        "value": item["cafename"]
                    },
                    {
                        "name": "카페 바로가기",
                        "value": f"[클릭]({item['cafeurl']})"
                    }
                ])

            caller_info = EmbedFactory.get_command_caller(user=ctx.author)
            search_embeds.append(
                await EmbedFactory(
                    title=f"네이버 검색 결과입니다!",
                    description=f"검색어 : {query}",
                    author={
                        "name": f"{EmbedFactory.get_user_info(user=self.bot.user, contain_id=True)}",
                        "icon_url": self.bot.user.avatar_url
                    },
                    footer={
                        "text": f"{caller_info['text']}",
                        "icon_url": f"{caller_info['icon_url']}"
                    },
                    thumbnail_url=item["link"],
                    fields=fields
                ).build()
            )
        if len(search_embeds) > 0:
            for embed in search_embeds:
                await ctx.send(embed=embed)

    @search_naver.error
    async def on_search_neaver_error(self, ctx: commands.Context, error: Exception):
        pass

    @search.command(
        name="google",
        aliases=["구글"],
        description="구글 검색엔진 API를 활용해 검색 결과를 반환합니다.",
        help=""
    )
    async def search_google(self, ctx: commands.Context, category: str, *, query: str):
        result: dict = await self.googleSearch.search(query=query, response_format="xml")

    @search_google.error
    async def on_search_google_error(self, ctx: commands.Context, error: Exception):
        pass


def setup(bot: Latte):
    cog = SearchAPICog(bot)
    bot.get_logger().info(
        msg="[SearchAPIExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=SearchAPICog.__module__)
    bot.add_cog(cog)
