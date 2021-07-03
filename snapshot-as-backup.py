# Copyright (c) 2021 Felix Brettnich
# Licensed under MIT (https://github.com/fbrettnich/hcloud-snapshot-as-backup/blob/main/LICENSE)

import os
import sys
import json
import time
import requests

base_url = "https://api.hetzner.cloud/v1"
servers = {}


def get_servers(page=1):
    url = base_url + "/servers?page=" + str(page)
    r = requests.get(url=url, headers=headers)

    if not r.ok:
        print(f"Servers Page #{page} could not be retrieved: {r.reason}")
        print(r.text)

    else:
        r = r.json()
        np = r['meta']['pagination']['next_page']

        for s in r['servers']:
            if config['mode'] == "exclude":
                if s['id'] not in config['servers']:
                    servers[s['id']] = s

            elif config['mode'] == "only":
                if s['id'] in config['servers']:
                    servers[s['id']] = s

        if np is not None:
            get_servers(np)


def create_snapshot(server_id, snapshot_desc):
    url = base_url + "/servers/" + str(server_id) + "/actions/create_image"
    r = requests.post(
        url=url,
        json={"description": snapshot_desc, "type": "snapshot"},
        headers=headers
    )

    if not r.ok:
        print(f"Snapshot for Server #{server_id} could not be created: {r.reason}")
        print(r.text)
    else:
        image_id = r.json()['image']['id']
        print(f"Snapshot #{image_id} (Server #{server_id}) has been created")


def cleanup_snapshots(keep_last):
    url = base_url + "/images?type=snapshot"
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
            if len(si) > keep_last:
                si.sort(reverse=True)
                si = si[keep_last:]

                for s in si:
                    if config['mode'] == "exclude":
                        if k not in config['servers']:
                            delete_snapshots(snapshot_id=s, server_id=k)

                    elif config['mode'] == "only":
                        if k in config['servers']:
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

    if config['mode'] != "exclude" and config['mode'] != "only":
        print(f"Invalid server mode: {config['mode']}")
        print("Possible modes: exclude, only")
        sys.exit(1)

    get_servers()

    for server in servers:
        create_snapshot(
            server_id=server,
            snapshot_desc=str(config['snapshot-name'])
                .replace("%id%", str(servers[server]['id']))
                .replace("%name%", servers[server]['name'])
                .replace("%timestamp%", str(int(time.time())))
        )
        cleanup_snapshots(keep_last=config['keep-last'])
