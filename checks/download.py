import time
import requests

from checks.monitor import Monitor

# disable warnings in case of ssl = false
import urllib3
urllib3.disable_warnings()

class DownloadMonitor(Monitor):
    def __init__(self, label, config, notifiers):
        super().__init__("download", label, config, notifiers)

        self.url = config['url']
        self.timeout = float(config.get('timeout', 10))
        self.headers = config.get('headers', {})
        self.ssl = config.get('ssl', "true").lower() in ('yes', 'true', 't', 'y', '1')

    # ping a server, returns data number of packets send, and round trip times
    def check(self):
        self.logger.debug(f"Downloading {self.url}")

        download_start = time.time_ns()
        download_bytes = 0
        try:
            self.logger.debug(f"Attempting to download from {self.url}...")
            res = requests.get(self.url, stream=True, headers=self.headers, timeout=self.timeout, verify=self.ssl)
            res.raise_for_status()
            timeout = time.time() + self.timeout
            for chunk in res.iter_content(chunk_size=1024):
                download_bytes += len(chunk)
                if time.time() > timeout:
                    raise TimeoutError
            self.logger.debug(f"Download success: {self.url}")
            download_diff = (time.time_ns() - download_start) / 1.0e9
            message = f"Finished download {download_bytes} in {download_diff:.3} seconds"
            result = 'success'
        except TimeoutError:
            self.logger.debug(f"Download not finished in time: {self.url}")
            download_diff = (time.time_ns() - download_start) / 1.0e9
            message = f"Failed to download the file in {self.timeout} seconds"
            result = 'failure'
        except:
            self.logger.exception(f"Download failed: {self.url}")
            download_diff = (time.time_ns() - download_start) / 1.0e9
            message = f"Failed to download the file"
            result = 'failure'

        data = {
            "bytes": download_bytes,
            "time": download_diff,
            "speed": (8 * download_bytes / 1_000_000) / download_diff,
            "state": 0 if result == 'success' else 1
        }

        return self.report(result, message, data)
