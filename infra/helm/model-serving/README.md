# model-serving Helm chart

Templated equivalent of [`infra/k8s`](../../k8s)'s raw manifests. This is
the deploy mechanism the CD pipeline (`.github/workflows/model-serving-cd.yml`)
actually uses.

## Local install (against a kind cluster)

```bash
docker build -t genomerse-model-serving:local services/model-serving
kind create cluster --name genomerse --config infra/k8s/kind-config.yaml
kind load docker-image genomerse-model-serving:local --name genomerse

helm install model-serving infra/helm/model-serving \
  --create-namespace --namespace model-serving

kubectl -n model-serving wait --for=condition=available --timeout=120s deployment/model-serving
curl http://localhost:8080/health
```

## Overriding for a real registry image

```bash
helm upgrade --install model-serving infra/helm/model-serving \
  --namespace model-serving --create-namespace \
  --set image.repository=ghcr.io/nosakhareosaro/genome-rse-model-serving \
  --set image.tag=<sha-or-version> \
  --set image.pullPolicy=IfNotPresent
```

## Verified

`helm lint` and `helm template` pass; `helm install` was run against a
real local kind cluster (loaded with a locally-built image), and
`/health`, `/model-info`, `/predict` all returned correct real responses
through the cluster's NodePort -- same as the raw-manifest path in
`infra/k8s`, using the same underlying image.
