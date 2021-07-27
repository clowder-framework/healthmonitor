import argparse
import logging
import os
import time

import yaml

import notifiers
import checks


# e.g. Example: config.yml
def parse_config(filename):
    with open(filename, 'r') as f:
        config = yaml.load(f, Loader=yaml.BaseLoader)

        # Set up notifiers - what should we do with results?
        notifiers_list = setup_notifiers(config['notifiers'])

        # Set up checks - how should we gather results?
        monitors = setup_checks(config['checks'], notifiers_list)

        return monitors


# Each check creates its own HealthMonitor
def setup_checks(checks_conf, notifiers_list):
    monitors = []

    for k, v in checks_conf.items():
        if k == 'ping':
            for label, config in v.items():
                monitor = checks.PingMonitor(label, config, notifiers_list)
                monitor.start()
                monitors.append(monitor)
        elif k == 'hostport':
            for label, config in v.items():
                monitor = checks.HostPortMonitor(label, config, notifiers_list)
                monitor.start()
                monitors.append(monitor)
        elif k == 'filewrite':
            for label, config in v.items():
                monitor = checks.FileWriteMonitor(label, config, notifiers_list)
                monitor.start()
                monitors.append(monitor)
        elif k == 'download':
            for label, config in v.items():
                monitor = checks.DownloadMonitor(label, config, notifiers_list)
                monitor.start()
                monitors.append(monitor)
        elif k == 'random':
            for label, config in v.items():
                monitor = checks.RandomMonitor(label, config, notifiers_list)
                monitor.start()
                monitors.append(monitor)
        else:
            logging.warning(f"Unknown check '{k}'")

    return monitors


def setup_notifiers(notifiers_conf):
    health_notifiers = []

    for name, config in notifiers_conf.items():
        if name == 'console':
            notifier = notifiers.ConsoleNotifier(config)
            health_notifiers.append(notifier)
        elif name == 'slack':
            notifier = notifiers.SlackNotifier(config)
            health_notifiers.append(notifier)
        elif name == 'email':
            notifier = notifiers.EmailNotifier(config)
            health_notifiers.append(notifier)
        elif name == 'influxdb':
            notifier = notifiers.InfluxDBNotifier(config)
            health_notifiers.append(notifier)
        else:
            logging.warning(f"Unknown notifier '{name}'")

    return health_notifiers


if __name__ == "__main__":
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(level=logging.INFO,
                        datefmt='%Y-%m-%dT%H:%M:%S',
                        format='%(asctime)-15s.%(msecs)03dZ %(levelname)-7s [%(threadName)-15s] : %(name)s - %(message)s')
    logging.getLogger("requests.packages.urllib3").setLevel(logging.WARNING)
    base_logger = logging.getLogger("HealthMonitor")

    parser = argparse.ArgumentParser()

    parser.add_argument("--config-file",
                        default=os.environ.get("HEALTHMONITOR_CONFIG_FILE", "config.yml"),
                        help="file path of the healthmonitor config")

    args = parser.parse_args()

    health_monitors = []
    try:
        health_monitors = parse_config(args.config_file)

        base_logger.info("HealthMonitors are now running!")

        # keep running, and die if any thread stops
        while True:
            for monitor in health_monitors:
                monitor.logger.debug("Checking if HealthMonitor is still running: " + monitor.label)

                if not monitor.is_alive():
                    monitor.logger.warning("HealthMonitor " + monitor.label + " thread has died: ... Restarting it.")
                    # Restart the monitor
                    monitor.cancel()
                    monitor.start()

            # wait one second to make sure threads are still alive
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    except Exception:
        base_logger.exception("exception in healthmonitor, will exit.")
    finally:
        # stop all threads first
        for m in health_monitors:
            m.cancel()
