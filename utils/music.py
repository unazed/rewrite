from discord.ext import commands

from utils.exceptions import CustomCheckFailure
from .visual import WARNING
from .DB.db import SettingsDB


def music_check(**kwargs):
    in_channel = kwargs.pop("in_channel", False)
    playing = kwargs.pop("playing", False)
    is_dj = kwargs.pop("is_dj", False)
    guild_only = kwargs.pop("guild_only", True)

    async def predicate(ctx):
        if guild_only and not ctx.guild:
            raise CustomCheckFailure(f"{WARNING} This command is guild only")

        settings = await SettingsDB.get_instance().get_guild_settings(ctx.guild.id)
        vc = ctx.guild.get_channel(settings.voiceId)
        tc = ctx.guild.get_channel(settings.textId)
        dj = ctx.guild.get_channel(settings.djroleId)

        if vc and ctx.author.voice.channel != vc:
            raise CustomCheckFailure(f"{WARNING} You must be listening in `{vc.name}` to use this command!")
        if tc and ctx.channel != tc:
            raise CustomCheckFailure(f"{WARNING} You must be typing in `{tc.name}` to use this command!")

        player = ctx.bot.lavalink.players.get(ctx.guild.id)
        player_handler = player.event_adapter

        if playing and not player_handler and not player.is_playing:
            raise CustomCheckFailure(f"{WARNING} The bot must be playing or paused to use this command!")
        if in_channel and not ctx.author.voice and not ctx.author.voice.channel:
            raise CustomCheckFailure(f"{WARNING} You must be in a voice channel to use this command!")
        if is_dj and dj and dj not in ctx.author.roles and not ctx.author.guild_permissions.mute_members:
            raise CustomCheckFailure(f"{WARNING} You must have the role: `{dj.name}` "
                                     f"or the mute members permission to use this command!")
        return True

    return commands.check(predicate)
