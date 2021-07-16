import logging
import threading
import time


class Monitor(object):
    def __init__(self, check, label, config, notifiers):
        self.name = check
        self.label = label
        self.config = config
        self.notifiers = notifiers

        self.successesSinceLastFailure = 9999
        self.failuresSinceLastSuccess = 0

        self.sleep = int(config.get('sleep', 60))
        self.check_thread = None

        self.logger = logging.getLogger(f"{check}-{label}-monitor")

    def check(self):
        return {
            "status": "success",
            "check": self.name,
            "label": self.label,
            "message": "no test configured"
        }

    def run(self):
        while self.check_thread:
            self.logger.debug("Running check " + self.label)
            result = None
            try:
                # Run our handler with the given config
                result = self.check()
            except:
                self.logger.exception(f"Error running check_handler: {self.label}")

            if result:
                # Count number of success / failures since last status change
                if result['status'] == 'failure':
                    self.successesSinceLastFailure = 0
                    self.failuresSinceLastSuccess += 1
                if result['status'] == 'success':
                    self.failuresSinceLastSuccess = 0
                    self.successesSinceLastFailure += 1

                # Report results to interested notifiers
                for notifier in self.notifiers:
                    self.logger.debug(self.label + " checking notifier: " + notifier.label)

                    # 'always' or 'failure' (default)
                    report = notifier.report

                    # Report successes only if requested and over the threshold
                    try:
                        if report == 'always' and self.successesSinceLastFailure == notifier.threshold:
                            self.logger.debug(self.label + " reporting success: " + notifier.label)
                            notifier.notify(result)
                        # Report failures only if threshold is surpassed
                        elif self.failuresSinceLastSuccess == notifier.threshold:
                            self.logger.debug(self.label + " reporting failure: " + notifier.label)
                            notifier.notify(result)
                        else:
                            self.logger.debug(f"Skipping report: {self.label}-{notifier.label} " +
                                              f"- faililures={self.failuresSinceLastSuccess} " +
                                              f"/ successes={self.successesSinceLastFailure} " +
                                              f"/ threshold={notifier.threshold})")
                    except:
                        self.logger.exception(f"Error calling notifier: {self.label}-{notifier.label}")

            time.sleep(self.sleep)

    def start(self):
        # noop if Timer is already running
        if self.check_thread is not None:
            self.logger.warning("HealthMonitor already running.. skipping.")
            return

        # Create a Timer and start it
        self.logger.info(f"Starting HealthMonitor: {self.name}-{self.label}")
        self.check_thread = threading.Thread(name=self.label, target=self.run)
        self.check_thread.setDaemon(True) # no need to wait for these to finish.
        self.check_thread.start()
        self.logger.debug(f"Started HealthMonitor: {self.name}-{self.label}")

    def is_alive(self):
        return False if self.check_thread is None else self.check_thread.is_alive()

    def cancel(self):
        self.logger.info(f"Stopping HealthMonitor: {self.name}-{self.label}")
        self.check_thread = None
        self.logger.debug(f"Stopped HealthMonitor: {self.name}-{self.label}")
