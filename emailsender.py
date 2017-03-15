import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader

logging.basicConfig(level=logging.INFO)


class EmailSender:
    """ Composes and sends email message with air pollution level data. """
    def __init__(self, config, data):
        self.config = config
        self.data = data

    def compose_email(self):
        env = Environment(loader=FileSystemLoader('templates'))
        email_template = env.get_template('email.html')
        email_body = email_template.render(
            station=self.data['station'],
            last_update=self.data['last_update'],
            pm10=self.data['pm10'],
            pm10_level=self.data['pm10_level'],
            pm25=self.data['pm25'],
            pm25_level=self.data['pm25_level'])

        email = MIMEMultipart()
        email['From'] = self.config['SENDER']['Email']
        email['To'] = self.config['RECIPIENT']['Email']
        email['Subject'] = self.config['MESSAGES']['Subject']
        email.attach(MIMEText(email_body, 'html'))
        return email.as_string()

    def send_email(self):
        server = smtplib.SMTP(self.config['SENDER']['SMTP'],
                              self.config['SENDER']['Port'])
        server.starttls()
        try:
            server.login(self.config['SENDER']['Email'],
                         self.config['SENDER']['Password'])
            server.sendmail(self.config['SENDER']['Email'],
                            self.config['RECIPIENT']['Email'],
                            self.compose_email())
            logging.info("Message was sent successfully")
        except smtplib.SMTPAuthenticationError:
            logging.info("Wrong username or password")
            return False
        server.quit()
        return True
