from discord.ext import commands
import discord, aiohttp, random
from core import Latte
from utils import get_cog_name_in_ext


class AICog(commands.Cog):
    def __init__(self, bot: Latte):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.content in ["라떼야", "라떼"]:
            await msg.channel.send(await self.random_text())

    async def random_text(self) -> str:
        from typing import List
        text_pool: List[str] = [
            "부르셨나요?",
            "네!",
            "라떼에요!",
            "라떼는 말이야...",
            "This Is K-Latte 😎",
            "부르셨습니까 휴먼 🤖"
        ]
        return random.choice(text_pool)


def setup(bot: Latte):
    cog = AICog(bot)
    bot.get_logger().info(
        msg="[GameExt] Injecting key from ext_map matching with module path into cog ..."
            "(To access to cog instance in easier way.)"
    )
    cog.__cog_name__ = get_cog_name_in_ext(ext_map=bot.ext.ext_map, module_path=AICog.__module__)
    bot.add_cog(cog)
