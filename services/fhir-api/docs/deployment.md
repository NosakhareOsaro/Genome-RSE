# Deployment: AWS EC2 + Nginx + Let's Encrypt

This document describes how to deploy `fhir-api` to a single AWS EC2
instance behind Nginx with a Let's Encrypt TLS certificate. **It is
documentation only** — nothing in this repository provisions live AWS
infrastructure; the commands below are meant to be run manually (or
adapted into your own infrastructure-as-code) against a real AWS
account you control.

> Before deploying anywhere beyond local development, replace every
> placeholder secret (`DEMO_CLIENT_SECRET`, `JWT_SIGNING_KEY`,
> `GF_SECURITY_ADMIN_PASSWORD`, the Postgres password) with real
> generated values. See the top-level service README's callout: the
> bundled OAuth2 Authorization Server is a demo, not production
> identity infrastructure — do not put real patient data behind it
> without addressing that first.

## Architecture

```
Internet
   |
   v
[ Nginx :443 ]  <-- Let's Encrypt cert, terminates TLS
   |  proxy_pass to 127.0.0.1:8000
   v
[ fhir-api container :8000 ]  (docker compose, this repo)
   |
   +--> [ postgres container ]  (internal only, not published)
   +--> [ redis container ]     (internal only, not published)
   +--> [ prometheus :9090 ]    (bind to localhost or a VPN-only interface)
   +--> [ grafana :3000 ]       (bind to localhost or a VPN-only interface)
```

Nginx runs directly on the EC2 host (not in a container) so it can own
port 443 and manage the Let's Encrypt certificate with certbot's
standard tooling. The application stack runs via the repo's
`docker-compose.yml`. Prometheus and Grafana should **not** be exposed
to the public internet on a real deployment — either bind them to
`127.0.0.1` in `docker-compose.yml` and reach them over SSH tunnel /
VPN, or put them behind their own authenticated Nginx location.

## 1. Provision the EC2 instance

- AMI: Ubuntu Server 22.04 LTS (or later)
- Instance type: `t3.small` is enough for a demo/portfolio deployment;
  size up if you expect real load.
- Storage: 20+ GB gp3 EBS volume.
- Security group (inbound):
  - `22/tcp` from your IP only (SSH)
  - `80/tcp` from `0.0.0.0/0` (HTTP, needed for the Let's Encrypt HTTP-01 challenge and to redirect to HTTPS)
  - `443/tcp` from `0.0.0.0/0` (HTTPS)
  - Do **not** open 5432, 6379, 8000, 9090, or 3000 to the public internet.
- Allocate and associate an Elastic IP so the DNS record below stays stable.
- Point a DNS `A` record (e.g. `fhir-api.example.com`) at that Elastic IP.

## 2. Install Docker and Docker Compose on the instance

```bash
ssh ubuntu@<your-elastic-ip>

sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker "$USER"
# log out and back in for the group change to take effect
```

## 3. Deploy the application

```bash
git clone https://github.com/NosakhareOsaro/Genome-RSE.git
cd Genome-RSE/services/fhir-api

cp .env.example .env
# Edit .env: set real values for DEMO_CLIENT_SECRET, JWT_SIGNING_KEY, etc.
# Also edit docker-compose.yml's DEMO_CLIENT_SECRET/JWT_SIGNING_KEY/
# GF_SECURITY_ADMIN_PASSWORD environment entries to match, or refactor
# them to read from .env via `env_file:` for a real deployment.

# Bind Prometheus/Grafana to localhost only for a real deployment:
#   ports:
#     - "127.0.0.1:9090:9090"
#     - "127.0.0.1:3000:3000"

docker compose up --build -d
docker compose ps
curl -s http://localhost:8000/healthz
```

## 4. Install Nginx and obtain a Let's Encrypt certificate

```bash
sudo apt-get install -y nginx certbot python3-certbot-nginx
```

Create `/etc/nginx/sites-available/fhir-api`:

```nginx
server {
    listen 80;
    server_name fhir-api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/fhir-api /etc/nginx/sites-enabled/fhir-api
sudo nginx -t
sudo systemctl reload nginx

# Obtain and install a certificate; certbot edits the Nginx config in
# place to add the `listen 443 ssl` block and redirect HTTP -> HTTPS.
sudo certbot --nginx -d fhir-api.example.com
```

Certbot installs a systemd timer (`certbot.timer`) that renews the
certificate automatically before it expires; verify it's active with:

```bash
systemctl status certbot.timer
sudo certbot renew --dry-run
```

## 5. Verify

```bash
curl -s https://fhir-api.example.com/healthz
curl -s https://fhir-api.example.com/metadata | head -c 200
```

## Operational notes

- **Rate limiting** (`RATE_LIMIT` in `.env`) is per-client-IP at the
  application layer. If you run Nginx as a reverse proxy in front of
  it, the app sees Nginx's IP for every request unless Nginx forwards
  the real client IP — it does via `X-Forwarded-For` above, but
  `slowapi`'s default `get_remote_address` key function reads the
  direct connection IP, not the `X-Forwarded-For` header. For accurate
  per-client limiting behind a proxy, swap the key function in
  `app/rate_limit.py` for one that trusts `X-Forwarded-For` from your
  known proxy only (don't trust it blindly from arbitrary clients).
- **Backups**: the `postgres_data` Docker volume is the only stateful
  data. Back it up with `docker compose exec postgres pg_dump -U fhir
  fhir > backup.sql` on a schedule, or use EBS snapshots of the volume's
  underlying storage.
- **Updates**: `git pull && docker compose up --build -d` rebuilds and
  restarts the `api` image; Alembic migrations run automatically on
  container start (see `docker-entrypoint.sh`).
- **Logs**: `docker compose logs -f api`.
- **Rollback**: `git checkout <previous-tag> && docker compose up --build -d`.
