import smtplib
from email.mime.text import MIMEText
from flowc.config import Config

class EmailSender:
    def __init__(self):
        if not Config.SMTP_HOST:
            raise RuntimeError("SMTP config not set")

    def send(self, html: str, subject: str = "[FlowC] Daily Report"):
        msg = MIMEText(html, "html", "utf-8")
        msg["Subject"] = subject
        msg["From"] = Config.SMTP_FROM
        msg["To"] = Config.SMTP_TO

        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            server.starttls()
            if Config.SMTP_USER:
                server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)
