FROM alpine:3.12

ENV PING_URL="" \
    DOWNLOAD_WEBPAGE_URL="" \
    REPORT_URL="" \
    REPORT_APIKE=""

RUN apk add --no-cache python3 py3-pip

COPY *.py requirements.txt /

RUN pip3 install --upgrade  -r requirements.txt

CMD python3 /healthmonitor.py --server $PING_URL --downloadurl $DOWNLOAD_WEBPAGE_URL --report_url $REPORT_URL --report_apikey $REPORT_APIKEY
