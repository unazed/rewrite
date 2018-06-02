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


def run(bs, manager, shard_count):
    controller = ShardController(bs, shard_count)
    controller.start_shards(manager)


if __name__ == "__main__":
    db = SettingsDB.get_instance()
    bot_settings = loop.run_until_complete(db.get_bot_settings())

    mp.set_start_method("spawn")
    manager = mp.Manager()
    run(bot_settings, manager, 8)

