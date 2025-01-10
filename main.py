#!/usr/bin/env python

from requests import get, put
import logging
import sys
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# this is just to make the output look nice
formatter = logging.Formatter(fmt="%(asctime)s %(name)s.%(levelname)s: %(message)s", datefmt="%Y.%m.%d %H:%M:%S")

# this logs to stdout and I think it is flushed immediately
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("Starting.")

targets = []
token = ""
zone = ""

with open("token") as f:
    token = f.read().strip()
with open("targets") as f:
    targets = f.read().strip().split("\n")
with open("zone") as f:
    zone = f.read().strip()

headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type": "application/json"
}

targets_set = set(targets)

logger.info("Successfully read token and zone.")

def get_records():
    record = get(
            url=f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records",
            headers=headers
            )
    if record.status_code != 200:
        logger.error("Could not get DNS record ID from CloudFlare!")
        return None

    res = record.json()["result"]

    return [(r["name"], r["content"], r["id"]) for r in res]

def get_bad_records(cur_ip):
    records_res = get_records()
    if records_res is None:
        logger.error("DNS record ID was undefined. Do nothing.")
        return
    
    records = [(name, ip, ident) for (name, ip, ident) in records_res if name in targets_set and ip != cur_ip]
    
    return records

def update_record(ident, name, new_ip):
    # update via cloudflare api
    payload = {
        "type": "A",
        "name": name, 
        "content": new_ip,
    }

    status = put(
            url=f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records/{ident}",
            headers=headers,
            json=payload)


    if status.status_code != 200:
        logger.error("ERROR: Could not update DNS record! Error is as follows:\n" + status.text)
    else:
        logger.info("Successfully updated DNS record.")

def update():
    try:
        cur_ip = get('https://api.ipify.org').content.decode('utf8')
    except Exception as e:
        logger.error("Error trying to get IP:\n" + str(e))
        return
    
    logger.info(f"Server IP: {cur_ip}")

    bad_records = get_bad_records(cur_ip)
    
    for name, bad_ip, ident in bad_records:
        logger.info(f"Hostname {name} has content {bad_ip}. Updating.")
        update_record(ident, name, cur_ip)

def main():
    # Run every minute
    interval = 60
    starttime = time.time()
    while True:
        try:
            update()
        except Exception as e:
            logger.error("Uncaught error in running:\n" + str(e)) 
        time.sleep(interval - ((time.time() - starttime) % interval))

if __name__ == "__main__":
    main()