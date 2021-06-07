import logging
import requests
import socket
import subprocess
import time


# ping a server, returns data number of packets send, and round trip times
def ping(label, config):
    host = config['host']
    max_count = 5 if 'count' not in config else config['count']
    sleep = 60 if 'sleep' not in config else config["sleep"]
    count = 0

    results = []
    failure_count = 0

    logging.debug("Running " + str(max_count) + " pings to " + host)

    while count < max_count:
        # sleep between ping attempts
        time.sleep(sleep)

        data = {}

        logging.debug(f"Attempt #" + str(count + 1) + " - pinging " + str(host) + "...")


        try:
            # ping server
            output = subprocess.getstatusoutput(f"ping -c {max_count} -W 1 {host}")
            data["status"] = output[0]
            lines = output[1].split("\n")
            idx = -1

            # parse round-trip information
            if "round-trip" in lines[idx]:
                timing = lines[-1].split()[3].split('/')
                timing_unit = lines[idx].split()[-1]
                data['packets'] = config['count']
                data['unit'] = timing_unit
                data['min'] = float(timing[0])
                data['avg'] = float(timing[1])
                data['max'] = float(timing[2])
                idx -= 1

            # parse loss information
            if "packet loss" in lines[idx]:
                data["loss"] = float(lines[idx].split()[6][:-1])
                idx -= 1

            logging.debug(host + ": " + "ping success! (" + str(count) + " / " + str(max_count) + ")")

            data["state"] = 'success'
        except Exception as e:
            logging.debug(host + ": " + "ping failed! (" + str(count) + " / " + str(max_count) + ")")

            data["state"] = 'failure'
            data["loss"] = 100
            failure_count += 1

        results.append(data)

    status = 'failure' if failure_count > 0 else 'success'
    return {'status': status, 'results': results, 'label': label, 'host': host}


def hostport(label, config):
    host = config['host']
    port = config['port']
    timeout = 30 if 'timeout' not in config else config['timeout']
    result = {'status': 'failure', 'label': label, 'host': host, 'port': port}

    connection = None
    try:
        logging.debug(f"Attempting to connect (" + label + "): " + str(host) + ":" + str(port) + "...")
        connection = socket.create_connection((host, port), timeout)
        result['status'] = 'success'
        logging.debug(f"Connection success (" + label + "): " + str(host) + ":" + str(port))
    except:
        logging.error(f"Could not connect to " + label + "): " + str(host) + ":" + str(port))
        return result
    finally:
        if connection is not None:
            connection.shutdown
            connection.close()

    return result


# download (and discard the data), return speed of download
def download_data(label, config): # url, headers=None, timeout=30):
    start = time.time_ns()
    download_bytes = 0
    url = config['url']
    timeout = 30 if 'timeout' not in config else config['timeout']
    headers = [] if 'headers' not in config else config['headers']
    try:
        logging.debug(f"Attempting to download from " + str(url) + "...")
        r = requests.get(url, headers=headers, stream=True, timeout=timeout)
        r.raise_for_status()
        logging.debug(f"Download success: " + str(url) + "...")
    except:
        errtime = (time.time_ns() - start) / 1.0e9
        return {'status': 'failure', 'bytes': 0, 'time': errtime, 'speed': 0}
    for chunk in r.iter_content(chunk_size=1_000_000):
        download_bytes += len(chunk)
    diff = (time.time_ns() - start) / 1.0e9
    return {
        "status": "success",
        "label": label,
        "url": url,
        "bytes": download_bytes,
        "time": diff,
        "speed": (8 * download_bytes / 1_000_000) / diff
    }
