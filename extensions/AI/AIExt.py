from discord.ext import commands
import discord, aiohttp, random
from core import Latte


class AICog(commands.Cog):
    def __init__(self, bot: Latte):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.content in ["라떼야", "라떼"]:
            await msg.channel.send(await self.random_text())
        await self.bot.process_commands(msg)

    async def random_text(self) -> str:
        from typing import List
        text_pool: List[str] = [
            "부르셨나요?",
            "네!",
            "라떼에요!",
            "라떼는 말이야..."
        ]
        return random.choice(text_pool)


def setup(bot: Latte):
    bot.add_cog(AICog(bot))
