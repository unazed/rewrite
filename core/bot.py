import os

from discord.ext.commands import AutoShardedBot

from utils import config


class Bot(AutoShardedBot):
    COLOR = 0xff3f3f

    def __init__(self, bot_settings, **kwargs):
        super().__init__(command_prefix=config.default_prefix, **kwargs)
        self.bot_settings = bot_settings
        self.prefix = bot_settings.prefix
        self.owners = bot_settings.owners

    async def on_ready(self):
        print("!! ready !!")
        # load commands
        commands_dir = "commands"
        ext = ".py"
        self.remove_command("help")
        for file_name in os.listdir(commands_dir):
            if not file_name.endswith(ext):
                continue

            command_name = file_name[:-len(ext)]
            self.load_extension(f"{commands_dir}.{command_name}")

    async def on_message(self, msg):
        if msg.author.bot:
            return

        await self.process_commands(msg)
