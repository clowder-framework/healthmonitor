import logging


class HealthNotifier(object):
    def __init__(self, label, config):
        self.label = label
        self.config = config
        self.report = 'failure' if 'report' not in self.config else self.config['report']
        self.threshold = 1 if 'threshold' not in self.config else self.config['threshold']
        if self.threshold < 1:
            self.threshold = 1
        self.failures = 0
        self.logger = logging.getLogger(label + "-notifier")


    def notify(self, result):
        self.logger.info("Reporting for duty! here is your message: " + str(result))
