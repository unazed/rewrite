import asyncio

from utils.DB.SettingsDB import SettingsDB

db = SettingsDB()
loop = asyncio.get_event_loop()
bot_settings = loop.run_until_complete(db.get_bot_settings())

# default bot settings
default_prefix = bot_settings.prefix
commands_dir = "commands"
token = bot_settings.token
owners = bot_settings.owners
