import re
from enum import Enum

from decouple import config

from machine_attributes import Machine


def get_name_worker(machine: Machine):
    """Retorna o nome do worker"""
    worker_name = re.sub(r"\s", "", machine.processor).upper()
    return worker_name

mac = Machine()

class Coin(Enum):
    QRL = (
        "rx/0",
        "ca.qrl.herominers.com:1166",
        config("WALLET_QRL") + f".{get_name_worker(mac)}", "https://qrl.herominers.com/",
        True

    )

    XMR = (
        "rx/0", "ca.monero.herominers.com:1111",
        config("WALLET_XMR") + f".{get_name_worker(mac)}", "https://monero.herominers.com/",
        True

    )

    ZEPH = (
        "rx/0", "ca.zephyr.herominers.com:1123",
        config("WALLET_ZEPH") + f".{get_name_worker(mac)}", "https://zephyr.herominers.com/",
        True

    )

    XDAG = (
        "rx/0", "equal.xdagminer.com:13003",
        config("WALLET_XDAG") + f".{get_name_worker(mac)}", "https://xdag1usa.com/xdag/",
        True

    )

    def __init__(self, algorithm, pool, wallet, site, tls):
        self.algorithm = algorithm
        self.pool = pool
        self.wallet = wallet
        self.site = site
        self.tls = tls

