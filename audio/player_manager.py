from utils.magma.core import Lavalink
from .player import MusicPlayer


class MusicPlayerManager:
    def __init__(self, bot):
        self.bot = bot
        self.music_players = {}
        self.lavalink = Lavalink(bot)

    def get_music_player(self, ctx, select_if_absent=True):
        if not select_if_absent and ctx.guild.id in self.music_players:
            return self.music_players.get(ctx.guild.id)

        link = self.lavalink.get_link(ctx.guild)
        mp = MusicPlayer(ctx, link)
        self.music_players[ctx.guild.id] = mp
        return mp
