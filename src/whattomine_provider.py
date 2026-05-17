from decouple import config
from http import HTTPStatus
from src.logger import get_logger
from src.dto_wins import WinsDTO
import requests

logger = get_logger("whattomine-script")

KEY_API = config("WHAT_TO_MINE_API")
URL_API = config("WHAT_TO_MINE_URL")


class WhatToMinerProvider:
    """
    Classe que representa o provider do WhatToMine
    """
    url = URL_API
    api_key = KEY_API

    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key

    def get_estimate_profit(self, power: int, hashrate: int) -> list[WinsDTO]:
        """
        Método que estima o lucro com base na potência e hashrate
        Args:
            power (int): Potência
            hashrate (int): Hashrate
        Returns:
            list[WinsDTO]: Lista de objetos WinsDTO
        """

        results = []
        try:
            logger.info("Buscando os dados...")
            response = requests.get(
                self.url,
                json={
                    "cost": 0.0,
                    "settings": [
                        {
                            "algorithm": "rmx",
                            "power": power,
                            "hashrate": hashrate,
                        }
                    ],
                },
                headers={"Authorization": f"Token {self.api_key}"},
            )
            
            if response.status_code == HTTPStatus.OK:
                logger.info("Sucesso ao buscar os dados.")
                response_json = response.json()

                for data in response_json:
                    results.append(
                        WinsDTO(
                            tag=data["tag"],
                            revenue=data["revenue"],
                            revenue24=data["revenue24"],
                            profit=data["profit"],
                            profit24=data["profit24"]
                        )
                    )

            return results
        except Exception as e:
            logger.error(f"Erro ao estimar lucro: {e}")
            raise

if __name__ == "__main__":
    wtm = WhatToMinerProvider(URL_API, KEY_API)
    print(wtm.get_estimate_profit(120, 2600))
