import requests
import json

from .notifier import HealthNotifier


class SlackNotifier(HealthNotifier):
    def __init__(self, config):
        super().__init__("slack", config)
        self.webhook = config['webhook']
        self.channel = None if 'channel' not in config else config['channel']
        self.user = None if 'user' not in config else config['user']

    def notify(self, result):
        message = "```"
        message += f"Label           : {result['label']}\n"
        message += f"Check           : {result['check']}\n"
        message += f"Status          : {result['status']}\n"
        if "config" in result:
            message += f"Config          : {result['config']}\n"
        message += '```\n'

        data = {
            "channel": self.channel,
            "username": self.user,
            "attachments": [
                {
                    "fallback": message,
                    "pretext": result.get("message", f"{result['status']} from {result['check']}-{result['label']}"),
                    "color": "#2ECC71" if result['status'] == "success" else "#E74C3C",
                    "text": message
                }
            ]
        }
        requests.post(self.webhook,
                      headers={"Content-Type": "application/json"},
                      data=json.dumps(data))
