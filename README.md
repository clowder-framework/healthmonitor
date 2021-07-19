

We run a health monitor service periodically fetch the statistics data of Clowder service, e.g., response time of ping Clowder website.
response time of download Clowder website and bytes of homepage.

Uptime of Clowder website: The uptime of Clowder website can ensure we understand the liveness of Clowder service and this metric will be collected by sending ping to the target Clowder website with a certain timeout.

Response time: We collect the statistics of the response time of the ping command. And the elapsed time of downloading Clowder homepage.


# Configuration
The config file is split into two sections: `checks` and `notifiers`

The `checks` section defines what tests we are running against which server targets. This section supports various checks:

* `ping` - periodically run a `ping` against the target server to verify that the host is still responding
* `hostport` - periodically attempt to connect to the target `host` / `port` to verify that the port is still alive
* `filewrite` - periodically tries to write to a file on disk
  
Coming soon:
* `download` - periodically attempt to download bytes from the target url to verify that it is still serving files or data

The `notifiers` section then tells us which mediums should receive our reports about the success and/or failure of those tests. This section supports various suptypes:
* `console` - print successes and/or failure to the console
* `email` - send the success/failure message as an e-mail
* `influxdb` - send success/failure message to influxdb. (requires `hostname`, `port`, `database`)
* `slack` - send the success/failure message to a Slack channel. (requires a `webhook` url)

Coming soon:
* `msteams` - send the success/failure message to a MS Teams channel
* `rabbitmq` - send the success/failure message to a RabbitMQ queue (e.g. Clowder's eventsink)
* `mongo` - store the success/failure message in a MongoDB collection

Notifiers can be configured when to send their message:
* `always` - send a message for each check
* `change` - when the status of the check changes
* `failure` - only send failure messages

`change` and `failure` are only send if the number of messages crosses the threshold set for the notifier.


An example configuration file is provided below:
```yaml
notifiers:
  # DEBUG only: report all successes and failures to the console
  console:
    report: change
    threshold: 0

  # report only failures to Slack, and only when consecutive failures > 600
  slack:
    report: failure
    threshold: 600
    # required
    webhook: https://hooks.slack.com/services/some/secret/code
    # optional?
    channel: alerts
    user: alert-bot
checks:
  ping:
    # verify that server is online
    clowder:
      host: clowder.ncsa.illinois.edu
      # optional
      count: 5
      timeout: 30
      sleep: 60
    # verify general network connectivity of healthmonitor (sanity check)
    google:
      host: google.com
      # optional
      count: 3
      timeout: 30
      sleep: 600
  hostport:
    # verify that server
    clowder:
      # required
      host: localhost
      port: 9000
      # optional
      sleep: 10
      timeout: 5
  download:
    clowder:
      url: "http://localhost:9000"
      # optional
      sleep: 900
      threshold: 2
      timeout: 5

```


## Usage (Docker)
Mount in your config file and run a container from the Docker image:
```bash
docker run -it --rm -v $(pwd)/config.yml:/src/confg.yml clowder/healthmonitor
```

The image should be automatically downloaded if it is not already present on your machine

### Optional: Rebuild Docker Image
If you modify the Python source, the Docker image will need to be rebuilt for new containers to reflect the new changes:
```bash
docker build -t clowder/healthmonitor .
```

## Usage (Python)
To get started developing, create and activate a `virtualenv`:
```bash
virtualenv
source venv/bin/activate
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Finally, run the script and pass it the path to the config file:
```bash
python ./healthmonitor.py --config-file config.yml
```


## TODOs
* Error-handling during parse / checks
* Add more notifier types
* Better explanation of config file format
