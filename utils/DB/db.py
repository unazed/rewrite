import motor.motor_asyncio

from utils.DB.settings import GuildSettings, BotSettings


class SettingsDB:
    _instance = None

    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient("localhost", 27017)
        self.db = self.client.local
        self.guild_settings_col = self.db.settings
        self.bot_settings_col = self.db.bot_settings

    @staticmethod
    def get_instance():
        if not SettingsDB._instance:
            SettingsDB._instance = SettingsDB()
        return SettingsDB._instance

    async def get_bot_settings(self):
        document = await self.bot_settings_col.find_one({"_id": 0})
        return BotSettings(document.get("_id"), **document)

    async def set_bot_settings(self, settings):
        return await self.bot_settings_col.replace_one({"_id": 0}, settings.__dict__)

    async def get_guild_settings(self, id):
        document = await self.guild_settings_col.find_one({"_id": id})
        if document:
            return GuildSettings(document.get("_id"), **document)
        return GuildSettings(id)

    async def set_guild_settings(self, settings):
        return await self.guild_settings_col.replace_one({"_id": settings._id}, settings.__dict__)
