import asyncio
import logging
import os
from datetime import datetime

from discord.ext import commands

from audio.player_manager import MusicPlayerManager
from utils.DB import SettingsDB
from utils.exceptions import CustomCheckFailure
from utils.visual import ERROR


class Bot(commands.AutoShardedBot):

    @staticmethod
    def prefix_from(bot, msg):
        # must be an instance of this bot pls dont use anything else
        return bot.prefix_map.get(msg.guild.id, bot.bot_settings.prefix)

    def __init__(self, bot_settings, **kwargs):
        super().__init__(Bot.prefix_from, **kwargs)
        self.logger = logging.getLogger("bot")
        self.start_time = datetime.now()
        self.bot_settings = bot_settings
        self.prefix_map = {}
        self.mpm = None
        self.ready = False

        logging.basicConfig(format="%(levelname)s -- %(name)s.%(funcName)s : %(message)s", level=logging.INFO)

    async def on_ready(self):
        if self.ready:
            return

        self.logger.info("!! Logged in !!")
        self.remove_command("help")

        self.mpm = MusicPlayerManager(self)
        await self.mpm.lavalink.add_node("local", "ws://localhost:8080",
                                         "http://localhost:2333", "youshallnotpass")

        prefix_servers = SettingsDB.get_instance().guild_settings_col.find({
            "$and": [{"prefix": {"$exists": True}},
                     {"prefix": {"$ne": "NONE"}}]
        })

        async for i in prefix_servers:
            self.prefix_map[i["_id"]] = i["prefix"]

        commands_dir = "commands"
        ext = ".py"
        for file_name in os.listdir(commands_dir):
            if file_name.endswith(ext):
                command_name = file_name[:-len(ext)]
                self.load_extension(f"{commands_dir}.{command_name}")

        self.ready = True

    async def on_shard_ready(self, shard_id):
        self.logger.info(f"Shard: {shard_id}/{self.shard_count} is ready")

    async def on_message(self, msg):
        if not msg.author.bot:
            await self.process_commands(msg)

    async def on_command_error(self, context, exception):
        exc_class = exception.__class__
        if exc_class in (commands.CommandNotFound, commands.NotOwner):
            return

        exc_table = {
            CustomCheckFailure: exception.msg,
            commands.MissingRequiredArgument: f"{WARNING} The required arguments are missing for this command!",
            commands.NoPrivateMesssage: f"{WARNING} This command cannot be used in PM's!"
        }

        if isinstance(exception, (*exc_table,)):  # converts dictionary keys to tuple
            msg = await context.send(exc_table[exc_class])
            await asyncio.sleep(5)
            await msg.delete()
        else:
            await super().on_command_error(ctx, exception)

