FROM python:3.9-alpine

# CONFIG, NOTIFIERS, CHECKS are strings with YAML
# CONFIG_FILE, NOTIFIERS_FILE, CHECKS_FILE are filenames
# HEALTHMONITOR_CONFIG_FILE is deprecated, use CONFIG_FILE
ENV CONFIG="" \
    CONFIG_FILE="" \
    NOTIFIERS="" \
    NOTIFIERS_FILE="" \
    CHECKS="" \
    CHECKS_FILE="" \
    HEALTHMONITOR_CONFIG_FILE=""

WORKDIR /src
COPY requirements.txt ./
RUN pip3 install -r ./requirements.txt

COPY . ./

CMD python3 ./healthmonitor.py 
