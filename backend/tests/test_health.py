"""
Health endpoint test — basic smoke test.
"""


class TestHealth:
    """GET /api/v1/health"""

    def test_health_endpoint(self, client):
        """Health check should return 200 with status info."""
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
