import logging
import requests
import time

from healthmonitor import notifiers
import server


# check to see if clowder claims to be healthy
def healthy(**kwargs):
    while True:
        data = {'healthy': 0}

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
        notifiers.utils.report_result(kwargs["report_url"], kwargs["report_apikey"], "healthz", data)

        # sleep
        time.sleep(kwargs["ping_sleep_sec"])


# download clowder homepage
def homepage(**kwargs):
    # download homepage and report, using streaming protocol
    while True:
        try:
            data = server.download_data(kwargs['clowder_url'], None, kwargs["clowder_timeout_sec"])
            # send response to server
            notifiers.utils.report_result(kwargs["report_url"], kwargs["report_apikey"], "homepage", data)
        except Exception as e:
            logging.exception(f"Could not download file {e}")
            pass
        # sleep
        time.sleep(kwargs["clowder_sleep_sec"])


# download a file from clowder
def download_file(**kwargs):
    headers = {}
    tags = {}
    if kwargs['clowder_key']:
        headers['X-API-Key'] = kwargs['clowder_key']
    if kwargs['clowder_file_id']:
        url = f"{kwargs['clowder_url']}api/files/{kwargs['clowder_file_id']}/blob"
        tags["asset"] = kwargs['clowder_file_id']
    else:
        url = f"{kwargs['clowder_url']}assets/javascripts/previewers/pdf/pdf.js"
        tags["asset"] = "pdf.js"

    # download file and report, using streaming protocol
    while True:
        try:
            data = server.download_data(url, headers, kwargs["clowder_timeout_sec"])
            # send response to server
            notifiers.utils.report_result(kwargs["report_url"], kwargs["report_apikey"], "download", data, tags)
        except Exception as e:
            logging.exception(f"Could not download file {e}")
            pass
        # sleep
        time.sleep(kwargs["clowder_file_sleep_sec"])
