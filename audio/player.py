from collections import deque
from random import shuffle
import discord
import itertools

from utils.DB import SettingsDB
from utils.magma.core import TrackPauseEvent, TrackResumeEvent, TrackStartEvent, TrackEndEvent, \
    AbstractPlayerEventAdapter, TrackExceptionEvent, TrackStuckEvent, format_time
from utils.music import UserData, Enqueued
from utils.visual import NOTES, COLOR


class MusicQueue:
    def __init__(self, items=deque()):
        self.items = items

    def __len__(self):
        return len(self.items)

    def __getitem__(self, item):
        return self.items[item]

    @property
    def size(self):
        return self.__len__()

    @property
    def empty(self):
        return not self.items

    def index(self, item):
        return self.items.index(item)

    def popleft(self):
        return self.items.popleft()

    def put(self, item):
        self.items.append(item)
        return self.index(item)

    def remove(self, item):
        return self.items.remove(item)

    def shorten(self, start):
        self.items = deque(itertools.islice(self.items, start, self.size))

    def clear(self):
        return self.items.clear()

    def move(self, to_move, pos):
        moved = self.items[to_move]
        self.items.remove(moved)
        self.items.insert(pos, moved)
        return moved

    def shuffle(self):
        shuffle(self.items)


class MusicPlayer(AbstractPlayerEventAdapter):
    def __init__(self, ctx, link):
        self.ctx = ctx
        self.link = link
        self.player = link.player
        self.bot = ctx.bot
        self.guild = ctx.guild
        self.skips = set()
        self.queue = MusicQueue()
        self.repeat_queue = deque()
        self.paused = False
        self.autoplaying = False
        self.autoplayed = False
        self.current = None
        self.previous = None

        link.player.event_adapter = self

    def embed_current(self):
        track = self.current.track
        title = track.title
        url = track.uri
        requester = self.current.requester.name
        progress = f"{format_time(self.player.position)}/{format_time(track.duration)}"

        embed = discord.Embed(description=f"[{title}]({url})", color=COLOR) \
            .set_author(name="Now playing", icon_url=self.current.requester.avatar_url) \
            .add_field(name="Requested by", value=requester, inline=True) \
            .add_field(name="Progress", value=progress, inline=True)
        if "youtube" in url:
            embed.set_thumbnail(url=f"https://img.youtube.com/vi/{track.identifier}/hqdefault.jpg")
        return embed

    def shuffle(self):
        self.queue.shuffle()

    def clear(self):
        self.queue.clear()

    def remove(self, to_remove):
        return self.queue.remove(to_remove)

    def move(self, to_move, pos):
        return self.queue.move(to_move, pos)

    async def music_chan(self):
        settings = await SettingsDB.get_instance().get_guild_settings(self.guild.id)
        text_id = settings.textId
        return self.guild.get_channel(text_id)

    async def tms(self):
        settings = await SettingsDB.get_instance().get_guild_settings(self.guild.id)
        return settings.tms

    async def add_track(self, audio_track, requester):
        return await self.add_enqueued(Enqueued(audio_track, requester))

    async def add_enqueued(self, enqueued):
        enqueued.track.user_data = UserData.UNCHANGED
        if not self.current:
            self.current = enqueued
            await self.player.play(enqueued.track)
            return -1
        if self.autoplaying:
            self.current.track.user_data = UserData.REPLACED_AUTOPLAY
            self.autoplaying = False
            self.queue.clear()
            self.queue.put(enqueued)
            await self.player.stop()
            return -1
        self.queue.put(enqueued)
        return self.queue.index(enqueued)

    async def stop(self):
        self.current = None
        self.paused = False
        if self.player.current:
            self.player.current.user_data = UserData.STOPPED
            await self.player.stop()
        self.clear()

    async def skip(self):
        self.player.current.user_data = UserData.SKIPPED
        await self.player.stop()

    async def skip_to(self, pos):
        self.player.current.user_data = UserData.SKIPPED
        self.queue.shorten(pos)
        await self.player.stop()

    async def load_autoplay(self, identifier):
        if identifier == "DEFAULT":
            bot_settings = self.bot.bot_settings
            playlist = bot_settings.autoplayPlaylist
        else:
            playlist = identifier

        tracks = await self.link.get_tracks(playlist, False)
        shuffle(tracks)
        for track in tracks:
            await self.add_track(track, self.guild.me)
        self.autoplaying = True

    async def track_pause(self, event: TrackPauseEvent):
        self.paused = True

    async def track_resume(self, event: TrackResumeEvent):
        self.paused = False

    async def track_start(self, event: TrackStartEvent):
        self.skips.clear()
        self.repeat_queue.append(self.current)
        topic = f"{NOTES} **Now playing** {self.current}"
        music_channel = await self.music_chan()
        tms = await self.tms()
        if music_channel:
            if tms:
                await music_channel.send(topic)
            try:
                await music_channel.edit(topic=topic)
            except:
                pass

    async def track_end(self, event: TrackEndEvent):
        user_data = event.track.user_data
        self.previous = self.current
        if user_data.may_start_next:
            if self.queue.empty:
                settings = await SettingsDB.get_instance().get_guild_settings(self.guild.id)

                if settings.repeat:
                    self.queue = MusicQueue(self.repeat_queue)
                    self.repeat_queue = deque()
                elif settings.autoplay != "NONE" and not self.autoplaying:
                    await self.load_autoplay(settings.autoplay)
                    music_channel = await self.music_chan()
                    tms = await self.tms()
                    if music_channel and tms:
                        await self.ctx.send(f"{NOTES} **Added** the autoplay playlist to the queue")

            if not self.queue.empty:
                self.current = self.queue.pop_left()
                await self.player.play(self.current.track)
                return

        if self.guild.id not in self.bot.bot_settings.patrons.values():
            await self.stop()
        settings = await SettingsDB.get_instance().get_guild_settings(self.guild.id)
        text_id = settings.textId
        music_channel = self.guild.get_channel(text_id)
        if music_channel:
            try:
                await music_channel.edit(topic="Not playing anything right now...")
            except:
                pass

    async def track_exception(self, event: TrackExceptionEvent):
        pass

    async def track_stuck(self, event: TrackStuckEvent):
        pass

