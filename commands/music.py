import re
from random import shuffle

from discord.ext import commands

from audio import PlayerHandlerManager, QueuePaginator
from utils.music import music_check
from utils.visual import SUCCESS, WARNING, ERROR, NOTES

time_rx = re.compile('[0-9]+')


class Music:
    def __init__(self, bot):
        self.bot = bot
        self.lavalink_wrapper = PlayerHandlerManager(bot)

    @commands.command(aliases=["pl"])
    @music_check(in_channel=True)
    async def play(self, ctx, *, query: str):
        handler = await self.lavalink_wrapper.get_player_handler(ctx)
        splitted = query.split()
        should_shuffle = False

        if splitted[0] == "shuffle":
            should_shuffle = True
            query = "".join(splitted[1:])
        if query == "init0":
            query = "https://www.youtube.com/playlist?list=PLzME6COik-H9hSsEuvAf26uQAN228ESck"

        if not ctx.author.voice.channel:
            await ctx.send(f"{WARNING} You must be in a voice channel first!")
            return
        if handler.player.is_connected and ctx.author.voice.channel.id != int(handler.player.channel_id):
            await ctx.send(f"{WARNING} You must be listening in my voice channel to use that command!")
            return
        try:
            await handler.player.connect(ctx.author.voice.channel)
        except:
            await ctx.send(f"{ERROR} I am unable to connect to **{ctx.author.voice.channel.name}**")
        if not query.startswith("http"):
            query = f"ytsearch:{query}"
        results = await self.lavalink_wrapper.search(query)

        if not results:
            await ctx.send(f"{WARNING} No results found!")
            return

        if not query.startswith("http"):
            await handler.add_track(results[0], ctx.author)
            await ctx.send(f"{NOTES} **Added** `{results[0].title}` to the queue")
        else:
            if should_shuffle:
                shuffle(results)
            for track in results:
                await handler.add_track(track, ctx.author)
            await ctx.send(f"{NOTES} **Added** {len(results)} entries to the queue")

    @commands.command(aliases=["disconnect", "dc"])
    @music_check(in_channel=True, is_dj=True)
    async def stop(self, ctx):
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if player.event_adapter:
            await player.event_adapter.stop()
        await player.disconnect()
        await ctx.send(f"{SUCCESS} The player has been stopped and the bot has disconnected")

    @commands.command(aliases=["np", "nowplaying"])
    @music_check(playing=True)
    async def current(self, ctx):
        player = self.bot.lavalink.players.get(ctx.guild.id)
        embed = player.event_adapter.embed_current()
        await ctx.send(embed=embed)

    @commands.command(aliases=["q", "songlist"])
    @music_check(playing=True)
    async def queue(self, ctx, page=0):
        player = self.bot.lavalink.players.get(ctx.guild.id)
        handler = player.event_adapter
        if not handler.queue:
            await ctx.send(f"{WARNING} No songs are in the queue!")
            return
        paginator = QueuePaginator(ctx=ctx, player_handler=handler, page=page)
        await paginator.send_to_channel()

    @commands.command(aliases=["sh"])
    @music_check(playing=True)
    async def shuffle(self, ctx):
        player = self.bot.lavalink.players.get(ctx.guild.id)
        player.event_adapter.shuffle()
        await ctx.send()

    @commands.command(aliases=["s"])
    @music_check(playing=True)
    async def skip(self, ctx):
        player = self.bot.lavalink.players.get(ctx.guild.id)
        handler = player.event_adapter
        listeners = list(filter(lambda m: not m.bot and not (m.voice.deaf or m.voice.self_deaf),
                                player.connected_channel.members))
        skips_needed = round(len(listeners)*0.5)
        current_skips = len(player.skips)
        if handler.current.requester == ctx.author or current_skips+1 >= skips_needed:
            await handler.skip()
            await ctx.send(f"{SUCCESS} The current song has been skipped")
        else:
            handler.skips.add(ctx.author)
            await ctx.send(f"{SUCCESS} You have voted to skip this song, "
                           f"`{current_skips-skips_needed}` more skips are needed to skip")


def setup(bot):
    bot.add_cog(Music(bot))
