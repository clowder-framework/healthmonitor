import argparse
import requests
import datetime
import subprocess

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


def download_clowderhomepage(server):
    success = True
    bytes = -1
    response = requests.get(server)
    try:
        response.raise_for_status()
        bytes = len(response.content)
    except Exception as e:
        success = False
    return {"success": success, "bytes": bytes}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="localhost:9000", help="Clowder website url")
    parser.add_argument("--downloadurl", default="localhost:9000", help="download url of web page")
    parser.add_argument("--ping_wait_sec", default=1, help="ping command default wait time in second")
    args = parser.parse_args()
    print(args.server)
    response_time = responsetime_clowder(args.server, args.ping_wait_sec)
    print(response_time)
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
    if response_time.get('loss') == '0%':
        liveness += 1
    uptime = float(liveness)/total_runs
    print("uptime: %f" % uptime)

    with open("./total.txt", 'w') as filetowrite:
        filetowrite.write(str(total_runs))

    download_homepage_status = download_clowderhomepage(args.downloadurl)
    print(download_homepage_status)
