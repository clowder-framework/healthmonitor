import datetime
import threading
import time

import influxdb
import influxdb.exceptions
import requests
import json

from .notifier import HealthNotifier


class InfluxDBNotifier(HealthNotifier):
    def __init__(self, config):
        super().__init__("influxdb", config)
        self.hostname = config.get('hostname', 'localhost')
        self.port = int(config.get('port', '8086'))
        self.username = config.get('username', 'localhost')
        self.password = config.get('password', 'localhost')
        self.database = config.get('database', 'localhost')
        self.tags = config.get('tags', {})

        self.influxdb = None
        self.points = []

        self.influxdb_thread = threading.Thread(name=self.label, target=self.run)
        self.influxdb_thread.setDaemon(True) # no need to wait for these to finish.
        self.influxdb_thread.start()

    def run(self):
        while True:
            if self.points:
                self.logger.debug(f"Writing {len(self.points)} points")
                try:
                    if not self.influxdb:
                        self.influxdb = influxdb.InfluxDBClient(self.hostname, self.port, self.username, self.password,
                                                                self.database)
                        try:
                            self.influxdb.create_database(self.database)
                        except influxdb.exceptions.InfluxDBClientError:
                            pass
                        self.influxdb.switch_database(self.database)

                    # try and write points, if successful empty points, otherwise set connection to None
                    if self.influxdb.write_points(self.points):
                        self.logger.debug("Finished writing points")
                        self.points = []
                    else:
                        self.logger.error("Error writing points")
                        self.influxdb = None
                except requests.exceptions.ConnectionError:
                    self.logger.error(f"Could not connect to influxdb {self.hostname}")
                    self.influxdb = None
                    pass
                except influxdb.exceptions.InfluxDBClientError:
                    self.logger.error(f"Could not connect to influxdb {self.hostname}")
                    self.influxdb = None
                except Exception:
                    self.logger.exception("Could not send data to influxdb")
                    self.influxdb = None
                    pass

            try:
                time.sleep(5)
            except:
                pass

    def notify(self, result):
        tags = dict(**self.tags, **result['config'])
        tags['name'] = result['label']

        values = dict(result['measurement'])
        values['message'] = result['message']
        values['status'] = result['status']

        self.points.append({
            "measurement": result['check'],
            "tags": tags,
            "fields": values,
            "time": str(datetime.datetime.utcnow())
        })

