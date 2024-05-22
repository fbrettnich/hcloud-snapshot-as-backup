# Licensed under MIT (https://github.com/fbrettnich/hcloud-snapshot-as-backup/blob/main/LICENSE)

import os
import sys
import json
import time
import requests
from cron_validator import CronScheduler

base_url = "https://api.hetzner.cloud/v1"
api_token = ""
snapshot_name = ""
label_selector = ""
keep_last_default = 3
headers = {}
servers = {}
servers_keep_last = {}
snapshot_list = {}


def get_servers(page=1):
    url = base_url + f"/servers?label_selector={label_selector}=true&page=" + str(page)
    r = requests.get(url=url, headers=headers)

    if not r.ok:
        print(f"Servers Page #{page} could not be retrieved: {r.reason}")
        print(r.text)

    else:
        r = r.json()
        np = r['meta']['pagination']['next_page']

        for s in r['servers']:
            servers[s['id']] = s

            keep_last = keep_last_default
            if f"{label_selector}.KEEP-LAST" in s['labels']:
                keep_last = int(s['labels'][f"{label_selector}.KEEP-LAST"])

            if keep_last < 1:
                keep_last = 1

            servers_keep_last[s['id']] = keep_last

        if np is not None:
            get_servers(np)


def create_snapshot(server_id, snapshot_desc):
    url = base_url + "/servers/" + str(server_id) + "/actions/create_image"
    r = requests.post(
        url=url,
        json={"description": snapshot_desc, "type": "snapshot", "labels": {f"{label_selector}": ""}},
        headers=headers
    )

    if not r.ok:
        print(f"Snapshot for Server #{server_id} could not be created: {r.reason}")
        print(r.text)
    else:
        image_id = r.json()['image']['id']
        print(f"Snapshot #{image_id} (Server #{server_id}) has been created")


def get_snapshots(page=1):
    url = base_url + f"/images?type=snapshot&label_selector={label_selector}&page=" + str(page)
    r = requests.get(url=url, headers=headers)

    if not r.ok:
        print(f"Snapshots Page #{page} could not be retrieved: {r.reason}")
        print(r.text)

    else:
        r = r.json()
        np = r['meta']['pagination']['next_page']

        for i in r['images']:
            if i['created_from']['id'] in snapshot_list:
                snapshot_list[i['created_from']['id']].append(i['id'])
            else:
                snapshot_list[i['created_from']['id']] = [i['id']]

        if np is not None:
            get_snapshots(np)


def cleanup_snapshots():
    for k in snapshot_list:
        si = snapshot_list[k]
        keep_last = keep_last_default

        if k in servers_keep_last:
            keep_last = servers_keep_last[k]

        if len(si) > keep_last:
            si.sort(reverse=True)
            si = si[keep_last:]

            for s in si:
                delete_snapshots(snapshot_id=s, server_id=k)


def delete_snapshots(snapshot_id, server_id):
    url = base_url + "/images/" + str(snapshot_id)
    r = requests.delete(url=url, headers=headers)

    if not r.ok:
        print(f"Snapshot #{snapshot_id} (Server #{server_id}) could not be deleted: {r.reason}")
        print(r.text)
    else:
        print(f"Snapshot #{snapshot_id} (Server #{server_id}) was successfully deleted")


def run():

    if api_token is None:
        print("API token is missing... Exit.")
        sys.exit(0)

    servers.clear()
    servers_keep_last.clear()
    snapshot_list.clear()
    headers['Content-Type'] = "application/json"
    headers['Authorization'] = "Bearer " + api_token

    get_servers()

    if not servers:
        print("No servers found with label")

    for server in servers:
        create_snapshot(
            server_id=server,
            snapshot_desc=str(snapshot_name)
            .replace("%id%", str(server))
            .replace("%name%", servers[server]['name'])
            .replace("%timestamp%", str(int(time.time())))
            .replace("%date%", str(time.strftime("%Y-%m-%d")))
            .replace("%time%", str(time.strftime("%H:%M:%S")))
        )

    get_snapshots()

    if not snapshot_list:
        print("No snapshots found with label")

    cleanup_snapshots()


if __name__ == '__main__':

    IN_DOCKER_CONTAINER = os.environ.get('IN_DOCKER_CONTAINER', False)

    if IN_DOCKER_CONTAINER:
        api_token = os.environ.get('API_TOKEN')
        snapshot_name = os.environ.get('SNAPSHOT_NAME', "%name%-%timestamp%")
        label_selector = os.environ.get('LABEL_SELECTOR', 'AUTOBACKUP')
        keep_last_default = int(os.environ.get('KEEP_LAST', 3))

        cron_string = os.environ.get('CRON', '0 1 * * *')

        if cron_string is False or cron_string.lower() == 'false':
            run()

        else:
            print(f"Starting CronScheduler [{cron_string}]...")
            cron_scheduler = CronScheduler(cron_string)

            while True:
                try:
                    if cron_scheduler.time_for_execution():
                        print("Script is now executed by cron...")
                        run()
                except KeyboardInterrupt:
                    sys.exit(0)

                time.sleep(1)

    else:
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.json"), "r") as config_file:
            config = json.load(config_file)

        label_selector = config['label-selector']
        api_token = config['api-token']
        snapshot_name = config['snapshot-name']
        keep_last_default = int(config['keep-last'])

        run()
