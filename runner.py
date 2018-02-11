#!/usr/bin/env python3
import asyncio

from core.bot import BotInstance
from utils.DB.SettingsDB import SettingsDB

loop = asyncio.get_event_loop()


def run(bs, **kwargs):
    tasks = (BotInstance(bs, **kwargs).run(bs.token), )
    loop.run_until_complete(asyncio.gather(*tasks))


if __name__ == "__main__":
    """
    Replace bot_settings with something such as:

    BotSettings("0", token="token_here", prefix=",", ...)

    if you don't have a proper DB set up
    """
    db = SettingsDB()
    bot_settings = loop.run_until_complete(db.get_bot_settings())
    run(bot_settings)
