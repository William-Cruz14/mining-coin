import pathlib

import resend
from decouple import config
from jinja2 import Template

from logger import get_logger

resend.api_key = config("RESEND_API_KEY")


logger = get_logger("email-script")

def send_email(coin, pool):
    """
    Função para envio de email automatizado ao usuário.
    Args:
        coin (str): Nome da moeda mais rentável.
        pool (str): Endereço do pool de mineração.
    """
    try:
        logger.info("Enviando email...")
        template_path = pathlib.Path(__file__).parent.parent / "static" / "templates" / "email_template.html"

        with open(template_path, encoding="utf-8") as f:
            template = Template(f.read())

        msg = template.render(coin=coin, pool=pool)

        params : resend.Emails.SendParams ={
                "from": config("EMAIL_SERVER"),
                "to": [config("USER_EMAIL"),],
                "subject": "Nova moeda rentável",
                "html": msg,
        }

        email = resend.Emails.SendResponse = resend.Emails.send(params)
        logger.info(f"Email enviado com sucesso!")

    except Exception as e:
        logger.error(f"Erro ao enviar email: {e}")
        raise


