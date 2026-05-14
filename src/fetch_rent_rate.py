from logger import get_logger
from whattomine_provider import WhatToMinerProvider
import re
import time

logger = get_logger("fetch_rentability-script")


class Strategy:
    def __init__(self, machine,  ):
        self.data = 