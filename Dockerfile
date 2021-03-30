FROM ubuntu:20.04

ENV PING_URL="" \
    DOWNLOAD_WEBPAGE_URL="" \
    REPORT_URL="" \
    REPORT_APIKEY="" \
    SLEEP_TIMER_SEC="" \
    HEALTHZ_URL="" \
    REQUEST_TIMEOUT="" \
    PING_WAIT_SEC=""
    



RUN apt-get update &&\
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    iputils-ping \
    python3 \
    python-is-python3 \
    python3-pip \
    python-is-python3 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY *.py.txt /

CMD python3 /healthmonitor.py --server $PING_URL --downloadurl $DOWNLOAD_WEBPAGE_URL --report_url $REPORT_URL --request_timeout $REQUEST_TIMEOUT --report_apikey $REPORT_APIKEY --sleep_timer_sec $SLEEP_TIMER_SEC --ping_wait_sec $PING_WAIT_SEC --healthz_url $HEALTHZ_URL
