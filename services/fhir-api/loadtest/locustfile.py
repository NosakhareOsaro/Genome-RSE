"""Locust load test for fhir-api.

Run against a live instance (e.g. the docker-compose stack):

    pip install -e ".[loadtest]"
    locust -f loadtest/locustfile.py --host http://localhost:8000

Each simulated user fetches its own OAuth2 access token on start using
the same demo client_credentials flow the rest of this service uses.
DEMO_CLIENT_SECRET below is the same obvious placeholder used
throughout this repo (see the top-level README's demo-Authorization-
Server callout) -- it is not a real secret.
"""

from __future__ import annotations

import random

from locust import HttpUser, between, task

DEMO_CLIENT_ID = "demo-client"
DEMO_CLIENT_SECRET = "REPLACE_ME_NOT_A_REAL_SECRET"


class FhirApiUser(HttpUser):
    wait_time = between(0.2, 1.0)

    def on_start(self) -> None:
        self.created_ids: list[str] = []
        response = self.client.post(
            "/oauth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": DEMO_CLIENT_ID,
                "client_secret": DEMO_CLIENT_SECRET,
                "scope": "system/MolecularSequence.read system/MolecularSequence.write",
            },
            name="/oauth/token",
        )
        token = response.json()["access_token"]
        self.client.headers.update({"Authorization": f"Bearer {token}"})

    @task(5)
    def read_random_resource(self) -> None:
        if not self.created_ids:
            return
        resource_id = random.choice(self.created_ids)
        self.client.get(f"/MolecularSequence/{resource_id}", name="/MolecularSequence/[id]")

    @task(3)
    def search_resources(self) -> None:
        self.client.get(
            "/MolecularSequence", params={"_count": 20}, name="/MolecularSequence (search)"
        )

    @task(2)
    def create_resource(self) -> None:
        patient_id = random.randint(1, 1000)
        response = self.client.post(
            "/MolecularSequence",
            json={"coordinateSystem": 0, "patient": {"reference": f"Patient/{patient_id}"}},
            name="/MolecularSequence (create)",
        )
        if response.status_code == 201:
            self.created_ids.append(response.json()["id"])
            if len(self.created_ids) > 200:
                self.created_ids.pop(0)

    @task(1)
    def check_metadata(self) -> None:
        self.client.get("/metadata", name="/metadata")
