import datetime
import threading
import time

import influxdb_client
import requests
import json

from .notifier import HealthNotifier


class InfluxDBV2Notifier(HealthNotifier):
    def __init__(self, config):
        super().__init__("influxdb_v2", config)
        self.url = config.get('url', 'url')
        self.token = config.get('token', '')
        self.org = config.get('org', '')
        self.bucket = config.get('bucket', '')
        self.tags = config.get('tags', {})

        self.client = None
        self.writer = None
        self.points = []

        self.influxdb_thread = threading.Thread(name=self.label, target=self.run)
        self.influxdb_thread.setDaemon(True) # no need to wait for these to finish.
        self.influxdb_thread.start()

    def run(self):
        while True:
            if self.points:
                self.logger.debug(f"Writing {len(self.points)} points")
                try:
                    if not self.client:
                        self.client = influxdb_client.InfluxDBClient(self.url, token=self.token, org=self.org,
                                                                     default_tags=self.tags)
                        self.writer = self.client.write_api()

                    # try and write points, if successful empty points, otherwise set connection to None
                    self.writer.write(self.bucket, record=self.points)
                    self.logger.debug("Finished writing points")
                    self.points = []
                except requests.exceptions.ConnectionError:
                    self.logger.exception(f"Could not connect to influxdb {self.url}")
                    self.writer = None
                    self.client = None
                    pass
                except Exception:
                    self.logger.exception("Could not send data to influxdb")
                    self.writer = None
                    self.client = None
                    pass

            try:
                time.sleep(5)
            except:
                pass

    def notify(self, result):
        tags = dict(**result['config'])
        tags['name'] = result['label']

        values = dict(result['measurement'])
        values['message'] = result['message']
        values['status'] = result['status']

        self.points.append({
            "measurement": result['check'],
            "tags": tags,
            "fields": values,
            "time": int(time.time() * 10 ** 9)
        })
