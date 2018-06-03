#!/usr/bin/env python3
import asyncio
import multiprocessing as mp

import uvloop

from core.bot_controller import ShardController
from utils.DB import SettingsDB
from utils.magma.core import node

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()
node.tries = 1
node.timeout = 2


if __name__ == "__main__":
    mp.set_start_method("spawn")
    mp_manager = mp.Manager()

    db = SettingsDB.get_instance()
    bot_settings = loop.run_until_complete(db.get_bot_settings())
    shards = 1#44

    controller = ShardController(bot_settings, (*range(shards),), shards)
    controller.start_shards(mp_manager)
