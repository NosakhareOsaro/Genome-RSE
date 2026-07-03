{{/*
Chart name and version as used by the chart label.
*/}}
{{- define "model-serving.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels.
*/}}
{{- define "model-serving.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ include "model-serving.chart" . }}
{{- end }}

{{/*
Selector labels.
*/}}
{{- define "model-serving.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Namespace to deploy into.
*/}}
{{- define "model-serving.namespace" -}}
{{- .Values.namespace.name | default .Release.Namespace }}
{{- end }}
