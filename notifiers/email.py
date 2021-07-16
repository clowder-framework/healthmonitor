from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

from .notifier import HealthNotifier


class EmailNotifier(HealthNotifier):
    """
    The email notifier. This will notify people using email. The following configuration is
    supported (as well as the values from the HealthNotifier such as threshold and report.

        email:
           to:
             - user1 <email>
             - user2 <email>
           # optional
           # default localhost:25
           server: smtp.example.com
           # default healtmonitor <healthmonitor@localhost>
           from: "user <email>"
           # prefix to subject
           # default nothing
           subject: [HEALTH]
           # login for smtp server
           username: bob
           password: alice
    """
    def __init__(self, config):
        super().__init__("email", config)
        self.to = config['to']
        self.server = config.get('server', "localhost:25")
        self.sender = config.get('from', 'healthmonitor@localhost')
        self.prefix = config.get('prefix', '')
        if self.prefix and self.prefix[:-1] != ' ':
            self.prefix += ' '

    def notify(self, result):
        msg = MIMEMultipart('alternative')
        msg['From'] = self.sender
        msg['To'] = ', '.join(self.to)
        msg['Subject'] = f'{self.prefix} {result["status"]} - {result["label"]}'

        if result['status'] == 'success':
            txt = 'The following checks are now successful:\n'
        else:
            txt = 'The following checks are now failing:\n'
        txt += f'- {result["check"]} : {result["label"]}\n'
        if "message" in result:
            txt += f'  - {result["message"]}\n'
        if "config" in result:
            txt += f'  - config:\n'
            for k, v in result['config'].items():
                txt += f'    - {k} = {v}\n'
        msg.attach(MIMEText(txt, 'plain'))

        # send the actual message
        mailserver = SMTP(self.server)
        mailserver.sendmail(msg['From'], self.to, msg.as_string())
        mailserver.quit()
