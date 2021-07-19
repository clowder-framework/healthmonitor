import requests
import json

from .notifier import HealthNotifier


class SlackNotifier(HealthNotifier):
    def __init__(self, config):
        super().__init__("slack", config)
        self.webhook = config['webhook']
        self.channel = None if 'channel' not in config else config['channel']
        self.user = None if 'user' not in config else config['user']
        self.tags = config.get('tags', {})

    def notify(self, result):
        fallback = "```\n"
        fallback += f"Label           : {result['label']}\n"
        fallback += f"Check           : {result['check']}\n"
        fallback += f"Status          : {result['status']}\n"
        fallback += "\n"
        fallback += f"Tags\n"
        for k, v in self.tags.items():
            fallback += f"- {k:13} : {v}\n"
        fallback += "\n"
        fallback += f"Config \n"
        for k, v in result['config'].items():
            fallback += f"- {k:13} : {v}\n"
        fallback += '```\n'

        message = "```\n"
        message += f"Label           : {result['label']}\n"
        message += f"Check           : {result['check']}\n"
        message += f"Status          : {result['status']}\n"
        message += "\n"
        message += f"Config \n"
        for k, v in result['config'].items():
            message += f"- {k:13} : {v}\n"
        message += '```\n'

        data = {
            "channel": self.channel,
            "username": self.user,
            "attachments": [
                {
                    "fallback": fallback,
                    "pretext": result.get("message", f"{result['status']} from {result['check']}-{result['label']}"),
                    "color": "#2ECC71" if result['status'] == "success" else "#E74C3C",
                    "text": message,
                    "fields": [{"title": k, "value": v, "short": False} for k, v in self.tags.items()]
                }
            ]
        }
        requests.post(self.webhook,
                      headers={"Content-Type": "application/json"},
                      data=json.dumps(data))
