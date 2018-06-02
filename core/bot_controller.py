import multiprocessing as mp
import signal

from core.bot import Bot


def start_shard_cluster(*args):
    shard_clusters, controller, shard_ids = args
    print(f"starting shard cluster: {shard_ids} in proc: {mp.current_process().pid}")
    bot = Bot(controller.bot_settings, shard_clusters, shard_ids=shard_ids, shard_count=controller.shard_count)
    bot.run(controller.bot_settings.token)


class ShardController:
    def __init__(self, bot_settings, shard_count, shards_p_cluster=4):
        self.bot_settings = bot_settings
        self.shard_count = shard_count
        self.shards_p_cluster = shards_p_cluster

    def start_shards(self, manager):
        print(f"starting shards in parent proc: {mp.current_process().pid}")
        shards = [*range(self.shard_count)]
        shard_ids = [shards[i:i+self.shards_p_cluster] for i in range(0, self.shard_count, self.shards_p_cluster)]
        shard_clusters = manager.dict()
        for id_cluster in shard_ids:
            proc = mp.Process(target=start_shard_cluster, args=(shard_clusters, self, id_cluster))
            proc.start()
            proc.join(len(id_cluster)*5)
        signal.pause()
