from typing import Type, Dict, List, Tuple
import discord, json, asyncio
from discord.ext import commands
from core import Latte
from utils import EmbedFactory


class InviteCog(commands.Cog):
    def __init__(self, bot: Latte):
        self.bot = bot
        self.invite_tracks: Dict[str, Dict[str, int]] = self.update()

    def cog_unload(self):
        pass

    @commands.Cog.listener
    async def on_ready(self):
        """
        Called when the client is done preparing the data received from Discord. Usually after login is successful and the Client.guilds and co. are filled up.
        :return:
        """
        self.update()
        print(json.dumps(self.invite_tracks, ensure_ascii=False, indent=4))

    @commands.Cog.listener
    async def on_invite_create(self, invite: discord.Invite):
        """
        Event listern for invite_create event, which is dispatched when a new invite instance is created.
        :param invite: an invite instance which is created.
        """
        self.invite_tracks[invite.guild.id].update({invite.code: invite.uses})

    @commands.Cog.listener
    async def on_invite_delete(self, invite: discord.Invite):
        """
        Event listern for invite_delete event, which is dispatched when an invite instance is deleted.
        :param invite: an invite instance which is deleted.
        """
        del self.invite_tracks[invite.guild.id][invite.code]

    @commands.Cog.listener
    async def on_member_join(self, member: discord.Member):
        """
        Event listern for member_join event, which is dispatched when new member joins the server.
        :param member:  a member who joined in the server.
        """

        used_invite_code, used_count = await self.compare_invites(member.guild)
        log_embed: discord.Embed = EmbedFactory.LOG_EMBED(
            title="새로운 멤버 참가!",
            desc=f"{member.display_name} 님은 {used_invite_code} 초대코드를 사용해 서버에 참여했습니다."
        )
        log_embed.add_field(name=f"{used_invite_code}의 현재 사용 횟수 : {used_count}")
        return await member.guild.system_channel.send(log_embed)

    def update(self) -> Dict[str, Dict[str, int]]:
        if self.bot.is_ready():
            invite_tracks: Dict[str, Dict[str, int]] = {}
            for guild in self.bot.guilds:
                invite_tracks[guild.id] = {}
                for invite in await guild.invites():
                    invite_tracks[guild.id].update({invite.code: invite.uses})

            import json
            print(json.dumps(obj=invite_tracks, indent=4, ensure_ascii=False))
        else:
            self.bot.logger.error("Bot`s internal cache is not ready! Cannot load invites...")
            return {}

    async def compare_invites(self, guild: discord.Guild) -> Tuple[str, int]:
        """
        Return changed invite instance`s code.
        :param guild:
        :return:
        """
        async for invite in await guild.invites():
            if self.invite_tracks[invite.code] < invite.uses:
                return invite.code, invite.uses


def setup(bot: Type[commands.Bot]):
    bot.add_cog(InviteCog(bot))