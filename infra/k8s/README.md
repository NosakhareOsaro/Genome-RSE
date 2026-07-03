# infra/k8s

Plain Kubernetes manifests for deploying `services/model-serving` to a
local [`kind`](https://kind.sigs.k8s.io/) cluster. See
[`infra/helm/model-serving`](../helm/model-serving) for the templated
Helm equivalent (used by the CD pipeline); these raw manifests are a
standalone, dependency-free alternative -- both were verified against a
real local cluster.

## Deploy

```bash
# 1. Build the image (from services/model-serving/)
docker build -t genomerse-model-serving:local services/model-serving

# 2. Create the cluster (the kind-config maps NodePort 30080 -> localhost:8080)
kind create cluster --name genomerse --config infra/k8s/kind-config.yaml

# 3. Load the locally-built image directly into the cluster's nodes --
#    no registry round-trip needed for local dev/CI validation.
kind load docker-image genomerse-model-serving:local --name genomerse

# 4. Apply the manifests
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/configmap.yaml
kubectl apply -f infra/k8s/deployment.yaml
kubectl apply -f infra/k8s/service.yaml

# 5. Wait for it, then hit it for real
kubectl -n model-serving wait --for=condition=available --timeout=120s deployment/model-serving
curl http://localhost:8080/health
curl -X POST http://localhost:8080/predict -H "Content-Type: application/json" \
  -d '{"sequence": "CCAGCTGCATCACAGGAGGCCAGCGAGCAGGTCTGTTCCAAGGGCCTTCGAGCCAGTCTG"}'
```

Tear down: `kind delete cluster --name genomerse`.

**`image: genomerse-model-serving:local` / `imagePullPolicy: Never`** in
`deployment.yaml` is a real, working local-dev tag, not a placeholder --
it's the exact image `kind load docker-image` puts on the cluster's
nodes. `imagePullPolicy: Never` makes that explicit: this manifest is
for local/CI validation against an image that's already on the node, not
one Kubernetes should try to pull from a registry (that's what the CD
pipeline's Helm-based deploy does instead, with a real image reference).

## Verified

Actually deployed to a real local `kind` cluster (not just manifests
that pass `kubectl apply --dry-run`): both replicas reached
`Running`/`Ready`, and `/health`, `/model-info`, and `/predict` all
returned correct real responses through the cluster's actual NodePort
(not a `kubectl exec`/port-forward shortcut) -- the same commands shown
above.
