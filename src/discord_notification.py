import requests

def send_discord_notification(webhook_url, message):
    """Envia uma notificação no discord.
    Args:
        webhook_url (str): a URL do webhook do Discord.
        message (str): A mensagem que se deseja enviar.
    """
    
    payload = {
        "content" : message,
        "username" : "Bot Python Miner 📊",
        "embeds": [
            {
                "title": "Status da Moeda mais Rentável",
                "description": "Todos os serviços estão funcionando normalmente, sem erros ou falhas.",
                "color": 0x00FF00,
                "footer": {
                    "text": "SwithCoin 1.0 - Gerado Automaticamente",
                },
                "image": {
                    "url": "https://i.ibb.co/KpPcbcRw/Logo-Switch-Coin.png",
                    "placeholder": "Logo do SwitchCoin",
                }
            }

        ]

    }
    response = requests.post(webhook_url, json=payload)
    
    if response.status_code == 204:
        print("Notificação enviada com sucesso para o Discord.")
    else:
        print(f"Erro ao enviar a notificação {response.status_code}")