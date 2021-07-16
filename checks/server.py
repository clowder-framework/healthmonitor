import logging
import requests
import time

logger = logging.getLogger(__name__)


# download (and discard the data), return speed of download
def download_data(label, config): # url, headers=None, timeout=30):
    start = time.time_ns()
    download_bytes = 0
    url = config['url']
    timeout = 30 if 'timeout' not in config else config['timeout']
    headers = [] if 'headers' not in config else config['headers']
    result = 'success'
    try:
        logger.debug(f"Attempting to download from " + str(url) + "...")
        r = requests.get(url, headers=headers, stream=True, timeout=timeout)
        r.raise_for_status()
        logger.debug(f"Download success: " + str(url) + "...")
        for chunk in r.iter_content(chunk_size=1_000_000):
            download_bytes += len(chunk)
    except:
        result = 'failure'
    return {
        "status": "success",
        "check": "download",
        "label": label,
        "url": url,
        "bytes": download_bytes,
        "time": (time.time_ns() - start) / 1.0e9,
        "speed": (8 * download_bytes / 1_000_000) / diff
    }
