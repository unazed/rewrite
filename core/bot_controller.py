import multiprocessing as mp
import signal

from core.bot import Bot


def start_shard_cluster(*args):
    controller, shard_stats, shard_id = args
    print(f"starting shard: {shard_id} in proc: {mp.current_process().pid}")
    bot = Bot(controller.bot_settings, shard_stats, shard_id=shard_id, shard_count=controller.shard_count)
    bot.run(controller.bot_settings.token)


class ShardController:
    def __init__(self, bot_settings, shard_ids, shard_count):
        self.bot_settings = bot_settings
        self.shard_ids = shard_ids
        self.shard_count = shard_count

    def start_shards(self, manager):
        print(f"starting shards in parent proc: {mp.current_process().pid}")
        shard_stats = manager.dict()
        for shard in self.shard_ids:
            proc = mp.Process(target=start_shard_cluster, args=(self, shard_stats, shard))
            proc.start()
            proc.join(5)
        signal.pause()
