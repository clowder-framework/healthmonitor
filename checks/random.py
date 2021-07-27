import random

from checks.monitor import Monitor


class RandomMonitor(Monitor):
    def __init__(self, label, config, notofiers):
        super().__init__("filewrite", label, config, notofiers)

        self.random = random.Random(int(config.get("seed", "0")))
        self.mark = float(config.get("mark", "0.5"))
        self.count = 0

    def check(self):
        self.count += 1
        v = self.random.random()
        if v > self.mark:
            message = f"[{self.count:5}] value is ok  {v} >  {self.mark}"
            result = 'success'
        else:
            message = f"[{self.count:5}] value is bad {v} <= {self.mark}"
            result = 'failure'

        return self.report(result, message, {"value": v, "mark": self.mark})
