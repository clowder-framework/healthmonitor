import requests
import json

import healthmonitor


class SlackNotifier(healthmonitor.HealthNotifier):
    def __init__(self, config):
        self.webhook = config['webhook']
        self.channel = None if 'channel' not in config else config['channel']
        self.user = None if 'user' not in config else config['user']

        self.label = 'slack'
        self.threshold = config['threshold'] or 5
        self.report = config['report'] or 'failure'  # either 'always' or 'failure' (default)

    def notify(self, result):
        slack_message = build_message(result)
        try:
            requests.post(self.webhook, headers={"Content-Type": "application/json"},
                          data=json.dumps({"channel": self.channel,
                                           "username": self.user,
                                           "text": slack_message}))
        except Exception as e:
            raise e


def build_message(result, notify_on='both'):
    print(result)
    message = ""
    message += "Label           : %s\n" % result['url'] if 'url' in result else result['host']
    message += "Status          : %s\n" % result['status']
    #message += "Server          : %s\n" % servertype
    #message += "Total Tests     : %d\n" % test_groups['total']
    #if notify_on == 'failures' or notify_on == 'both':
    #    message += "Failures        : %d\n" % len(result['failures'])
    #message += "Errors          : %d\n" % len(result['errors'])
    #message += "Timeouts       : %d\n" % len(result['timeouts'])
    #message += "Skipped         : %d\n" % len(result['skipped'])
    #if notify_on == 'successes' or notify_on == 'both':
    #    message += "Success         : %d\n" % len(result['success'])
    #message += "Clowder Broken  : %d\n" % test_groups['clowder']
    #message += "Elapsed time    : %5.2f seconds\n" % elapsed_time
    message += '\n'

    return message
