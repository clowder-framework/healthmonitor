import requests
import json

import notifier


class SlackNotifier(notifier.HealthNotifier):
    def __init__(self, config):
        super().__init__("slack", config)
        self.webhook = config['webhook']
        self.channel = None if 'channel' not in config else config['channel']
        self.user = None if 'user' not in config else config['user']

    def notify(self, result):
        message = ""
        message += "Label           : %s\n" % result['label'] if 'label' in result else result['label']
        message += "Status          : %s\n" % result['status']
        message += '\n'

        requests.post(self.webhook, headers={"Content-Type": "application/json"},
                      data=json.dumps({"channel": self.channel,
                                       "username": self.user,
                                       "text": message}))
