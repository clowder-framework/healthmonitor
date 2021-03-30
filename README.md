

We run a health monitor service periodically fetch the statistics data of Clowder service, e.g., response time of ping Clowder website.
response time of download Clowder website and bytes of homepage.

Uptime of Clowder website: The uptime of Clowder website can ensure we understand the liveness of Clowder service and this metric will be collected by sending ping to the target Clowder website with a certain timeout.

Response time: We collect the statistics of the response time of the ping command. And the elapsed time of downloading Clowder homepage.


# Run from Python Script
```
python ./healthmonitor.py --server https://clowderhost/clowder --downloadurl https://clowderhost/clowder --healthz_url https://clowderhost/clowder/healthz --report_url http://simpl-eventbus-api-host/service --report_apikey api_key --sleep_timer_sec 10 --ping_wait_sec 10 --request_timeout 60
```

# Docker Build and Run
```
cd health-monitor
docker build -t healthmonitor .
docker run -it --rm -e "PING_URL=clowderhost" -e "HEALTHZ_URL=https://clowderhost/clowder/healthz" -e "DOWNLOAD_WEBPAGE_URL=https://clowderhost/clowder" -e "REPORT_URL=http://simpl-eventbus-api/service" -e "REPORT_APIKEY=api_key" -e "REQUEST_TIMEOUT=60" -e "SLEEP_TIMER_SEC=10" -e "PING_WAIT_SEC=10" -v ${PWD}/total.txt:/total.txt healthmonitor
```



