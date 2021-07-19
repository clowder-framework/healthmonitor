import subprocess

from checks.monitor import Monitor


class PingMonitor(Monitor):
    def __init__(self, label, config, notifiers):
        super().__init__("ping", label, config, notifiers)

        self.host = config['host']
        self.count = int(config.get('count', 5))
        self.loss = float(config.get('loss', 99))
        self.timeout = int(config.get('timeout', 30))

    # ping a server, returns data number of packets send, and round trip times
    def check(self):
        self.logger.debug(f"Running {self.count} pings to {self.host}")

        data = {
            'packets': self.count
        }

        try:
            # ping server
            output = subprocess.getstatusoutput(f"ping -c {self.count} -W 1 {self.host}")
            data["status"] = output[0]
            lines = output[1].split("\n")
            idx = -1

            # parse round-trip information
            if "round-trip" in lines[idx]:
                timing = lines[-1].split()[3].split('/')
                timing_unit = lines[idx].split()[-1]
                data['unit'] = timing_unit
                data['min'] = float(timing[0])
                data['avg'] = float(timing[1])
                data['max'] = float(timing[2])
                idx -= 1

            # parse loss information
            if "packet loss" in lines[idx]:
                data["loss"] = float(lines[idx].split()[6][:-1])
                idx -= 1
            else:
                data["loss"] = 0.0

        except Exception as e:
            data["loss"] = 100

        if data["loss"] < self.loss:
            data["state"] = 'success'
            self.logger.debug(f"{self.host}: ping success!")
            message = "Host is reachable."
        else:
            data["state"] = 'failure'
            self.logger.debug(f"{self.host}: ping failed! ({data['loss']}% packet loss)")
            message = f"Host is not reachable ({data['loss']}% packet loss)"

        return self.report(data["state"], message, data)
