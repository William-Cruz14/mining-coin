import time

from decouple import config

from benchmark_provider import BenchmarkProvider
from benchmark_selector import BenchmarkMatcher
from logger import get_logger
from machine_attributes import Machine
from orchestrator_miner import StrategyMiner
from whattomine_provider import WhatToMinerProvider
from xmrig import Miner

logger = get_logger("main-script")

if __name__ == "__main__":
    logger.info("Iniciando o script de mineração.")
    machine  = Machine()
    provider = BenchmarkProvider(machine)
    matcher  = BenchmarkMatcher(benchmark=provider.full_benchmarks(), machine=machine)
    wtm      = WhatToMinerProvider(config("WHAT_MINE_URL"), config("WHAT_TO_MINE_API"))
    miner    = Miner()

    strategy = StrategyMiner(machine=machine, benchmark=matcher, data=wtm, miner=miner)

    while True:
        strategy.initialize()
        time.sleep(2 * 60 * 60)
