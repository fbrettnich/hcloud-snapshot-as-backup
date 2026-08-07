{{/*
Chart name.
*/}}
{{- define "hcloud-snapshot-as-backup.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Fully qualified release name.
Truncated to 40 characters so that the per-project suffix still fits into the
52 character limit Kubernetes enforces on CronJob names.
*/}}
{{- define "hcloud-snapshot-as-backup.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 40 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 40 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 40 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Name of the resources belonging to a single project.
Expects a dict with "root" (the chart context) and "project".
*/}}
{{- define "hcloud-snapshot-as-backup.projectFullname" -}}
{{- printf "%s-%s" (include "hcloud-snapshot-as-backup.fullname" .root) .project.name | trunc 52 | trimSuffix "-" }}
{{- end }}

{{- define "hcloud-snapshot-as-backup.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels.
*/}}
{{- define "hcloud-snapshot-as-backup.labels" -}}
helm.sh/chart: {{ include "hcloud-snapshot-as-backup.chart" . }}
{{ include "hcloud-snapshot-as-backup.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- with .Values.commonLabels }}
{{ toYaml . }}
{{- end }}
{{- end }}

{{- define "hcloud-snapshot-as-backup.selectorLabels" -}}
app.kubernetes.io/name: {{ include "hcloud-snapshot-as-backup.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Service account name used by the pods.
*/}}
{{- define "hcloud-snapshot-as-backup.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "hcloud-snapshot-as-backup.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Name of the secret holding the API token of a project.
Expects a dict with "root" and "project".
*/}}
{{- define "hcloud-snapshot-as-backup.secretName" -}}
{{- if .project.existingSecret }}
{{- .project.existingSecret }}
{{- else }}
{{- include "hcloud-snapshot-as-backup.projectFullname" . }}
{{- end }}
{{- end }}

{{- define "hcloud-snapshot-as-backup.secretKey" -}}
{{- if .project.existingSecret }}
{{- default "API_TOKEN" .project.existingSecretKey }}
{{- else }}
{{- print "API_TOKEN" }}
{{- end }}
{{- end }}

{{/*
Validate .Values.projects. Rendered once from validation.yaml.
*/}}
{{- define "hcloud-snapshot-as-backup.validate" -}}
{{- if not .Values.projects }}
{{- fail "hcloud-snapshot-as-backup: .Values.projects must contain at least one project" }}
{{- end }}
{{- $seen := dict }}
{{- range $i, $project := .Values.projects }}
  {{- if not $project.name }}
    {{- fail (printf "hcloud-snapshot-as-backup: projects[%d] is missing the required field 'name'" $i) }}
  {{- end }}
  {{- if hasKey $seen $project.name }}
    {{- fail (printf "hcloud-snapshot-as-backup: duplicate project name %q - project names must be unique" $project.name) }}
  {{- end }}
  {{- $_ := set $seen $project.name true }}
  {{- if and (not $project.apiToken) (not $project.existingSecret) }}
    {{- fail (printf "hcloud-snapshot-as-backup: project %q needs either 'apiToken' or 'existingSecret'" $project.name) }}
  {{- end }}
  {{- if and $project.apiToken $project.existingSecret }}
    {{- fail (printf "hcloud-snapshot-as-backup: project %q sets both 'apiToken' and 'existingSecret' - use only one of them" $project.name) }}
  {{- end }}
  {{- if not (or $project.schedule $.Values.schedule) }}
    {{- fail (printf "hcloud-snapshot-as-backup: project %q has no 'schedule' and no chart-wide default schedule" $project.name) }}
  {{- end }}
{{- end }}
{{- end }}
