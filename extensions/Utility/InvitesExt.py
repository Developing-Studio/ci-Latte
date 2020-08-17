from typing import Type, Dict, List, Tuple
import discord, json, asyncio
from discord.ext import commands
from core import Latte
from utils import EmbedFactory


class InviteCog(commands.Cog):
    def __init__(self, bot: Latte):
        self.bot = bot
        self.invite_tracks: Dict[str, Dict[str, int]] = {}
        try:
            asyncio.wait_for(self.update(), timeout=30)
        except asyncio.TimeoutError as e:
            self.bot.get_logger().error(
                msg="[InvitesExt] Cannot update invites data. Maybe bot is still starting :(",
                exc_info=e
            )
        else:
            print(self.invite_tracks)

    def cog_unload(self):
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Called when the client is done preparing the data received from Discord. Usually after login is successful and the Client.guilds and co. are filled up.
        :return:
        """
        self.invite_tracks = await self.update()
        print("[InvitesExt.update] Updated result (Checking assigned value in class instance.) :\n", json.dumps(self.invite_tracks, ensure_ascii=False, indent=4))

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """
        Event listener for invite_create event, which is dispatched when a new invite instance is created.

        :param guild:
        :return:
        """
        self.bot.get_logger().info(
            msg=f"[InvitesExt.on_guild_join] Latte joined new discord guild : {guild.name}#{guild.id}, updating tracking invites data."
        )
        self.invite_tracks = await self.update()
        self.bot.get_logger().info(
            msg=f"[InvitesExt.on_guild_join] Start tracking invites data of the guild : {guild.name}#{guild.id}"
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """
        Event listener for invite_create event, which is dispatched when a new invite instance is created.

        :param guild:
        :return:
        """
        self.bot.get_logger().info(
            msg=f"[InvitesExt.on_guild_remove] Latte left the discord guild : {guild.name}#{guild.id}, removing information of the guild..."
        )
        self.invite_tracks.pop(str(guild.id))
        self.bot.get_logger().info(
            msg=f"[InvitesExt.on_guild_remove] Removed all tracking invites data of the guild : {guild.name}#{guild.id}"
        )

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        """
        Event listener for invite_create event, which is dispatched when a new invite instance is created.
        :param invite: an invite instance which is created.
        """
        self.bot.get_logger().info(
            msg=f"[InvitesExt.on_invite_create] New invite with code {invite.code} created in guild : {invite.guild.name}#{invite.guild.id}"
        )
        self.invite_tracks[str(invite.guild.id)].update({invite.code: invite.uses})

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        """
        Event listener for invite_delete event, which is dispatched when an invite instance is deleted.
        :param invite: an invite instance which is deleted.
        """
        self.bot.get_logger().info(
            msg=f"[InvitesExt.on_invite_delete] An invite  with code {invite.code} deleted in guild : {invite.guild.name}#{invite.guild.id}"
        )
        self.invite_tracks[invite.guild.id].pop(invite.code)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        Event listener for member_join event, which is dispatched when new member joins the server.
        :param member:  a member who joined in the server.
        """

        used_invite_code, used_count = await self.compare_invites(member.guild)
        log_embed: discord.Embed = EmbedFactory.LOG_EMBED(
            title="새로운 멤버 참가!",
            description=f"{member.display_name} 님은 {used_invite_code} 초대코드를 사용해 서버에 참여했습니다."
        )
        log_embed.add_field(name=f"{used_invite_code}의 현재 사용 횟수 : {used_count}")
        return await member.guild.system_channel.send(log_embed)

    async def update(self) -> Dict[str, Dict[str, int]]:
        self.bot.get_logger().info(
            msg="[InvitesExt.update] Updating tracking invites data..."
        )
        if self.bot.is_ready():
            self.bot.get_logger().info(
                msg="[InvitesExt.update] Bot`s internal cache is ready. Try to update tracking invites data ..."
            )
            invite_tracks: Dict[str, Dict[str, int]] = {}
            for guild in self.bot.guilds:
                invite_tracks[str(guild.id)] = {}
                guild_invites: List[discord.Invite] = await guild.invites()
                for invite in guild_invites:
                    invite_tracks[str(guild.id)].update({invite.code: invite.uses})

            import json
            print("[InvitesExt.update] Updated result (on update method, not assigned to class instance.) :\n", json.dumps(obj=invite_tracks, indent=4, ensure_ascii=False))
            return invite_tracks
        else:
            self.bot.get_logger().error("[InvitesExt.update] Bot`s internal cache is not ready! Cannot load invites...")
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


def setup(bot: Latte):
    bot.add_cog(InviteCog(bot))