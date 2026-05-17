from enum import Enum
from decouple import config


class Coin(Enum):
    QRL = ("rx/0", "ca.qrl.herominers.com:1166", config("WALLET_QRL"), "https://qrl.herominers.com/")
    XMR = ("rx/0", "ca.monero.herominers.com:1111", config("WALLET_XMR"), "https://monero.herominers.com/")
    ZEPH = ("rx/0", "ca.zephyr.herominers.com:1123", config("WALLET_ZEPH"), "https://zephyr.herominers.com/")

    def __init__(self, algorithm, pool, wallet, site):
        self.algorithm = algorithm
        self.pool = pool
        self.wallet = wallet
        self.site = site
