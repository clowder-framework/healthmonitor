import socket

from checks.monitor import Monitor


class HostPortMonitor(Monitor):
    def __init__(self, label, config, notofiers):
        super().__init__("hostport", label, config, notofiers)

        self.host = config['host']
        self.port = int(config['port'])
        self.timeout = int(config.get('timeout', 30))

    def check(self):
        result = 'failure'

        connection = None
        try:
            self.logger.debug(f"Attempting to connect ({self.name}-{self.label}): {self.host}:{self.port}")
            connection = socket.create_connection((self.host, self.port), self.timeout)
            result = 'success'
            message = f"Successfully connected to {self.host}:{self.port}"
            data = {"connection": 1}
            self.logger.debug(f"Connection success ({self.name}-{self.label}): {self.host}:{self.port}")
        except:
            message = f"Failed to connected to {self.host}:{self.port}"
            data = {"connection": 0}
            self.logger.error(f"Could not connect to ({self.name}-{self.label}): {self.host}:{self.port}")
        finally:
            if connection is not None:
                #connection.shutdown()
                connection.close()

        return {
            "status": result,
            "check": self.name,
            "label": self.label,
            "message": message,
            "config": self.config,
            "measurement": data
        }
