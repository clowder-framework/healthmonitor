import argparse
import logging
import os
import time

import yaml

import notifiers
import checks


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


def load_checks(args, health_notifiers):
    health_checks = []

    # Set up checks using environment variables
    if os.getenv("CHECKS", ""):
        config = yaml.safe_load(os.getenv("CHECKS", "{}"))
        health_checks.extend(setup_checks(config, health_notifiers))
    if os.getenv("CONFIG", ""):
        config = yaml.safe_load(os.getenv("CONFIG", "{}"))
        if 'checks' in config:
            health_checks.extend(setup_checks(config, health_notifiers))
    if os.getenv("CHECKS_FILE", ""):
        with open(os.getenv("CHECKS_FILE", ""), 'r') as f:
            config = yaml.load(f, Loader=yaml.BaseLoader)
            health_checks.extend(setup_checks(config, health_notifiers))
    if os.getenv("CONFIG_FILE", ""):
        with open(os.getenv("CONFIG_FILE", ""), 'r') as f:
            config = yaml.load(f, Loader=yaml.BaseLoader)
            health_checks.extend(setup_checks(config['checks'], health_notifiers))
    elif os.getenv("HEALTHMONITOR_CONFIG_FILE", ""):
        with open(os.getenv("HEALTHMONITOR_CONFIG_FILE", ""), 'r') as f:
            config = yaml.load(f, Loader=yaml.BaseLoader)
            health_checks.extend(setup_checks(config['checks'], health_notifiers))

    # Set up checks using arguments
    if args.checks:
        with open(args.checks, 'r') as f:
            config = yaml.load(f, Loader=yaml.BaseLoader)
            health_checks.extend(setup_checks(config, health_notifiers))
    if args.config:
        for config_file in args.config:
            with open(config_file, 'r') as f:
                config = yaml.load(f, Loader=yaml.BaseLoader)
                health_checks.extend(setup_checks(config['checks'], health_notifiers))
    elif args.config_file:
        with open(args.config_file, 'r') as f:
            config = yaml.load(f, Loader=yaml.BaseLoader)
            health_checks.extend(setup_checks(config['checks'], health_notifiers))

    # fallback in case nothing was specified
    if not health_checks:
        with open("config.yml", 'r') as f:
            config = yaml.load(f, Loader=yaml.BaseLoader)
            health_checks.extend(setup_checks(config['checks'], health_notifiers))

    return health_checks


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
        elif name == 'influxdb_v2':
            notifier = notifiers.InfluxDBV2Notifier(config)
            health_notifiers.append(notifier)
        else:
            logging.warning(f"Unknown notifier '{name}'")

    return health_notifiers


def load_notifiers(args):
    health_notifiers = []

    # Set up notifiers using environment variables
    if os.getenv("NOTIFIERS", ""):
        config = yaml.safe_load(os.getenv("NOTIFIERS", "{}"))
        health_notifiers.extend(setup_notifiers(config))
    if os.getenv("CONFIG", ""):
        config = yaml.safe_load(os.getenv("CONFIG", "{}"))
        if 'notifiers' in config:
            health_notifiers.extend(setup_notifiers(config['notifiers']))
    if os.getenv("NOTIFIERS_FILE", ""):
        with open(os.getenv("NOTIFIERS_FILE", ""), 'r') as f:
            config = yaml.load(f, Loader=yaml.BaseLoader)
            health_notifiers.extend(setup_notifiers(config))
    if os.getenv("CONFIG_FILE", ""):
        with open(os.getenv("CONFIG_FILE", ""), 'r') as f:
            config = yaml.load(f, Loader=yaml.BaseLoader)
            health_notifiers.extend(setup_notifiers(config['notifiers']))
    elif os.getenv("HEALTHMONITOR_CONFIG_FILE", ""):
        with open(os.getenv("HEALTHMONITOR_CONFIG_FILE", ""), 'r') as f:
            config = yaml.load(f, Loader=yaml.BaseLoader)
            health_notifiers.extend(setup_notifiers(config['notifiers']))

    # Set up notifiers using arguments
    if args.notifiers:
        with open(args.notifiers, 'r') as f:
            config = yaml.load(f, Loader=yaml.BaseLoader)
            health_notifiers.extend(setup_notifiers(config))
    if args.config:
        for config_file in args.config:
            with open(config_file, 'r') as f:
                config = yaml.load(f, Loader=yaml.BaseLoader)
                health_notifiers.extend(setup_notifiers(config['notifiers']))
    elif args.config_file:
        with open(args.config_file, 'r') as f:
            config = yaml.load(f, Loader=yaml.BaseLoader)
            health_notifiers.extend(setup_notifiers(config['notifiers']))

    # fallback in case nothing was specified
    if not health_notifiers:
        with open("config.yml", 'r') as f:
            config = yaml.load(f, Loader=yaml.BaseLoader)
            health_notifiers.extend(setup_notifiers(config['notifiers']))

    return health_notifiers


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file",
                        help="file path of the healthmonitor config")
    parser.add_argument("--config", nargs='*',
                        help="file path of the healthmonitor config")
    parser.add_argument("--notifiers", help="file path of the notifiers config")
    parser.add_argument("--checks", help="file path of the monitors config")
    args = parser.parse_args()

    health_notifiers = load_notifiers(args)
    health_checks = load_checks(args, health_notifiers)
    # noinspection PyBroadException
    try:
        base_logger.info("HealthMonitors are now running!")

        # keep running, and die if any thread stops
        while True:
            for check in health_checks:
                check.logger.debug("Checking if HealthMonitor is still running: " + check.label)

                if not check.is_alive():
                    check.logger.warning("HealthMonitor " + check.label + " thread has died: ... Restarting it.")
                    # Restart the monitor
                    check.cancel()
                    check.start()

            # wait one second to make sure threads are still alive
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    except Exception:
        base_logger.exception("exception in healthmonitor, will exit.")
    finally:
        # stop all threads first
        for m in health_checks:
            m.cancel()


if __name__ == "__main__":
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(level=logging.INFO,
                        datefmt='%Y-%m-%dT%H:%M:%S',
                        format='%(asctime)-15s.%(msecs)03dZ %(levelname)-7s [%(threadName)-15s] : %(name)s - %(message)s')
    logging.getLogger("requests.packages.urllib3").setLevel(logging.WARNING)
    base_logger = logging.getLogger("HealthMonitor")

    main()
