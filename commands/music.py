import random

import discord
from discord.ext import commands

from utils.DB import SettingsDB
from utils.magma.core import format_time
from utils.music import music_check, QueuePaginator
from utils.visual import ERROR, COLOR
from utils.visual import NOTES
from utils.visual import SUCCESS
from utils.visual import WARNING


class Music:
    def __init__(self, bot):
        self.bot = bot
        self.mpm = bot.mpm

    @commands.command(aliases=["pl"])
    @music_check(in_channel=True)
    async def play(self, ctx, *, query: str):
        mp = self.mpm.get_music_player(ctx)
        splitted = query.split()
        should_shuffle = False

        if splitted[0] == "shuffle":
            should_shuffle = True
            query = "".join(splitted[1:])
        if query == "init0":
            query = "https://www.youtube.com/playlist?list=PLzME6COik-H9hSsEuvAf26uQAN228ESck"

        try:
            await mp.link.connect(ctx.author.voice.channel)
        except discord.ClientException:
            await ctx.send(f"{ERROR} I am unable to connect to **{ctx.author.voice.channel.name}**, "
                           f"check if the permissions are correct!")
            return

        if query.startswith("http"):
            results = await mp.link.get_tracks(query, False)
        else:
            results = await mp.link.get_tracks(query)

        if not results:
            await ctx.send(f"{WARNING} No results found!")
            return

        if query.startswith("http"):
            if should_shuffle:
                random.shuffle(results)
            for track in results:
                await mp.add_track(track, ctx.author)
            await ctx.send(f"{NOTES} **Added** {len(results)} entries to the queue")
        else:
            pos = await mp.add_track(results[0], ctx.author)
            if pos == -1:
                await ctx.send(f"{NOTES} **Added** `{results[0].title}` to be played now")
                return
            await ctx.send(f"{NOTES} **Added** `{results[0].title}` to position: `{pos+1}`")

    @commands.command(aliases=["np", "nowplaying"])
    @music_check(playing=True)
    async def current(self, ctx):
        mp = self.mpm.get_music_player(ctx, False)
        embed = mp.embed_current()
        await ctx.send(embed=embed)

    @commands.command(aliases=["prev"])
    @music_check(in_channel=True)
    async def previous(self, ctx):
        mp = self.mpm.get_music_player(ctx, False)
        if not mp or not mp.previous:
            await ctx.send(f"{WARNING} There hasn't been played anything yet!")
            return

        pos = await mp.add_track(mp.previous.track, ctx.author)
        if pos == -1:
            await ctx.send(f"{NOTES} **Added previous track:** `{mp.previous.track.title}` to be played now")
            return
        await ctx.send(f"{NOTES} **Added previous track:** `{mp.previous.track.title}` to position: `{pos+1}`")

    @commands.command(aliases=["q", "songlist"])
    @music_check(playing=True)
    async def queue(self, ctx, page=0):
        mp = self.mpm.get_music_player(ctx, False)
        if not mp.queue:
            await ctx.send(f"{WARNING} No songs are in the queue!")
            return
        paginator = QueuePaginator(ctx=ctx, music_player=mp, page=page)
        await paginator.send_to_channel()

    @commands.command(aliases=["s"])
    @music_check(playing=True)
    async def skip(self, ctx):
        mp = self.mpm.get_music_player(ctx, False)
        listeners = list(filter(lambda m: not m.bot and not (m.voice.deaf or m.voice.self_deaf),
                                ctx.guild.me.voice.channel.members))
        skips_needed = round(len(listeners) * 0.5)
        current_skips = len(mp.skips)
        if mp.current.requester == ctx.author or current_skips + 1 >= skips_needed:
            await mp.skip()
            await ctx.send(f"{SUCCESS} The current song has been skipped")
        else:
            mp.skips.add(ctx.author)
            await ctx.send(f"{SUCCESS} You have voted to skip this song, "
                           f"`{current_skips-skips_needed}` more skips are needed to skip")

    @commands.command(aliases=["sh"])
    @music_check(playing=True, is_dj=True)
    async def shuffle(self, ctx):
        mp = self.mpm.get_music_player(ctx, False)
        mp.shuffle()
        await ctx.send(f"{SUCCESS} The queue has been shuffled")

    @commands.command(aliases=["disconnect", "leave"])
    @music_check(in_channel=True, is_dj=True)
    async def stop(self, ctx):
        try:
            link = self.mpm.lavalink.get_link(ctx.guild)
            await link.disconnect()
            mp = self.mpm.get_music_player(ctx, False)
            await mp.stop()
        except:
            pass
        await ctx.send(f"{SUCCESS} The player has been stopped and the bot has disconnected")

    @commands.command(aliases=["rq", "clearqueue"])
    @music_check(in_channel=True, playing=True, is_dj=True)
    async def reset(self, ctx):
        mp = self.mpm.get_music_player(ctx, False)
        mp.clear()
        await ctx.send(f"{SUCCESS} The queue has been cleared")

    @commands.command(aliases=["r", "delete"])
    @music_check(in_channel=True, playing=True, is_dj=True)
    async def remove(self, ctx, pos: int):
        pos -= 1
        mp = self.mpm.get_music_player(ctx, False)
        track = mp.remove(pos)
        await ctx.send(f"{SUCCESS} The track: `{track.track.title}` has been removed")

    @commands.command(aliases=["jumpto", "jump"])
    @music_check(in_channel=True, playing=True, is_dj=True)
    async def skipto(self, ctx, pos: int):
        pos -= 1
        mp = self.mpm.get_music_player(ctx, False)
        await mp.skip_to(pos)
        await ctx.send(f"{SUCCESS} The current song has been skipped to pos: {pos}")

    @commands.command(aliases=["fskip", "modskip"])
    @music_check(in_channel=True, playing=True, is_dj=True)
    async def forceskip(self, ctx):
        mp = self.mpm.get_music_player(ctx, False)
        await mp.skip()
        await ctx.send(f"{SUCCESS} The current song has been skipped")

    @commands.command(aliases=["mov"])
    @music_check(playing=True, is_dj=True)
    async def move(self, ctx, to_moved: int, pos: int = 1):
        mp = self.mpm.get_music_player(ctx, False)
        queue_len = len(mp.queue)
        to_moved -= 1
        pos -= 1
        if not (0 <= to_moved < queue_len) and not (0 <= pos <= queue_len):
            await ctx.send(f"{WARNING} The specified positions must be from `0-{queue_len}`!")
            return
        moved = mp.move(to_moved, pos)
        if pos == 0:
            await ctx.send(f"{SUCCESS} The track: {moved} has been moved to be played next")
        else:
            await ctx.send(f"{SUCCESS} The track: {moved} has been moved to position {pos+1}")

    @commands.command()
    @music_check(playing=True, is_dj=True)
    async def seek(self, ctx, timestamp: str):
        mp = self.mpm.get_music_player(ctx, False)
        current_pos = round(mp.player.position)
        try:
            if ":" in timestamp:
                ts_split = [0, 0] + [int(t) for t in timestamp.split(':')]
                hours = ts_split[-3]
                mins = ts_split[-2]
                secs = ts_split[-1]
                pos = (secs + 60 * (mins + 60 * hours)) * 1000
            else:
                pos = current_pos + int(timestamp)*1000
        except ValueError:
            await ctx.send(f"{WARNING} The specified duration must be a number!")
            return

        await mp.player.seek_to(pos)
        await ctx.send(f"{SUCCESS} The current song has been seeked to `{format_time(pos)}`")

    @commands.command(aliases=["p"])
    @music_check(playing=True, is_dj=True)
    async def pause(self, ctx):
        mp = self.mpm.get_music_player(ctx, False)
        if mp.player.paused:
            await ctx.send(f"{WARNING} The player is already paused!")
            return

        await mp.player.set_paused(True)
        await ctx.send(f"{SUCCESS} The player has been paused")

    @commands.command(aliases=["re"])
    @music_check(playing=True, is_dj=True)
    async def resume(self, ctx):
        mp = self.mpm.get_music_player(ctx, False)
        if not mp.player.paused:
            await ctx.send(f"{WARNING} The player is not paused!")
            return

        await mp.player.set_paused(False)
        await ctx.send(f"{SUCCESS} The player has been resumed")

    @commands.command(aliases=["loop"])
    @music_check(playing=True, is_dj=True)
    async def repeat(self, ctx):
        settings = await SettingsDB.get_instance().get_guild_settings(ctx.guild.id)
        settings.repeat = not settings.repeat
        await SettingsDB.get_instance().set_guild_settings(settings)
        await ctx.send(f"{SUCCESS} The repeat state has been set to `{settings.repeat}`")

    @commands.command(aliases=["vol"])
    @music_check(playing=True, is_dj=True, is_donor="contributors")
    async def volume(self, ctx, volume: int):
        if not 0 <= volume <= 150:
            await ctx.send(f"{WARNING} The specified volume must be from `0-150`!")
            return

        mp = self.mpm.get_music_player(ctx, False)
        await mp.player.set_volume(volume)
        settings = await SettingsDB.get_instance().get_guild_settings(ctx.guild.id)
        settings.volume = volume
        await SettingsDB.get_instance().set_guild_settings(settings)
        await ctx.send(f"{SUCCESS} The player volume has been set to `{volume}`")

    @commands.group(pass_context=True, invoke_without_command=True, case_insensitive=True)
    @music_check(is_dj=True, is_donor="patrons")
    async def aliases(self, ctx):
        settings = await SettingsDB.get_instance().get_guild_settings(ctx.guild.id)
        aliases = settings.aliases if settings.aliases else {}
        if not aliases:
            await ctx.send(f"{WARNING} No aliases having been set! Add an alias with: `.aliases add [alias] [link]`")
            return

        embed = discord.Embed(color=COLOR)
        embed.set_footer(text="The name of the aliases are displayed above their links/values")
        for i in aliases:
            embed.add_field(name=i, value=aliases[i], inline=False)
        await ctx.send(content=f"{NOTES} Music aliases for **{ctx.guild.name}**", embed=embed)

    @aliases.command()
    @music_check(is_dj=True, is_donor="patrons")
    async def add(self, ctx, alias, *, link):
        settings = await SettingsDB.get_instance().get_guild_settings(ctx.guild.id)
        if not settings.aliases:
            settings.aliases = {}
        settings.aliases[alias] = link
        await SettingsDB.get_instance().set_guild_settings(settings)
        await ctx.send(f"{SUCCESS} The alias `{alias}` is now pointing to `{link}`. Use `.pl {alias}` to play it")

    @aliases.command(aliases=["delete"])
    @music_check(is_dj=True, is_donor="patrons")
    async def remove(self, ctx, alias):
        settings = await SettingsDB.get_instance().get_guild_settings(ctx.guild.id)
        if alias not in settings.aliases:
            await ctx.send(f"{WARNING} The alias `{alias}` is not found!")
            return
        del settings.aliases[alias]
        await SettingsDB.get_instance().set_guild_settings(settings)
        await ctx.send(f"{SUCCESS} The alias `{alias}` has been removed")


def setup(bot):
    bot.add_cog(Music(bot))
