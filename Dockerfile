FROM python:3.7-alpine

ENV HEALTHMONITOR_CONFIG_FILE="config.yml"

WORKDIR /src
COPY requirements.txt ./
RUN pip3 install -r ./requirements.txt

COPY . ./

CMD python3 ./healthmonitor.py 
