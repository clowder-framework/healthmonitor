import time
import urllib.request
import ssl

from checks.monitor import Monitor


class DownloadMonitor(Monitor):
    def __init__(self, label, config, notifiers):
        super().__init__("download", label, config, notifiers)

        self.url = config['url']
        self.timeout = float(config.get('timeout', 10))
        self.headers = config.get('headers', {})
        if bool(config.get('ssl', True)):
            self.ssl = None
        else:
            self.ssl = ssl.SSLContext()

    # ping a server, returns data number of packets send, and round trip times
    def check(self):
        self.logger.debug(f"Downloading {self.url}")

        download_start = time.time_ns()
        download_bytes = 0
        try:
            self.logger.debug(f"Attempting to download from {self.url}...")
            req = urllib.request.Request(self.url, headers=self.headers)
            res = urllib.request.urlopen(req, timeout=self.timeout, context=self.ssl)
            while True:
                chunk = res.read(1_000_000)
                if not chunk:
                    break
                download_bytes += len(chunk)
            self.logger.debug(f"Download success: {self.url}")
            download_diff = (time.time_ns() - download_start) / 1.0e9
            message = f"Finished download {download_bytes} in {download_diff:.3} seconds"
            result = 'success'
            data = {
                "bytes": download_bytes,
                "time": download_diff,
                "speed": (8 * download_bytes / 1_000_000) / download_diff
            }
        except:
            self.logger.exception(f"Download failed: {self.url}")
            download_diff = (time.time_ns() - download_start) / 1.0e9
            message = f"Failed to download the file"
            result = 'failure'
            data = {
                "bytes": download_bytes,
                "time": download_diff,
                "speed": 0,
            }

        return self.report(result, message, data)
