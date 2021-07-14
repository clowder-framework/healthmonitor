import requests
import json

import healthmonitor

msteamurl = ""
msteamnotify = ""


class MsTeamsNotifier(healthmonitor.HealthNotifier):
    def __init__(self, config):

    def notify(self, result):
        report(result)


def report(host, test_groups, elapsed_time, log, notify_on='both'):
    if msteamurl:
        message = ""
        message += "Host            : %s\n" % host
        message += "Total Tests     : %d\n" % test_groups['total']
        if notify_on == 'failure' or notify_on == 'both':
            message += "Failures        : %d\n" % len(log['failures'])
        message += "Errors          : %d\n" % len(log['errors'])
        message += "Timeouts       : %d\n" % len(log['timeouts'])
        message += "Skipped         : %d\n" % len(log['skipped'])
        if notify_on == 'successes' or notify_on == 'both':
            message += "Success         : %d\n" % len(log['success'])
        message += "Clowder Broken  : %d\n" % test_groups['clowder']
        message += "Elapsed time    : %5.2f seconds\n" % elapsed_time
        message += '\n'
        try:
            requests.post(msteamurl, headers={"Content-Type": "application/json"},
                              data=json.dumps({"title": "clowder-test",
                                               "text": message}))
        except Exception as e:
            print(e)
            raise e
