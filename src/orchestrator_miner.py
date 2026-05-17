from benchmark_selector import BenchmarkMatcher
from logger import get_logger

from coins import Coin
from machine_attributes import Machine
from whattomine_provider import WhatToMinerProvider
from xmrig import Miner


logger = get_logger("fetch_rentability-script")

class StrategyMiner:
    def __init__(self, machine: Machine, benchmark: BenchmarkMatcher, data: WhatToMinerProvider, miner: Miner):
        self.machine  = machine
        self.benchmark = benchmark
        self.data     = data
        self.miner    = miner


    def initialize(self):
        """
        Escolhe a melhor moeda para mineração e inicializa o minerador
        com ela.
        Returns:
             Coin: Moeda escolhida para mineração
        """

        try:
            logger.info("Inicializando estratégia de mineração.")

            hashrate = self.benchmark.select_hashrate()
            threads = self.benchmark.select_threads()
            power = self.benchmark.select_power()

            profits = self.data.get_estimate_profit(power=power, hashrate=hashrate)

            supported = {c.name for c in Coin}
            best = max(
                (p for p in profits if p.tag in supported),
                key=lambda p: p.profit24
            )

            best_coin = Coin[best.tag]
            self.miner.start_miner(coin=best_coin, threads=threads)
            return best_coin

        except Exception as e:
            logger.error(f"Erro ao inicializar a estratégia: {e}")
            raise












