from notifiers.notifier import HealthNotifier


class ConsoleNotifier(HealthNotifier):
    def __init__(self, config):
        super().__init__("console", config)
