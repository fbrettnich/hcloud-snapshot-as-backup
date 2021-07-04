# Copyright (c) 2021 Felix Brettnich
# Licensed under MIT (https://github.com/fbrettnich/hcloud-snapshot-as-backup/blob/main/LICENSE)

import os
import json
import time
import requests

base_url = "https://api.hetzner.cloud/v1"
servers = {}
servers_keep_last = {}


def get_servers(page=1):
    url = base_url + "/servers?label_selector=AUTOBACKUP=true&page=" + str(page)
    r = requests.get(url=url, headers=headers)

    if not r.ok:
        print(f"Servers Page #{page} could not be retrieved: {r.reason}")
        print(r.text)

    else:
        r = r.json()
        np = r['meta']['pagination']['next_page']

        for s in r['servers']:
            servers[s['id']] = s

            keep_last = config['keep-last']
            if "AUTOBACKUP.KEEP-LAST" in s['labels']:
                keep_last = int(s['labels']['AUTOBACKUP.KEEP-LAST'])

            if keep_last < 1:
                keep_last = 1

            servers_keep_last[s['id']] = keep_last

        if np is not None:
            get_servers(np)


def create_snapshot(server_id, snapshot_desc):
    url = base_url + "/servers/" + str(server_id) + "/actions/create_image"
    r = requests.post(
        url=url,
        json={"description": snapshot_desc, "type": "snapshot", "labels": {"AUTOBACKUP": ""}},
        headers=headers
    )

    if not r.ok:
        print(f"Snapshot for Server #{server_id} could not be created: {r.reason}")
        print(r.text)
    else:
        image_id = r.json()['image']['id']
        print(f"Snapshot #{image_id} (Server #{server_id}) has been created")


def cleanup_snapshots():
    url = base_url + "/images?type=snapshot&label_selector=AUTOBACKUP"
    r = requests.get(url=url, headers=headers)

    if not r.ok:
        print(f"Snapshots could not be retrieved: {r.reason}")
        print(r.text)

    else:
        sl = {}
        for i in r.json()['images']:
            if i['created_from']['id'] in sl:
                sl[i['created_from']['id']].append(i['id'])
            else:
                sl[i['created_from']['id']] = [i['id']]

        for k in sl:
            si = sl[k]
            keep_last = config['keep-last']

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


if __name__ == '__main__':

    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.json"), "r") as config_file:
        config = json.load(config_file)

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + config['api-token'],
    }

    get_servers()

    for server in servers:
        create_snapshot(
            server_id=server,
            snapshot_desc=str(config['snapshot-name'])
                .replace("%id%", str(server))
                .replace("%name%", servers[server]['name'])
                .replace("%timestamp%", str(int(time.time())))
        )

    cleanup_snapshots()
