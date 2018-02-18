import asyncio
import os
import sys
import traceback

from discord.ext.commands import AutoShardedBot, MissingRequiredArgument, CommandNotFound, NoPrivateMessage

from utils.exceptions import CustomCheckFailure
from utils.visual import WARNING


class Bot(AutoShardedBot):
    COLOR = 0x728fff

    def __init__(self, bot_settings, **kwargs):
        super().__init__(command_prefix=bot_settings.prefix, **kwargs)
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

    async def on_command_error(self, context, exception):
        if isinstance(exception, CommandNotFound):
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
