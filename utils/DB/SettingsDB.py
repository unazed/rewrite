import motor.motor_asyncio

from utils.DB.Settings import GuildSettings, BotSettings


class SettingsDB:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient("localhost", 27017)
        self.db = self.client.local
        self.guild_settings = self.db.settings
        self.bot_settings = self.db.bot_settings

    async def get_bot_settings(self):
        document = await self.bot_settings.find_one({"_id": "0"})
        return BotSettings(document.get("_id"), **document)

    async def set_bot_settings(self, settings):
        return await self.bot_settings.replace_one({"_id": "0"}, settings.__dict__)

    async def get_guild_settings(self, id):
        document = await self.guild_settings.find_one({"_id": id})
        return GuildSettings(document.get("_id"), **document)

    async def set_guild_settings(self, settings):
        return await self.guild_settings.replace_one({"_id": settings._id}, settings.__dict__)