"""
Search endpoint tests — mocking InsightFace to avoid loading AI models.
"""
import io
import pytest
from unittest.mock import patch, MagicMock
import numpy as np


class TestSearchEndpoint:
    """POST /api/v1/search/{event_id}"""

    def test_search_nonexistent_event(self, client):
        """Searching a non-existent event should return 404."""
        fake_image = io.BytesIO(b"fake image data")
        resp = client.post(
            "/api/v1/search/EVT-NONEXISTENT",
            files={"file": ("selfie.jpg", fake_image, "image/jpeg")},
        )
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()

    def test_search_no_file(self, client, test_event):
        """Missing file should return 422."""
        resp = client.post(f"/api/v1/search/{test_event.event_id}")
        assert resp.status_code == 422

    @patch("app.api.routes.search.extract_and_assess_faces")
    def test_search_no_face_detected(self, mock_extract, client, test_event):
        """When no face is detected in the selfie, should return 400."""
        mock_extract.return_value = []  # no faces detected

        fake_image = io.BytesIO(b"fake selfie image data")
        resp = client.post(
            f"/api/v1/search/{test_event.event_id}",
            files={"file": ("selfie.jpg", fake_image, "image/jpeg")},
        )
        assert resp.status_code == 400
        assert "no clear face" in resp.json()["detail"].lower()

    @patch("app.api.routes.search.search_faces_by_vector")
    @patch("app.api.routes.search.extract_and_assess_faces")
    @patch("app.api.routes.search.get_storage_manager")
    def test_search_valid_selfie_no_matches(
        self, mock_storage, mock_extract, mock_search, client, test_event
    ):
        """Valid selfie with face detected but no matching photos — returns empty results."""
        # Mock face detection: return one face with embedding
        mock_embedding = np.random.rand(512).astype(np.float32)
        mock_extract.return_value = [
            ([100, 100, 200, 200], 0.95, mock_embedding),
        ]

        # Mock vector search: no matches
        mock_search.return_value = []

        # Mock storage manager
        mock_storage_instance = MagicMock()
        mock_storage_instance.generate_presigned_download_url.return_value = "http://example.com/photo.jpg"
        mock_storage.return_value = mock_storage_instance

        fake_image = io.BytesIO(b"real enough selfie data")
        resp = client.post(
            f"/api/v1/search/{test_event.event_id}",
            files={"file": ("selfie.jpg", fake_image, "image/jpeg")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["match_count"] == 0
        assert data["photos"] == []
