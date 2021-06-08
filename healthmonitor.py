import argparse
import json
import logging
import os
import sys
import time

from queue import Queue
from threading import Thread

from checks import server
from notifiers import slack


import ruamel.yaml


# helper to report data
def report_result(report_url, report_key, measurement, values, tags=None):
    if not values:
        return
    if tags:
        data = json.dumps({"measurement": measurement, "tags": tags, "values": values})
    else:
        data = json.dumps({"measurement": measurement, "values": values})
    if not report_url or not report_key:
        logging.info(data)
    else:
        try:
            logging.debug("Reporting for duty")
            # r = requests.post(report_url,
            #                  headers={"Content-Type": "application/json", "API-KEY": report_key},
            #                  data=data)
            # r.raise_for_status()
        except Exception as e:
            logging.exception("Error uploading result, data is lost")


# e.g. Example: config.yml
def parse_config(filename):
    with open(filename, 'r') as f:
        config = ruamel.yaml.load(f, ruamel.yaml.RoundTripLoader)

        # Set up notifiers - what should we do with results?
        notifiers_list = setup_notifiers(config['notifiers'])

        # Set up checks - how should we gather results?
        monitors = setup_checks(config['checks'], notifiers_list)

        sleep = 30 if 'sleep' not in config else config['sleep']

        return monitors, sleep


# Each check creates its own HealthMonitor
def setup_checks(checks_conf, notifiers_list):
    monitors = []

    if 'ping' in checks_conf:
        for label in checks_conf['ping']:
            ping_target = checks_conf['ping'][label]
            ping_monitor = HealthMonitor('ping-' + label, server.ping, ping_target, notifiers_list)
            ping_monitor.start()
            monitors.append(ping_monitor)

    if 'hostport' in checks_conf:
        for label in checks_conf['hostport']:
            hostport_target = checks_conf['hostport'][label]
            hostport_monitor = HealthMonitor('hostport-' + label, server.hostport, hostport_target, notifiers_list)
            hostport_monitor.start()
            monitors.append(hostport_monitor)

    if 'download' in checks_conf:
        for label in checks_conf['download']:
            download_target = checks_conf['download'][label]
            download_monitor = HealthMonitor('download-' + label, server.download_data, download_target, notifiers_list)
            download_monitor.start()
            monitors.append(download_monitor)

    return monitors


def setup_notifiers(notifiers_conf):
    health_notifiers = []

    # Example of simple/generic HealthNotifier
    if 'console' in notifiers_conf:
        console_config = notifiers_conf['console']
        console_notifier = HealthNotifier('console', console_config)
        health_notifiers.append(console_notifier)

    # Example of complex/custom HealthNotifier subclass
    if 'slack' in notifiers_conf:
        slack_config = notifiers_conf['slack']
        slack_notifier = slack.SlackNotifier(slack_config)
        health_notifiers.append(slack_notifier)

    # TODO: Fill these out
    if 'msteams' in notifiers_conf:
        msteams_report = notifiers_conf['msteams']['report']
        msteams_threshold = notifiers_conf['msteams']['threshold']
        msteams_webhook = notifiers_conf['msteams']['webhook']
    if 'rabbitmq' in notifiers_conf:
        rabbitmq_report = notifiers_conf['rabbitmq']['report']
        rabbitmq_threshold = notifiers_conf['rabbitmq']['threshold']
        rabbitmq_uri = notifiers_conf['rabbitmq']['uri']
        rabbitmq_exchange = notifiers_conf['rabbitmq']['exchange']
    if 'mongo' in notifiers_conf:
        mongo_report = notifiers_conf['mongo']['report']
        mongo_threshold = notifiers_conf['mongo']['threshold']
        mongo_host = notifiers_conf['mongo']['host']
        mongo_database = notifiers_conf['mongo']['database']
        mongo_collection = notifiers_conf['mongo']['collection']
    if 'influxdb' in notifiers_conf:
        influxdb_report = notifiers_conf['influxdb']['report']
        influxdb_threshold = notifiers_conf['influxdb']['threshold']
        influxdb_hostname = notifiers_conf['influxdb']['hostname']
        influxdb_username = notifiers_conf['influxdb']['username']
        influxdb_password = notifiers_conf['influxdb']['password']
        influxdb_database = notifiers_conf['influxdb']['database']
        influxdb_measurement = notifiers_conf['influxdb']['measurement']
    if 'email' in notifiers_conf:
        email_server = notifiers_conf['mail']['server']

    return health_notifiers


class HealthNotifier(object):
    def __init__(self, label, notifier_config):
        self.label = label
        self.config = notifier_config
        self.report = 'failure' if 'report' not in self.config else self.config['report']
        self.threshold = 0 if 'threshold' not in self.config else self.config['threshold']
        self.failures = 0
        self.logger = logging.getLogger(label + "-notifier")

    def notify(self, result):
        self.logger.info("Reporting for duty! here is your message: " + str(result))


class HealthMonitor(object):
    def __init__(self, label, handler, config, configured_notifiers, sleep=3):
        self.label = label
        self.check_handler = handler
        self.check_config = config
        self.notifiers = configured_notifiers

        self.successesSinceLastFailure = 0
        self.failuresSinceLastSuccess = 0

        self.sleep = 60 if 'sleep' not in config else config['sleep']
        self.check_thread = None

        self.logger = logging.getLogger(label + "-monitor")


    def callback(self):
        while True:
            self.logger.debug("Running check " + self.label)
            result = None
            try:
                # Run our handler with the given config
                result = self.check_handler(self.label, self.check_config)
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
                        if report == 'always' and self.successesSinceLastFailure > notifier.threshold:
                            self.logger.debug(self.label + " reporting success: " + notifier.label)
                            notifier.notify(result)
                        # Report failures only if threshold is surpassed
                        elif self.failuresSinceLastSuccess > notifier.threshold:
                            self.logger.debug(self.label + " reporting failure: " + notifier.label)
                            notifier.notify(result)
                        else:
                            self.logger.debug(f"Skipping report: {self.label}-{notifier.label} - not over threshold (failures={self.failuresSinceLastSuccess} / successes={self.successesSinceLastFailure} / threshold={notifier.threshold})")
                    except:
                        self.logger.exception(f"Error calling notifier: {self.label}-{notifier.label}")

            time.sleep(self.sleep)

    def start(self):
        # noop if Timer is already running
        if self.check_thread is not None:
            self.logger.warning("HealthMonitor already running.. skipping.")
            return

        # Create a Timer and start it
        self.logger.info("Starting HealthMonitor: " + self.label)
        self.check_thread = Thread(name=self.label, target=self.callback)  #Timer(self.sleep, self.callback)
        self.check_thread.start()
        self.logger.debug("Started HealthMonitor: " + self.label)

    def is_alive(self):
        return False if self.check_thread is None else self.check_thread.is_alive()

    def cancel(self):
        self.logger.info("Stopping HealthMonitor: " + self.label)
        self.check_thread.join()
        self.check_thread = None
        self.logger.debug("Stopped HealthMonitor: " + self.label)


# logic of the code:
# each of the checks runs in their own thread and will send the results to the response app
# - ping_server:
#   - checks to see if the server is pingable
#   - reports {#pings, loss, and round trip time}
# - clowder_healthy:
#   - checks to see if clowder claims to be healthy
#   - reports {health: 1/0}
# - clowder_homepage:
#   - checks to see if clowder home page can be downloaded
#   - returns {status: 1/0, size: X}
# - clowder_download:
#   - checks to see if a file can be downloaded
#   - reports {status: 1/0, size: X, speed: Y (Mbps)}
if __name__ == "__main__":
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(level=logging.INFO,
                        datefmt='%Y-%m-%dT%H:%M:%S',
                        format='%(asctime)-15s.%(msecs)03dZ %(levelname)-7s [%(threadName)-10s] : %(name)s - %(message)s')
    logging.getLogger("requests.packages.urllib3").setLevel(logging.WARNING)
    base_logger = logging.getLogger("HealthMonitor")

    parser = argparse.ArgumentParser()

    parser.add_argument("--config-file",
                        default=os.environ.get("HEALTHMONITOR_CONFIG_FILE", "config.yml"),
                        help="file path of the healthmonitor config")

    args = parser.parse_args()

    health_monitors = []
    try:
        (health_monitors, sleep_time) = parse_config(args.config_file)

        base_logger.info("HealthMonitors are now running!")

        # keep running, and die if any thread stops
        while True:
            base_logger.debug("HealthMonitors are still running...")

            for monitor in health_monitors:
                monitor.logger.debug("Checking if HealthMonitor is still running: " + monitor.label)

                if not monitor.is_alive():
                    monitor.logger.warning("HealthMonitor " + monitor.label + " thread has died: ... Restarting it.")

                    # Restart the monitor?
                    monitor.cancel()
                    monitor.start()
                    #sys.exit(1)

            time.sleep(sleep_time)
    finally:
        # stop all threads first
        for m in health_monitors:
            m.cancel()