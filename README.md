# Hetzner Cloud | Snapshot-as-Backup  
This script automatically creates snapshots of your Hetzner Cloud Servers and deletes the old ones.  
Snapshots then work like the automatic backups offered directly by Hetzner, with the advantage that more backups and at self-defined times can be created.  

- [Installation](#installation)
- [Run script](#run-script)
- [Why is this script useful?](#why-is-this-script-useful)

## Installation
**1. Clone this repository**  
```
apt install git
git clone https://github.com/fbrettnich/hcloud-snapshot-as-backup.git /opt/hcloud-snapshot-as-backup
```

**2. Install requirements**  
```
apt install python3 python3-pip
pip3 install -r /opt/hcloud-snapshot-as-backup/requirements.txt
```

**3. Copy config.json**  
```
cd /opt/hcloud-snapshot-as-backup/
cp config.json.example config.json
```

**4. Generate Hetzner Cloud Console API-Key**  
1. Login to [Hetzner Cloud Console](https://console.hetzner.cloud/)
2. Select your project
3. Click "Access" on the left side
4. Switch to "API-Tokens" at the top
5. Click on "Create API Token" and create a new token with read & write permission
6. Copy the key and paste it into the config under `api-token`

**5. Choose how many backups you want to keep**  
You can specify in the config under `keep-last` how many backups you want to keep per server.  
The newest ones are kept and old ones are deleted.  

**6. Choose a server mode and set servers**  
The script supports two different modes:  
- **exclude**  
  - All servers are selected, except servers in the specified list  
- **only**  
  - Only the servers from the list are used, all others are ignored  

You can set the preferred mode in the config under `mode`.

**7. Add your servers to the list (optional)**  
According to the selected mode, you can set your Server IDs in the config under `servers`.

**8. Choose a name for your snapshots (optional)**  
Specify what you want your snapshots to be called in the config under `snapshot-name`.  
By default they are named `<server name>-<timestamp>`.  

| Placeholder | Value               |
| ----------- | ------------------- |
| %id%        | ID of the server    |
| %name%      | Name of the server  |
| %timestamp% | Current timestamp   |


## Run script
```
python3 /opt/hcloud-snapshot-as-backup/snapshot-as-backup.py
```

To execute the script automatically, you can create a crontab: [Crontab Generator](https://crontab-generator.org/)  
```
0 1 * * * python3 /opt/hcloud-snapshot-as-backup/snapshot-as-backup.py >/dev/null 2>&1
```
This crontab executes the script every day at 1am.

## Why is this script useful?
| Advantages                                                            | Disadvantages                                                       |
| --------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Snapshot Backups can be created at own times (Backups at given time)  | Snapshots are limited (but higher limit can be requested)           |
| Any number can be kept (Backups only maximum 3)                       | May be more expensive for extremely large servers (lots of storage) |
| Are not server bound                                                  |                                                                     |
| Are cheaper than backups for smaller servers (little storage space)   |                                                                     |
| New servers can be created directly from the snapshot                 |                                                                     |
