"""PLAN.md - Tests d'integration - Section 1: Reponse API correcte.

Utilise le test client Flask pour tester l'API sans demarrer le serveur.
"""

import struct

import pytest

from app import app


@pytest.fixture
def client():
    """Create test client for Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


class TestAPIResponses:
    """Reponse API correcte."""

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
            binary += struct.pack("<ff", p["x"], p["y"])
        resp = client.post(
            "/pointset",
            data=binary,
            content_type="application/octet-stream",
        )
        assert resp.status_code == 200
        return resp.get_json()["pointSetId"]

    def test_triangulate_with_valid_id(self, client):
        """Teste GET /triangulation/{valid-uuid} -> 200 OK + Binary.

        Raison: Verifier que l'API retourne les triangles pour un PointSetID valide.
        """
        points = [{"x": 0.0, "y": 0.0}, {"x": 1.0, "y": 0.0}, {"x": 0.5, "y": 1.0}]
        pointset_id = self._register_pointset(client, points)

        resp = client.get(f"/triangulation/{pointset_id}")
        assert resp.status_code == 200
        assert resp.content_type == "application/octet-stream"
        assert len(resp.data) > 0

        # Verifier que le binary est parsable
        binary = resp.data
        n_verts = struct.unpack("<I", binary[0:4])[0]
        assert n_verts > 0

    def test_response_content_type_is_binary(self, client):
        """Teste que le Content-Type de la reponse est application/octet-stream.

        Raison: Confirmer que la reponse est bien en format binaire.
        """
        points = [{"x": 0.0, "y": 0.0}, {"x": 1.0, "y": 0.0}, {"x": 0.5, "y": 1.0}]
        pointset_id = self._register_pointset(client, points)

        resp = client.get(f"/triangulation/{pointset_id}")
        assert resp.status_code == 200

        content_type = resp.content_type
        assert content_type is not None
        assert content_type == "application/octet-stream"
        assert "json" not in content_type.lower()

    def test_healthz_endpoint(self, client):
        """Teste GET /healthz -> 200 OK + "ok".

        Raison: Confirmer que le service est operationnel.
        """
        resp = client.get("/healthz")
        assert resp.status_code == 200
        assert resp.data == b"ok"
