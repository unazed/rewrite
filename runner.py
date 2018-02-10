#!/usr/bin/env python3
from core.bot import BotInstance
from utils import config
import asyncio


def run(token, owners):
    tasks = (BotInstance(owners).run(token), )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*tasks))


if __name__ == "__main__":
    run(config.token, config.owners)
