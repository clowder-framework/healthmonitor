FROM python:3.7-alpine

#    CLOWDER_KEY="4e1acfe7-bd4d-4a5c-8035-a3e544c46154" \
#    CLOWDER_FILE_ID="607e6e325e0e57a46506f0f0" \
ENV CLOWDER_URL="https://clowder.ncsa.illinois.edu/clowder/" \
    CLOWDER_SLEEP_SEC="60" \
    CLOWDER_KEY="" \
    CLOWDER_FILE_ID="" \
    CLOWDER_FILE_SLEEP_SEC="3600" \
    CLOWDER_TIMEOUT_SEC="30" \
    PING_HOST="clowder.ncsa.illinois.edu" \
    PING_COUNT="5" \
    PING_SLEEP_SEC="60" \
    REPORT_URL="" \
    REPORT_APIKEY="api-key"

WORKDIR /src
COPY requirements.txt ./
RUN pip3 install -r ./requirements.txt
COPY *.py ./

CMD python3 ./healthmonitor.py 
