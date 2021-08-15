# Hetzner Cloud | Snapshot-as-Backup  
This script automatically creates snapshots of your Hetzner Cloud Servers and deletes the old ones.  
Snapshots then work like the automatic backups offered directly by Hetzner, with the advantage that more backups and at self-defined times can be created.  
For ease of use, the script works with the powerful labels directly in the Hetzner Cloud Console. Just add labels to the servers and you are done.  

- [Installation](#installation)
- [About Labels](#about-labels)
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
cp config-example.json config.json
```

**4. Generate Hetzner Cloud Console API-Key**  
1. Login to [Hetzner Cloud Console](https://console.hetzner.cloud/)
2. Select your project
3. Click "Access" on the left side
4. Switch to "API-Tokens" at the top
5. Click on "Create API Token" and create a new token with read & write permission
6. Copy the key and paste it into the config under `api-token`

**5. Choose how many backups you want to keep by default**  
You can specify in the config under `keep-last` how many backups you want to keep per server by default.  
Labels can be used to overwrite the default value directly in the Hetzner Cloud Console.  
Add the label `AUTOBACKUP.KEEP-LAST` with the value that should apply to the server.  
The newest ones are kept and old ones are deleted.  

**6. Add label to servers that should be backed up**  
All servers that should be included by the script and automatic snapshot backups should be created must have the label `AUTOBACKUP` with the value `true`.  

**7. Choose a name for your snapshots (optional)**  
Specify how you want your snapshots to be named under `snapshot-name` in the config.  
By default they are named `<server name>-<timestamp>`.  

| Placeholder | Value               |
| ----------- | ------------------- |
| %id%        | ID of the server    |
| %name%      | Name of the server  |
| %timestamp% | Current timestamp   |

## About Labels  
This script works with the powerful Hetzner Labels.  
- **Server**
  - `AUTOBACKUP`
    - Server with label `AUTOBACKUP` and value `true` are included by the script
    - This makes it possible to specify directly in the Hetzner Cloud Console for which servers automatic snapshot backups should be created
  - `AUTOBACKUP.KEEP-LAST` (optional)
    - The label `AUTOBACKUP.KEEP-LAST` can be used to specify how many backups should be kept for this server
    - If this label is not specified, the default value from the config is used
- **Snapshots**
  - `AUTOBACKUP`
    - Snapshots are provided with the label `AUTOBACKUP`
    - This makes it possible to see which snapshot was automatically created by the script
    - The script ignores all snapshots without this label (Therefore, only old snapshots with this label are deleted)
    - If you want to keep an automatically generated snapshot, just remove the label `AUTOBACKUP`

![Server-Labels](https://raw.githubusercontent.com/fbrettnich/hcloud-snapshot-as-backup/main/.github/images/server-labels.png "Hetzner Cloud Console: Server Labels")

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
| Any number can be kept (Backups only maximum 7)                       | May be more expensive for extremely large servers (lots of storage) |
| Are cheaper than backups for smaller servers (little storage space)   |                                                                     |
| Are not server bound                                                  |                                                                     |
| New servers can be created directly from the snapshot                 |                                                                     |
