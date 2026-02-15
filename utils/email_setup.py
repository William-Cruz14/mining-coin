import resend
from decouple import config
from jinja2 import Template

resend.api_key = config("RESEND_API_KEY")

def send_email(moeda, pool):
    with open("static/email_template.html", "r", encoding="utf-8") as f:
        template = Template(f.read())

    msg = template.render(moeda=moeda, pool=pool)

    params : resend.Emails.SendParams ={
            "from": config("EMAIL_SERVER"),
            "to": [config("USER_EMAIL")],
            "subject": "Nova moeda rentável",
            "html": msg,
    }

    email = resend.Emails.SendResponse = resend.Emails.send(params)
    print(f"Email enviado!")
