import asyncio
from datetime import datetime
import os

import logging
from discord.ext.commands import AutoShardedBot, MissingRequiredArgument, CommandNotFound, NoPrivateMessage, NotOwner

from audio.player_manager import MusicPlayerManager
from utils.exceptions import CustomCheckFailure
from utils.visual import WARNING


class Bot(AutoShardedBot):

    def __init__(self, bot_settings, **kwargs):
        super().__init__(command_prefix=bot_settings.prefix, **kwargs)
        self.logger = logging.getLogger("bot")
        self.start_time = datetime.now()
        self.bot_settings = bot_settings
        self.prefix = bot_settings.prefix
        self.owners = bot_settings.owners
        self.mpm = None
        self.ready = False

        logging.basicConfig(format="%(levelname)s -- %(name)s.%(funcName)s : %(message)s", level=logging.INFO)

    async def on_ready(self):
        self.logger.info("!! Logged in !!")
        if not self.ready:
            self.remove_command("help")

            self.mpm = MusicPlayerManager(self)
            await self.mpm.lavalink.add_node("local", "ws://localhost:8080",
                                             "http://localhost:2333", "youshallnotpass")

            commands_dir = "commands"
            ext = ".py"
            for file_name in os.listdir(commands_dir):
                if not file_name.endswith(ext):
                    continue

                command_name = file_name[:-len(ext)]
                self.load_extension(f"{commands_dir}.{command_name}")
            self.ready = True

    async def on_shard_ready(self, shard_id):
        self.logger.info(f"Shard: {shard_id}/{self.shard_count} is ready")

    async def on_message(self, msg):
        if msg.author.bot:
            return
        await self.process_commands(msg)

    async def on_command_error(self, context, exception):
        if exception.__class__ in (CommandNotFound, NotOwner):
            return
        if isinstance(exception, CustomCheckFailure):
            msg = await context.send(exception.msg)
            await asyncio.sleep(5)
            await msg.delete()
        elif isinstance(exception, MissingRequiredArgument):
            msg = await context.send(f"{WARNING} The required arguments are missing for this command!")
            await asyncio.sleep(5)
            await msg.delete()
        elif isinstance(exception, NoPrivateMessage):
            msg = await context.send(f"{WARNING} This command cannot be used in PM's!")
            await asyncio.sleep(5)
            await msg.delete()
        else:
            await super().on_command_error(context, exception)
