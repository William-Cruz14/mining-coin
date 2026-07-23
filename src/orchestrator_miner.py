import json
from datetime import datetime, timedelta
from pathlib import Path

from decouple import config

from benchmark_selector import BenchmarkMatcher
from coins import Coin
from discord_notification import send_discord_notification
from dto_specs import CoinState
from logger import get_logger
from machine_attributes import Machine
from wallet_checker import BLACKLIST_HOURS, STALE_CYCLES_LIMIT, get_balance
from whattomine_provider import WhatToMinerProvider
from xmrig import Miner

logger = get_logger("fetch_rentability-script")

STATE_FILE = Path(__file__).parent.parent / "mining_state.json"


class StrategyMiner:
    def __init__(
            self, machine: Machine, benchmark: BenchmarkMatcher,
            data: WhatToMinerProvider, miner: Miner):

        self.machine = machine
        self.benchmark = benchmark
        self.data = data
        self.miner = miner
        self.current_coin: Coin | None = None
        self.states: dict[str, CoinState] = self._load_states()

    def _load_states(self) -> dict[str, CoinState]:
        if not STATE_FILE.exists():
            return {}
        try:
            raw = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            return {k: CoinState.model_validate(v) for k, v in raw.items()}
        except Exception as e:
            logger.error(f"Erro ao carregar mining_state.json: {e}")
            return {}

    def _save_states(self):
        try:
            STATE_FILE.write_text(
                json.dumps(
                    {k: v.model_dump(mode="json") for k, v in self.states.items()},
                    indent=2,
                    default=str,
                ),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"Erro ao salvar mining_state.json: {e}")

    def _get_state(self, coin: Coin) -> CoinState:
        if coin.name not in self.states:
            self.states[coin.name] = CoinState(coin=coin.name, balance=0, stale_cycles=0)
            self._save_states()
        return self.states[coin.name]

    def _is_blacklisted(self, coin: Coin) -> bool:
        state = self._get_state(coin)
        if state.blacklisted_until and datetime.now() < state.blacklisted_until:
            return True
        if state.blacklisted_until and datetime.now() >= state.blacklisted_until:
            state.stale_cycles = 0
            state.blacklisted_until = None
        return False

    def _check_wallet_progress(self, coin: Coin) -> bool:
        state = self._get_state(coin)
        current_balance = get_balance(coin)

        if current_balance is None:
            logger.warning(f"{coin.name}: não foi possível consultar saldo, ignorando ciclo.")
            return True

        progressed = current_balance > state.balance
        state.balance = current_balance

        if not progressed:
            state.stale_cycles += 1
            logger.warning(f"{coin.name}: sem progresso de saldo. Ciclos estagnados: {state.stale_cycles}")
        else:
            state.stale_cycles = 0

        if state.stale_cycles >= STALE_CYCLES_LIMIT:
            state.blacklisted_until = datetime.now() + timedelta(hours=BLACKLIST_HOURS)
            logger.warning(f"{coin.name}: blacklistada por {BLACKLIST_HOURS}h.")
            send_discord_notification(
                config("DISCORD_WEBHOOK_URL"),
                f"⚠️ {coin.name} sem ganhos por {STALE_CYCLES_LIMIT} ciclos consecutivos. "
                f"Moeda suspensa por {BLACKLIST_HOURS}h e nova seleção será feita."
            )
            self._save_states()
            return False

        self._save_states()
        return True

    def initialize(self):
        try:
            logger.info("Inicializando estratégia de mineração.")

            hashrate = self.benchmark.select_hashrate()
            threads = self.benchmark.select_threads()
            power = self.benchmark.select_power()

            profits = self.data.get_estimate_profit(power=power, hashrate=hashrate)

            supported = {c.name for c in Coin if not self._is_blacklisted(c)}
            if not supported:
                logger.warning("Todas as moedas estão blacklistadas. Mantendo mineração atual.")
                return self.current_coin

            best = max(
                (p for p in profits if p.tag in supported),
                key=lambda p: p.profit24
            )
            best_coin = Coin[best.tag]

            if self.current_coin and not self._check_wallet_progress(self.current_coin):
                logger.info("Moeda atual estagnada, forçando troca.")
                best_coin = Coin[max(
                    (p for p in profits if p.tag in {c.name for c in Coin if not self._is_blacklisted(c)}),
                    key=lambda p: p.profit24
                ).tag]

            if best_coin != self.current_coin:
                self.miner.start_miner(coin=best_coin, threads=threads)
                self.current_coin = best_coin
            else:
                logger.info(f"Moeda mais rentável continua sendo {best_coin.name}, mantendo mineração.")

            return best_coin

        except Exception as e:
            logger.error(f"Erro ao inicializar a estratégia: {e}")
            raise
