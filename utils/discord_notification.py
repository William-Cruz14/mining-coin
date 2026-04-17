import requests
from decouple import config

def send_discord_notification(webhook_url, message):
    """"Envia una notificación a un canal de Discord utilizando un webhook.
    Args:
        webhook_url (str): La URL del webhook de Discord.
        message (str): El mensaje que se desea enviar.
    """
    WEBHOOK_URL = config('DISCORD_WEBHOOK_URL', default=webhook_url)
    
    data_test = {
        "content" : "Testando webhook de discord",
        "username" : "Notificador de Discord",
        "avatar_url" : "https://i.ibb.co/KpPcbcRw/Logo-Switch-Coin.png"
        
    }
    response = requests.post(WEBHOOK_URL, json=data_test)
    
    if response.status_code == 204:
        print("Notificación enviada correctamente a Discord.")
    else:
        print(f"Error al enviar la notificación a Discord. Código de estado: {response.status_code}")