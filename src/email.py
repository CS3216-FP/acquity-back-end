import requests


class EmailService:
    def __init__(self, config):
        self.config = config

    def send_email(self, bcc_list, subject, text):
        return requests.post(
            f"https://api.mailgun.net/v3/{self.config['MAILGUN_API_BASE_URL']}/messages",
            auth=("api", self.config['MAILGUN_API_KEY']),
            data={
                "from": "Acquity <noreply@acquity.io>",
                "bcc": bcc_list,
                "subject": subject,
                "text": text,
            },
        )
