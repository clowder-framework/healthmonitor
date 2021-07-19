import datetime

from checks.monitor import Monitor


class FileWriteMonitor(Monitor):
    def __init__(self, label, config, notofiers):
        super().__init__("filewrite", label, config, notofiers)

        self.file = config['file']
        self.data = {"ok": 0, "fail": 0, "total": 0}

    def check(self):
        self.data['total'] += 1
        try:
            with open(self.file, "w") as f:
                f.write(f"{datetime.datetime.now()} : ok={self.data['ok']+1} fail={self.data['fail']}\n")
            result = 'success'
            self.data['ok'] += 1
            self.data['state'] = 0
            message = f"Successfully wrote to {self.file}"
            self.logger.debug(f"Successfully wrote to {self.file}")
        except:
            message = f"Failed to write to {self.file}"
            result = 'failure'
            self.data['fail'] += 1
            self.data['state'] = 1
            self.logger.error(f"Could not write to ({self.name}-{self.label}): {self.file}")

        return self.report(result, message, self.data)
