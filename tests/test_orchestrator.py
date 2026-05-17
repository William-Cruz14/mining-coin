import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import MagicMock, patch
from whattomine_provider import WhatToMinerProvider
from orchestrator_miner import StrategyMiner
from dto_wins import WinsDTO
from coins import Coin


@pytest.fixture
def wtm():
    return WhatToMinerProvider(url="http://fake-url", api_key="fake-key")


@pytest.fixture
def mock_profits():
    return [
        WinsDTO(tag="XMR", revenue=1.0, revenue24=1.0, profit=0.9, profit24=0.9),
        WinsDTO(tag="ZEPH", revenue=2.0, revenue24=2.0, profit=1.8, profit24=1.8),
        WinsDTO(tag="UNKNOWN", revenue=5.0, revenue24=5.0, profit=4.9, profit24=4.9),
    ]


def test_get_estimate_profit_returns_list(wtm):
    fake_response = [
        {"tag": "XMR", "revenue": 1.0, "revenue24": 1.0, "profit": 0.9, "profit24": 0.9}
    ]
    with patch("whattomine_provider.requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: fake_response)
        result = wtm.get_estimate_profit(power=65, hashrate=1200)
    assert len(result) == 1
    assert result[0].tag == "XMR"


def test_get_estimate_profit_non_200_returns_empty(wtm):
    with patch("whattomine_provider.requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=500)
        result = wtm.get_estimate_profit(power=65, hashrate=1200)
    assert result == []


def test_strategy_picks_best_supported_coin(mock_profits):
    machine = MagicMock()
    benchmark = MagicMock()
    benchmark.select_hashrate.return_value = 1200
    benchmark.select_threads.return_value = 12
    benchmark.select_power.return_value = 65

    data = MagicMock()
    data.get_estimate_profit.return_value = mock_profits

    miner = MagicMock()

    strategy = StrategyMiner(machine=machine, benchmark=benchmark, data=data, miner=miner)
    result = strategy.initialize()

    assert result == Coin.ZEPH
    miner.start_miner.assert_called_once_with(coin=Coin.ZEPH, threads=12)


def test_strategy_ignores_unsupported_coins(mock_profits):
    machine = MagicMock()
    benchmark = MagicMock()
    benchmark.select_hashrate.return_value = 1200
    benchmark.select_threads.return_value = 12
    benchmark.select_power.return_value = 65

    data = MagicMock()
    # Apenas moeda não suportada
    data.get_estimate_profit.return_value = [
        WinsDTO(tag="UNKNOWN", revenue=99.0, revenue24=99.0, profit=99.0, profit24=99.0)
    ]

    strategy = StrategyMiner(machine=machine, benchmark=benchmark, data=data, miner=MagicMock())
    with pytest.raises(Exception):
        strategy.initialize()
