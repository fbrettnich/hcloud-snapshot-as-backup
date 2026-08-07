# Helm Chart: hcloud-snapshot-as-backup

Deploys [hcloud-snapshot-as-backup](https://github.com/fbrettnich/hcloud-snapshot-as-backup) as a Kubernetes CronJob.

The chart creates **one CronJob per Hetzner Cloud project**, so a single release can back up any number of projects — each with its own API token, schedule, label selector and retention.

Scheduling is done by Kubernetes: the chart always sets `CRON=false` in the container, which disables the built-in CronScheduler and makes the script run once and exit.

## Requirements

- Kubernetes >= 1.21 (>= 1.27 for `timeZone`)
- Helm 3 or 4

## Installation

```bash
git clone https://github.com/fbrettnich/hcloud-snapshot-as-backup.git
cd hcloud-snapshot-as-backup

helm install hcloud-snapshot-as-backup ./.helm \
  --namespace hcloud-snapshot-as-backup --create-namespace \
  --set 'projects[0].name=production' \
  --set 'projects[0].apiToken=YOUR_HETZNER_API_TOKEN'
```

Usually you want a values file instead ([values-example.yaml](values-example.yaml)):

```yaml
# values.yaml
timeZone: "Europe/Berlin"

projects:
  - name: production
    apiToken: "YOUR_HETZNER_API_TOKEN"
    schedule: "0 1 * * *"
    keepLast: 7

  - name: staging
    existingSecret: hcloud-staging   # Secret you manage yourself
    schedule: "0 3 * * 0"
    keepLast: 2
```

```bash
helm install hcloud-snapshot-as-backup ./.helm -n hcloud-snapshot-as-backup --create-namespace -f values.yaml
```

`projects` is required — the chart refuses to render without at least one entry, and every entry needs a unique `name` plus either `apiToken` or `existingSecret`.

## API token handling

| Option | Behaviour |
| --- | --- |
| `apiToken` | The chart creates a `Secret` named `<release>-<chart>-<project>` containing the token. Simple, but the token ends up in your values file and in the Helm release data. |
| `existingSecret` / `existingSecretKey` | The chart only references a Secret you created yourself (default key: `API_TOKEN`). Recommended for GitOps, SealedSecrets or the External Secrets Operator. |

```bash
kubectl create secret generic hcloud-staging \
  --namespace hcloud-snapshot-as-backup \
  --from-literal=API_TOKEN=YOUR_HETZNER_API_TOKEN
```

## Testing a project without waiting for the schedule

```bash
kubectl create job -n hcloud-snapshot-as-backup manual-test \
  --from=cronjob/hcloud-snapshot-as-backup-production
kubectl logs -n hcloud-snapshot-as-backup job/manual-test -f
```

## Values

Everything under "per project" can be set on a `projects[]` entry as well as chart-wide. A value on the project wins; otherwise the chart-wide value applies.

### Per project

| Key | Default | Description |
| --- | --- | --- |
| `projects[].name` | — | **Required.** Unique name, used in resource names and as `app.kubernetes.io/component`. |
| `projects[].apiToken` | `""` | Hetzner Cloud API token (read & write). Mutually exclusive with `existingSecret`. |
| `projects[].existingSecret` | `""` | Name of an existing Secret holding the token. |
| `projects[].existingSecretKey` | `API_TOKEN` | Key inside `existingSecret`. |

### Per project or chart-wide

| Key | Default | Description |
| --- | --- | --- |
| `schedule` | `0 1 * * *` | Cron expression, evaluated by Kubernetes. |
| `timeZone` | `""` | Time zone for the schedule (Kubernetes >= 1.27). Also set as `TZ` in the container so `%date%`/`%time%` match. |
| `snapshotName` | `%name%-%timestamp%` | Snapshot naming pattern. Placeholders: `%id%`, `%name%`, `%timestamp%`, `%date%`, `%time%`. |
| `labelSelector` | `AUTOBACKUP` | Servers with this label set to `true` are backed up. |
| `keepLast` | `3` | Snapshots kept per server. Overridable per server via the Hetzner label `<labelSelector>.KEEP-LAST`. |
| `suspend` | `false` | Suspend the CronJob without deleting it. |
| `concurrencyPolicy` | `Forbid` | `Allow`, `Forbid` or `Replace`. |
| `successfulJobsHistoryLimit` | `3` | Completed Jobs to keep. |
| `failedJobsHistoryLimit` | `3` | Failed Jobs to keep. |
| `startingDeadlineSeconds` | `null` | Deadline for starting a missed run. |
| `restartPolicy` | `Never` | Pod restart policy. |
| `backoffLimit` | `0` | Job retries. See the note below before raising this. |
| `activeDeadlineSeconds` | `3600` | Kill a run that hangs. `null` disables. |
| `ttlSecondsAfterFinished` | `null` | Auto-delete finished Jobs after N seconds. |
| `resources` | `10m` CPU / `32Mi`–`128Mi` memory | Container resources. Overriding per project replaces the whole block. |
| `nodeSelector`, `tolerations`, `affinity` | `{}` / `[]` / `{}` | Scheduling constraints. |
| `extraEnv` | `[]` | Extra environment variables. Chart-wide and per-project lists are concatenated. |

> **On `backoffLimit`:** snapshot creation is not idempotent. If a run fails halfway through, the servers processed before the failure already have a snapshot, and a retry creates a second one. The default (`Never` / `0`) therefore does not retry — a failed run is visible in the Job history and the next scheduled run covers it. Raise it only if duplicate snapshots are acceptable.

### Chart-wide only

| Key | Default | Description |
| --- | --- | --- |
| `image.repository` | `fbrettnich/hcloud-snapshot-as-backup` | Image repository. `ghcr.io/fbrettnich/hcloud-snapshot-as-backup` works too. |
| `image.tag` | `""` | Defaults to the chart `appVersion`. |
| `image.pullPolicy` | `IfNotPresent` | |
| `imagePullSecrets` | `[]` | |
| `nameOverride`, `fullnameOverride` | `""` | |
| `podSecurityContext` | non-root, uid/gid `10001`, `RuntimeDefault` seccomp | |
| `securityContext` | no privilege escalation, read-only rootfs, all caps dropped | |
| `serviceAccount.create` | `false` | The script never talks to the Kubernetes API. |
| `serviceAccount.name` | `""` | Defaults to `default` when `create` is `false`. |
| `automountServiceAccountToken` | `false` | |
| `priorityClassName` | `""` | |
| `podLabels`, `podAnnotations` | `{}` | |
| `commonLabels`, `commonAnnotations` | `{}` | Added to all resources. |
| `extraVolumes`, `extraVolumeMounts` | `[]` | |

## Uninstall

```bash
helm uninstall hcloud-snapshot-as-backup -n hcloud-snapshot-as-backup
```

Snapshots already created in Hetzner Cloud are **not** removed — delete them in the Hetzner Cloud Console if you no longer need them.
