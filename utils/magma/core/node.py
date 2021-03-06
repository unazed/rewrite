import json

import asyncio
import aiohttp
import logging
import websockets

from .events import TrackEndEvent, TrackStuckEvent, TrackExceptionEvent
from .exceptions import NodeException

logger = logging.getLogger("magma")


class NodeStats:
    def __init__(self, msg):
        self.msg = msg

        self.players = msg.get("players")
        self.playing_players = msg.get("playingPlayers")
        self.uptime = msg.get("uptime")

        mem = msg.get("memory")
        self.mem_free = mem.get("free")
        self.mem_used = mem.get("used")
        self.mem_allocated = mem.get("allocated")
        self.mem_reservable = mem.get("reserveable")

        cpu = msg.get("cpu")
        self.cpu_cores = cpu.get("cores")
        self.system_load = cpu.get("systemLoad")
        self.lavalink_load = cpu.get("lavalinkLoad")

        frames = msg.get("frameStats")
        if frames:
            # These are per minute
            self.avg_frame_sent = frames.get("sent")
            self.avg_frame_nulled = frames.get("nulled")
            self.avg_frame_deficit = frames.get("deficit")
        else:
            self.avg_frame_sent = -1
            self.avg_frame_nulled = -1
            self.avg_frame_deficit = -1


class Node:
    def __init__(self, lavalink, name, uri, rest_uri, headers):
        self.name = name
        self.lavalink = lavalink
        self.uri = uri
        self.rest_uri = rest_uri
        self.headers = headers
        self.available = False
        self.stats = None
        self.ws = None

    async def _connect(self, tries=0):
        if tries < 5:
            try:
                self.ws = await websockets.connect(self.uri, extra_headers=self.headers)
            except OSError:
                logger.error(f"Connection refused, trying again in 5s, try: {tries+1}/5")
                await asyncio.sleep(5)
                await self._connect(tries+1)
        else:
            raise NodeException("Connection failed after 5 tries")

    async def connect(self):
        await self._connect()
        await self.on_open()
        self.lavalink.loop.create_task(self.listen())

    async def listen(self):
        try:
            while self.ws.open:
                msg = await self.ws.recv()
                await self.on_message(json.loads(msg))
        except websockets.ConnectionClosed as e:
            await self.on_close(e.code, e.reason)

    async def on_open(self):
        self.available = True
        await self.lavalink.load_balancer.on_node_connect(self)

    async def on_close(self, code, reason):
        self.available = False
        if not reason:
            reason = "<no reason given>"

        if code == 1000:
            logger.info(f"Connection to {self.name} closed gracefully with reason: {reason}")
        else:
            logger.warning(f"Connection to {self.name} closed unexpectedly with code: {code}, reason: {reason}")

        await self.lavalink.load_balancer.on_node_disconnect(self)

    async def on_message(self, msg):
        # We receive Lavalink responses here
        logger.debug(f"Received websocket message: {msg}")
        op = msg.get("op")
        if op == "playerUpdate":
            link = self.lavalink.get_link(msg.get("guildId"))
            await link.player.provide_state(msg.get("state"))
        elif op == "stats":
            self.stats = NodeStats(msg)
        elif op == "event":
            await self.handle_event(msg)
        else:
            logger.info(f"Received unknown op: {op}")

    async def send(self, msg):
        if not self.ws or not self.ws.open:
            try:
                await self.connect()
            except:
                raise NodeException("Websocket is not ready, cannot send message")
        await self.ws.send(json.dumps(msg))

    async def get_tracks(self, query):
        # Fetch tracks from the Lavalink node using its REST API
        params = {"identifier": query}
        headers = {"Authorization": self.headers["Authorization"]}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(self.rest_uri+"/loadtracks", params=params) as resp:
                return await resp.json()

    async def handle_event(self, msg):
        # Lavalink sends us track end event types
        player = self.lavalink.get_link(msg.get("guildId")).player
        event = None
        event_type = msg.get("type")

        if event_type == "TrackEndEvent":
            event = TrackEndEvent(player, player.current, msg.get("reason"))
        elif event_type == "TrackExceptionEvent":
            event = TrackExceptionEvent(player, player.current, msg.get("error"))
        elif event_type == "TrackStuckEvent":
            event = TrackStuckEvent(player, player.current, msg.get("thresholdMs"))
        elif event_type:
            logger.info(f"Received unknown event: {event}")

        if event:
            await player.trigger_event(event)
