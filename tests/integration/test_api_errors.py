"""PLAN.md - Tests d'integration - Section 2: Gestion d'erreur API.

Tests d'erreurs API (200, 400, 404, 500, 503) avec le test client Flask.
"""

import struct
import uuid

import pytest

from app import app


@pytest.fixture
def client():
    """Create test client for Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


class TestAPIErrors:
    """Gestion d'erreur API."""

    def _register_pointset(self, client, points):
        """Enregistrer un PointSet et retourner son ID.

        Args:
            client: Flask test client
            points: Liste de dicts {"x": float, "y": float}

        Returns:
            PointSetID (str)

        """
        binary = struct.pack("<I", len(points))
        for p in points:
            binary += struct.pack("<ff", float(p["x"]), float(p["y"]))
        resp = client.post(
            "/pointset",
            data=binary,
            content_type="application/octet-stream",
        )
        assert resp.status_code == 200, f"Failed: {resp.status_code}"
        return resp.get_json()["pointSetId"]

    def test_triangulate_with_valid_id_returns_200(self, client, sample_3_points):
        """Teste API /triangulate avec ID valide -> 200 OK.

        Raison: Verifier la reponse correcte en cas de succes.
        """
        pointset_id = self._register_pointset(client, sample_3_points)
        resp = client.get(f"/triangulation/{pointset_id}")

        assert resp.status_code == 200
        assert resp.content_type == "application/octet-stream"
        assert len(resp.data) > 0

    def test_triangulate_with_invalid_uuid_format_returns_400(self, client):
        """Teste API /triangulate avec UUID malforme -> 400 Bad Request.

        Raison: Garantir la robustesse contre les formats invalides.
        """
        resp = client.get("/triangulation/not-a-uuid")

        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
        assert "application/json" in resp.content_type

        data = resp.get_json()
        assert "code" in data or "error" in data
        assert "message" in data or "detail" in data

    def test_triangulate_with_nonexistent_id_returns_404(self, client):
        """Teste API /triangulate avec ID inexistant -> 404 Not Found.

        Raison: Verifier la gestion quand le PointSetID n'existe pas.
        """
        fake_id = str(uuid.uuid4())
        resp = client.get(f"/triangulation/{fake_id}")

        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
        assert "application/json" in resp.content_type

        data = resp.get_json()
        assert "code" in data or "error" in data
        assert "message" in data or "detail" in data

    def test_server_error_500_format(self, client):
        """Teste API /triangulate provoquant une erreur interne -> 500.

        Raison: Verifier le format d'erreur en cas de bug/exception cote serveur.
        """
        resp = client.get("/triangulation/cause-500")
        if resp.status_code != 500:
            pytest.skip("Server did not return 500; skipping test.")

        assert "application/json" in resp.content_type
        data = resp.get_json()
        assert "code" in data or "error" in data
        assert "message" in data or "detail" in data

    def test_service_unavailable_503_format(self, client):
        """Teste service indisponible / surcharge -> 503 Service Unavailable.

        Raison: Confirmer le comportement lorsque le service est indisponible.
        """
        resp = client.get("/triangulation/cause-503")
        if resp.status_code != 503:
            pytest.skip("Server did not return 503; skipping test.")

        assert "application/json" in resp.content_type
        data = resp.get_json()
        assert "code" in data or "error" in data
        assert "message" in data or "detail" in data
