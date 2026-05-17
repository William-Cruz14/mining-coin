import resend
import pathlib
from decouple import config
from jinja2 import Template

resend.api_key = config("RESEND_API_KEY")

def send_email(coin, pool):
    """
    Função para envio de email automatizado ao usuário.
    Args:
        coin (str): Nome da moeda mais rentável.
        pool (str): Endereço do pool de mineração.
    """

    template_path = pathlib.Path("../static/templates/email_template.html")

    with open(template_path, "r", encoding="utf-8") as f:
        template = Template(f.read())

    msg = template.render(coin=coin, pool=pool)

    params : resend.Emails.SendParams ={
            "from": config("EMAIL_SERVER"),
            "to": [config("USER_EMAIL"),],
            "subject": "Nova moeda rentável",
            "html": msg,
    }

    email = resend.Emails.SendResponse = resend.Emails.send(params)
    print(f"Email enviado!")
