import random

import discord
from discord.ext import commands

from utils.music import music_check, QueuePaginator
from utils.visual import ERROR
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
            await mp.add_track(results[0], ctx.author)
            await ctx.send(f"{NOTES} **Added** `{results[0].title}` to the queue")

    @commands.command(aliases=["np", "nowplaying"])
    @music_check(playing=True)
    async def current(self, ctx):
        mp = self.mpm.get_music_player(ctx, False)
        embed = mp.embed_current()
        await ctx.send(embed=embed)

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

    @commands.command(aliases=["disconnect", "dc"])
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
            await ctx.send(f"{WARNING} The specified positions must be within `0-{queue_len}`!")
            return
        moved = mp.move(to_moved, pos)
        if pos == 0:
            await ctx.send(f"{SUCCESS} The track: {moved} has been moved to be played next")
        else:
            await ctx.send(f"{SUCCESS} The track: {moved} has been moved to position {pos+1}")


def setup(bot):
    bot.add_cog(Music(bot))
