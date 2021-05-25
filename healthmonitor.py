import argparse
import json
import logging
import os
import subprocess
import sys
import threading
import time

import requests


# logic of the code:
# ech of the checkers runs in their own thread and will send the results to the response app
# - ping_server:
#   - checks to see if the server is pingable
#   - reports {#pings, loss, and round trip time}
# - clowder_healthy:
#   - checks to see if clowder claims to be healthy
#   - reports {health: 1/0}
# - clowder_homepage:
#   - checks to see if clowder home page can be downloaded
#   - returns {status: 1/0, size: X}
# - clowder_download:
#   - checks to see if a file can be downloaded
#   - reports {status: 1/0, size: X, speed: Y (Mbps)}


# helper to report data
def report_result(report_url, report_key, measurement, values, tags=None):
    if not values:
        return
    if tags:
        data = json.dumps({"measurement": measurement, "tags": tags, "values": values})
    else:
        data = json.dumps({"measurement": measurement, "values": values})
    if not report_url or not report_key:
        print(data)
    else:
        try:
            r = requests.post(report_url,
                              headers={"Content-Type": "application/json", "API-KEY": report_key},
                              data=data)
            r.raise_for_status()
        except Exception as e:
            logging.exception("Error uploading result, data is lost")


# download (and discard the data), return speed of download
def download_data(url, headers=None, timeout=30):
    start = time.time_ns()
    bytes = 0
    print(url)
    r = requests.get(url, headers=headers, stream=True, timeout=timeout)
    r.raise_for_status()
    for chunk in r.iter_content(chunk_size=1_000_000):
        bytes += len(chunk)
    diff = (time.time_ns() - start) / 1.0e9
    return {
        "bytes": bytes,
        "time": diff,
        "speed": (8 * bytes / 1_000_000) / diff
    }


# ping a server, returns data number of packets send, and round trip times
def ping_server(**kwargs):
    tags = {"server": kwargs['ping_host']}
    while True:
        data = {}

        try:
            # ping server
            output = subprocess.getstatusoutput(f"ping -c {kwargs['ping_count']} -W 1 {kwargs['ping_host']}")
            data["status"] = output[0]
            lines = output[1].split("\n")
            idx = -1

            # parse round-trip information
            if "round-trip" in lines[idx]:
                timing = lines[-1].split()[3].split('/')
                timing_unit = lines[idx].split()[-1]
                data['packets'] = kwargs['ping_count']
                data['unit'] = timing_unit
                data['min'] = float(timing[0])
                data['avg'] = float(timing[1])
                data['max'] = float(timing[2])
                idx -= 1

            # parse loss information
            if "packet loss" in lines[idx]:
                data["loss"] =  float(lines[idx].split()[6][:-1])
                idx -= 1

        except Exception as e:
            logging.exception(f"Could not ping server.")
            data["status"] = 999
            data["loss"] = 100

        # send response to server
        report_result(kwargs["report_url"], kwargs["report_apikey"], "ping", data, tags)

        # sleep
        time.sleep(kwargs["ping_sleep_sec"])


# check to see if clowder claims to be healthy
def clowder_healthy(**kwargs):
    while True:
        data = {}

        data['healthy'] = 0
        try:
            # check clowder healtz
            r = requests.get(f"{kwargs['clowder_url']}healthz", timeout=kwargs['clowder_timeout_sec'])
            r.raise_for_status()

            if r.text == "healthy":
                data['healthy'] = 1
        except:
            logging.debug("could not check health")
            pass

        # send response to server
        report_result(kwargs["report_url"], kwargs["report_apikey"], "healthz", data)

        # sleep
        time.sleep(kwargs["ping_sleep_sec"])


# download clowder homepage
def clowder_homepage(**kwargs):
    # download homepage and report, using streaming protocol
    while True:
        try:
            data = download_data(kwargs['clowder_url'], None, kwargs["clowder_timeout_sec"])
            # send response to server
            report_result(kwargs["report_url"], kwargs["report_apikey"], "homepage", data)
        except Exception as e:
            logging.exception(f"Could not download file {e}")
            pass
        # sleep
        time.sleep(kwargs["clowder_sleep_sec"])


# download a file from clowder
def clowder_download(**kwargs):
    headers = {}
    tags = {}
    if kwargs['clowder_key']:
        headers['X-API-Key'] = kwargs['clowder_key']
    if args.clowder_file_id:
        url = f"{args.clowder_url}api/files/{args.clowder_file_id}/blob"
        tags["asset"] = args.clowder_file_id
    else:
        url = f"{args.clowder_url}assets/javascripts/previewers/pdf/pdf.js"
        tags["asset"] = "pdf.js"

    # download file and report, using streaming protocol
    while True:
        try:
            data = download_data(url, headers, kwargs["clowder_timeout_sec"])
            # send response to server
            report_result(kwargs["report_url"], kwargs["report_apikey"], "download", data, tags)
        except Exception as e:
            logging.exception(f"Could not download file {e}")
            pass
        # sleep
        time.sleep(kwargs["clowder_file_sleep_sec"])


if __name__ == '__main__':
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(level=logging.INFO,
                        datefmt='%Y-%m-%dT%H:%M:%S',
                        format='%(asctime)-15s.%(msecs)03dZ %(levelname)-7s [%(threadName)-10s] : %(name)s - %(message)s')
    logging.getLogger("requests.packages.urllib3").setLevel(logging.WARNING)

    parser = argparse.ArgumentParser()

    parser.add_argument("--clowder_url",
                        default=os.environ.get("CLOWDER_URL", "http://localhost:9000/"),
                        help="home page of clowder")
    parser.add_argument("--clowder_sleep_sec",
                        type=int,
                        default=int(os.environ.get("CLOWDER_SLEEP_SEC", 60)),
                        help="how long to wait between consecutive checks of clowder")
    parser.add_argument("--clowder_key",
                        default=os.environ.get("CLOWDER_KEY", None),
                        help="key to download file if needed")
    parser.add_argument("--clowder_file_id",
                        default=os.environ.get("CLOWDER_FILE_ID", None),
                        help="file to download from clowder, if not specified will download other large object")
    parser.add_argument("--clowder_file_sleep_sec",
                        type=int,
                        default=int(os.environ.get("CLOWDER_FILE_SLEEP_SEC", "3600")),
                        help="how long to wait between consecutive downloads in seconds")
    parser.add_argument("--clowder_timeout_sec",
                        type=int,
                        default=int(os.environ.get("CLOWDER_TIMEOUT_SEC", "30")),
                        help="request timeout")

    parser.add_argument("--ping_host",
                        default=os.environ.get("PING_HOST", "localhost"),
                        help="Clowder server to ping")
    parser.add_argument("--ping_count",
                        type=int,
                        default=int(os.environ.get("PING_COUNT", "30")),
                        help="ping command number of tries")
    parser.add_argument("--ping_sleep_sec",
                        type=int,
                        default=int(os.environ.get("PING_SLEEP_SEC", "69")),
                        help="how long to wait between consecutive ping commands")

    parser.add_argument("--report_url", default=os.environ.get("REPORT_URL", "http://localhost:5000"),
                        help="website url to report the status")
    parser.add_argument("--report_apikey", default=os.environ.get("REPORT_APIKEY", "api-key"),
                        help="apikey t0 authorize the post data")

    args = parser.parse_args()

    threads = list()

    # ping server
    if args.ping_host:
        thread = threading.Thread(target=ping_server, kwargs=vars(args))
        thread.start()
        threads.append(thread)

    # if clowder url given
    if args.clowder_url:
        # check if clowder is healthy
        thread = threading.Thread(target=clowder_healthy, kwargs=vars(args))
        thread.start()
        threads.append(thread)

        # download clowder homepage
        thread = threading.Thread(target=clowder_homepage, kwargs=vars(args))
        thread.start()
        threads.append(thread)

        # try download file from clowder
        thread = threading.Thread(target=clowder_download, kwargs=vars(args))
        thread.start()
        threads.append(thread)

    # keep running, and die if any thread stops
    while True:
        for thread in threads:
            if not thread.is_alive():
                sys.exit(1)
        time.sleep(1)
