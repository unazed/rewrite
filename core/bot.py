from discord.ext.commands import Bot
from utils import config
import asyncio
import os


class BotInstance(Bot):
    def __init__(self, owners):
        # TODO: get prefix from server settings db
        super().__init__(loop=asyncio.get_event_loop(),
                         command_prefix=config.default_prefix)
        self.prefix = config.default_prefix
        self.owners = owners
        
        # load commands
        commands_dir = config.commands_dir
        ext = ".py"
        for file_name in os.listdir(commands_dir):
            if not file_name.endswith(ext):
                continue

            command_name = file_name[:-len(ext)]
            self.load_extension(f"{commands_dir}.{command_name}")

    async def on_message(self, msg):
        if msg.author.bot:
            return

        await self.process_commands(msg)
