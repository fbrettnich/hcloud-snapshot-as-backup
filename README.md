# Hetzner Cloud | Snapshot-as-Backup  
This script automatically creates snapshots of your Hetzner Cloud Servers and deletes the old ones.  
Snapshots then work like the automatic backups offered directly by Hetzner, with the advantage that more backups and at self-defined times can be created.  
For ease of use, the script works with the powerful labels directly in the Hetzner Cloud Console. Just add labels to the servers and you are done.  

- [Installation](#installation)
  - [With Docker (Recommended)](#installation-with-docker-recommended)
  - [With Docker Compose](#installation-with-docker-compose)
  - [Without Docker](#installation-without-docker)
- [Configuration](#configuration)
  - [Generate Hetzner Cloud Console API-Key](#generate-hetzner-cloud-console-api-key)
  - [Choose how many backups you want to keep by default](#choose-how-many-backups-you-want-to-keep-by-default)
  - [Add label to servers that should be backed up](#add-label-to-servers-that-should-be-backed-up)
  - [Choose a name for your snapshots (optional)](#choose-a-name-for-your-snapshots-optional)
  - [Docker: Specify how often the script should be executed via cron](#docker-specify-how-often-the-script-should-be-executed-via-cron)
- [About Labels](#about-labels)
- [Why is this script useful?](#why-is-this-script-useful)

## Installation

### Installation: With Docker (Recommended)
**1. Run the docker image**  
```
docker run -d --name hcloud-snapshot-as-backup \
  -v /etc/localtime:/etc/localtime:ro \
  --env API_TOKEN= \
  --env SNAPSHOT_NAME="%name%-%timestamp%" \
  --env KEEP_LAST=3 \
  --env CRON="0 1 * * *" \
  fbrettnich/hcloud-snapshot-as-backup
```

Put your [Hetzner Cloud Console API-Key](#generate-hetzner-cloud-console-api-key) after `API_TOKEN=` in command line 3.

Optional: Set `CRON` to `false` to disable CronScheduler in the container and schedule outside of the container, especially for using services like [Google Cloud Run jobs](https://cloud.google.com/run/docs/create-jobs) or [Amazon ECS scheduled tasks](https://docs.aws.amazon.com/AmazonECS/latest/userguide/scheduled_tasks.html).

---

### Installation: With Docker Compose
**1. Download [docker-compose.yml](https://github.com/fbrettnich/hcloud-snapshot-as-backup/blob/main/docker-compose.yml)**  
```
curl -sSL https://raw.githubusercontent.com/fbrettnich/hcloud-snapshot-as-backup/main/docker-compose.yml > docker-compose.yml
```

**2. Edit configuration**  
Open the `docker-compose.yml` file to complete the configuration.  
You can find more information about the configuration below ([click here](#configuration))


**3. Run docker-compose**  
````
docker-compose up -d
````

---

### Installation: Without Docker
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

**4. Edit configuration**  
Open the `config.json` file to complete the configuration.  
You can find more information about the configuration below ([click here](#configuration))

**5. Run script**  
```
python3 /opt/hcloud-snapshot-as-backup/snapshot-as-backup.py
```

To execute the script automatically, you can create a crontab: [Crontab Generator](https://crontab-generator.org/)

````
crontab -e
````

Add the crontab at the end of the file:  
```
0 1 * * * python3 /opt/hcloud-snapshot-as-backup/snapshot-as-backup.py >/dev/null 2>&1
```
This crontab executes the script every day at 1am.  

## Configuration  
Depending on how you run the script, you will need to configure.  
When you run the script using Docker, the options are set by environment variables.  
When you run the script via command/crontab, the options are set via the configuration file ([`config.json`](https://github.com/fbrettnich/hcloud-snapshot-as-backup/blob/main/config-example.json)).  

### Generate Hetzner Cloud Console API-Key  
1. Login to [Hetzner Cloud Console](https://console.hetzner.cloud/)
2. Select your project
3. Click "Access" on the left side
4. Switch to "API-Tokens" at the top
5. Click on "Create API Token" and create a new token with read & write permission
6. Copy the key and paste it into the environment variables under `API_TOKEN` or in the config under `api-token`

![Create Hetzner API Token Gif](https://raw.githubusercontent.com/fbrettnich/hcloud-snapshot-as-backup/main/.github/images/create-hetzner-api-token.gif)

### Choose how many backups you want to keep by default  
You can specify in the environment variables under `KEEP_LAST` or in the config under `keep-last` how many backups you want to keep per server by default.  
Labels can be used to overwrite the default value directly in the Hetzner Cloud Console.  
Add the label `AUTOBACKUP.KEEP-LAST` with the value that should apply to the server.  
The newest ones are kept and old ones are deleted.  

### Add label to servers that should be backed up  
All servers that should be included by the script and automatic snapshot backups should be created must have the label `AUTOBACKUP` with the value `true`.  

### Choose a name for your snapshots (optional)  
Specify how you want your snapshots to be named in the environment variables under `SNAPSHOT_NAME` or under `snapshot-name` in the config.  
By default they are named `<server name>-<timestamp>`.  

| Placeholder | Value                     |
|-------------|---------------------------|
| %id%        | ID of the server          |
| %name%      | Name of the server        |
| %timestamp% | Current timestamp         |
| %date%      | Current date (`%Y-%m-%d`) |
| %time%      | Current time (`%H:%M:%S`) |

### Docker: Specify how often the script should be executed via cron
If you run the script in Docker, a cron may be specified in the environment variables under `CRON`.  
The cron is used to define how often and at which times the script should be executed.  
Optionally, set `CRON` to `false` to disable CronScheduler in the container and schedule outside of the container.

Here you can create a cron: [Cron Generator](https://crontab.guru/#0_1_*_*_*)  

For example:  
```
0 1 * * *
```
This cron executes the script every day at 1am.  

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

## Why is this script useful?  
| Advantages                                                            | Disadvantages                                                       |
| --------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Snapshot Backups can be created at own times (Backups at given time)  | Snapshots are limited (but higher limit can be requested)           |
| Any number can be kept (Backups only maximum 7)                       | May be more expensive for extremely large servers (lots of storage) |
| Are cheaper than backups for smaller servers (little storage space)   |                                                                     |
| Are not server bound                                                  |                                                                     |
| New servers can be created directly from the snapshot                 |                                                                     |
