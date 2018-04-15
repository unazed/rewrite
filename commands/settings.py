import discord
from discord.ext import commands

from utils.DB import SettingsDB
from utils.visual import COLOR, WARNING


class Settings:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, invoke_without_command=True)
    async def settings(self, ctx, setting=None, value=None):
        guild = ctx.guild
        settings = await SettingsDB.get_instance().get_guild_settings(guild.id)
        if not setting:
            dj_role = discord.utils.get(guild.roles, id=settings.djroleId)
            music_chan = discord.utils.get(guild.text_channels, id=settings.voiceId)
            voice_chan = discord.utils.get(guild.voice_channels, id=settings.textId)

            dj_role = f"{dj_role.name}" if dj_role else "NONE"
            music_chan = f"{music_chan.name}" if music_chan else "NONE"
            voice_chan = f"{voice_chan.name}" if voice_chan else "NONE"

            volume = settings.volume
            autoplay = settings.autoplay
            repeat = settings.repeat
            tms = settings.tms
            prefix = settings.prefix

            e = discord.Embed(description=f"DJ role: {dj_role}\n"
                                          f"Music channel: {music_chan}\n"
                                          f"Voice channel: {voice_chan}\n"
                                          f"Volume: {volume}\n"
                                          f"Autoplay: {autoplay}\n"
                                          f"Repeat: {repeat}\n"
                                          f"Now playing messages: {tms}\n"
                                          f"Prefix: {prefix}",
                              colour=COLOR)

            await ctx.send(content=f":tools: Settings for **{guild.name}**", embed=e)
        elif value:
            print(value)
            if setting == "dj":
            elif setting == "tc":
                pass
            elif setting == "vc":
                pass
            elif setting == "autoplay":
                pass
            elif setting == "tms":
                pass
            elif setting == "prefix":
                pass
            else:
                await ctx.send(WARNING + "The setting you want to change must be one of the following: `dj, tc, vc, "
                                         "autoplay, tms, prefix`")
        else:
