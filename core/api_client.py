"""Authenticated HTTP session for API tests.

Tenant header is per request, not on the session, so isolation tests
can send the wrong tenant deliberately.
"""
import requests


class APIClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })

    def post(self, path, json=None, tenant_id=None):
        return self.session.post(
            f"{self.base_url}{path}",
            json=json,
            headers={"X-Tenant-ID": tenant_id} if tenant_id else {},
            timeout=30,
        )

    def get(self, path, tenant_id=None):
        return self.session.get(
            f"{self.base_url}{path}",
            headers={"X-Tenant-ID": tenant_id} if tenant_id else {},
            timeout=30,
        )

    def delete(self, path, tenant_id=None):
        return self.session.delete(
            f"{self.base_url}{path}",
            headers={"X-Tenant-ID": tenant_id} if tenant_id else {},
            timeout=30,
        )
