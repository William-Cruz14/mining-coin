import requests
from logger import get_logger

logger = get_logger("discord-notification")

def send_discord_notification(webhook_url, message):
    """
    Envia uma notificação no discord.
    Args:
        webhook_url (str): a URL do webhook do Discord.
        message (str): A mensagem que se deseja enviar.
    """
    try:
    
        payload = {
            "content" : message,
            "username" : "Bot Python HashPilot 📊",
            "embeds": [
                {
                    "title": "Status da Moeda mais Rentável",
                    "description": "Todos os serviços estão funcionando normalmente, sem erros ou falhas.",
                    "color": 0xF26A8D,
                    "footer": {
                        "text": "HashPilot v1.0 - Gerado Automaticamente",
                    },
                    "image": {
                        "url": "https://ik.imagekit.io/aqm7yiqet/Logo%20Hash%20Pilot.svg?updatedAt=1776548434942",
                        "placeholder": "Logo do HashPilot",
                    }
                }

            ]

        }
        response = requests.post(webhook_url, json=payload)

    except Exception as e:
        logger.error(f"Erro ao enviar notificação para o Discord: {e}")
        raise
    
if __name__ == "__main__":
    send_discord_notification("webhook_url", "message")