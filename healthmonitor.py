import argparse
import requests
import datetime
import json
import threading
import subprocess
from time import sleep

def responsetime_clowder(server, wait_sec=1):
    cmd = "ping -c {} -W {} {}".format(1, wait_sec, server).split(' ')
    output = subprocess.check_output(cmd).decode().strip()
    lines = output.split("\n")
    # total = lines[-2].split(',')[3].split()[1]
    loss = lines[-2].split(',')[2].split()[0]
    timing = lines[-1].split()[3].split('/')
    timing_unit = lines[-1].split()[-1]
    response_time = {
            # 'type': 'rtt',
            'min': timing[0] + " " + timing_unit,
            'avg': timing[1] + " " + timing_unit,
            'max': timing[2] + " " + timing_unit,
            # 'mdev': timing[3],
            # 'total': total,
            'loss': loss,
        }
    return response_time

def clowder_healthy(server):
    healthy = False
    try:
        r = requests.get(server+"/healthz")
        r.raise_for_status()
        message = r.content.decode("utf-8")
        if message == "healthy":
            healthy = True
    except Exception as e:
        pass
    return healthy

def download_clowderhomepage(server):
    success = True
    bytes = -1
    try:
        response = requests.get(server)
        response.raise_for_status()
        bytes = len(response.content)
    except Exception as e:
        success = False
    return {"success": success, "bytes": bytes}

def ping_thread_func(server, ping_wait_sec, report_url, report_apikey):
    status = dict()
    healthy = clowder_healthy(server)
    status['healthy'] = healthy
    response_time = responsetime_clowder(server, ping_wait_sec)
    status['response_time'] = response_time
    # print(response_time)
    uptime = 0
    total_runs = 0
    with open("./total.txt", "r") as myfile:
        total = myfile.readlines()
    try:
        total_runs = int(total[0])
    except Exception as e:
        pass
    liveness = total_runs
    total_runs += 1
    if response_time.get('loss') == '0%' or response_time.get('loss') == '0.0%':
        liveness += 1
    uptime = float(liveness)/total_runs
    # print("uptime: %f" % uptime)
    status['uptime'] = uptime

    # print(status)
    try:
        r = requests.post(report_url, headers={"Content-Type": "application/json", "API-KEY": report_apikey},
                          data=json.dumps({"ping_status": status}))
        r.raise_for_status()
    except Exception as e:
        pass

    with open("./total.txt", 'w') as filetowrite:
        filetowrite.write(str(total_runs))

def download_homepage_thread_func(downloadurl, report_url, report_apikey):
    homepage_status = dict()
    try:
        download_homepage_status = download_clowderhomepage(downloadurl)
        # print(download_homepage_status)
        homepage_status['homepage_status'] = download_homepage_status
        try:
            r = requests.post(report_url, headers={"Content-Type": "application/json", "API-KEY": report_apikey},
                              data=json.dumps(homepage_status))
            r.raise_for_status()
        except Exception as e:
            pass
    except Exception as e:
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="localhost:9000", help="Clowder website url")
    parser.add_argument("--report_url", default="localhost:5000", help="website url to report the status")
    parser.add_argument("--report_apikey", default="api-key", help="apikey t0 authorize the post data")
    parser.add_argument("--sleep_timer_sec", default=1, help="sleep time in second between each run")
    parser.add_argument("--downloadurl", default="localhost:9000", help="download url of web page")
    parser.add_argument("--ping_wait_sec", default=1, help="ping command default wait time in second")
    args = parser.parse_args()
    print(args.server)

    while (True):
        threads = list()
        ping_thread = threading.Thread(target=ping_thread_func, args=(args.server, args.ping_wait_sec, args.report_url,
                                                                      args.report_apikey))
        download_thread = threading.Thread(target=download_homepage_thread_func, args=(args.downloadurl,args.report_url,
                                                                                       args.report_apikey,))
        threads.append(ping_thread)
        threads.append(download_thread)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        sleep(args.sleep_timer_sec)