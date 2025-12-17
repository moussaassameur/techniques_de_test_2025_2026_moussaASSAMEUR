"""PLAN.md - Tests d'integration - Section 3: Stabilite et charge.

Tests de stabilite et gestion de charge avec le test client Flask.
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


class TestStabilityAndLoad:
    """Stabilite et charge."""

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
        assert resp.status_code == 200, f"Failed to register: {resp.status_code}"
        return resp.get_json()["pointSetId"]

    def test_multiple_sequential_requests(self, client):
        """Teste plusieurs requetes sequentielles -> pas d'erreur ni de blocage.

        Raison: Tester la capacite de l'API a gerer plusieurs requetes.
        """
        # Creer 5 PointSets differents
        pointset_ids = []
        for i in range(5):
            points = [
                {"x": float(i), "y": 0.0},
                {"x": float(i + 1), "y": 0.0},
                {"x": float(i + 0.5), "y": 1.0},
            ]
            pointset_ids.append(self._register_pointset(client, points))

        # Lancer 10 requetes sequentielles
        results = []
        for _ in range(2):
            for pid in pointset_ids:
                resp = client.get(f"/triangulation/{pid}")
                results.append((resp.status_code, len(resp.data)))

        # Verifier que toutes les requetes ont reussi
        assert len(results) == 10, f"Expected 10 results, got {len(results)}"
        for status, size in results:
            assert status == 200, f"Expected 200, got {status}"
            assert size > 0, "Response should not be empty"

    def test_register_and_triangulate_cycle(self, client):
        """Teste un cycle complet d'enregistrement et triangulation.

        Raison: Verifier le workflow complet de l'API.
        """
        # Cycle: register -> triangulate -> verify
        for i in range(3):
            points = [
                {"x": float(i * 10), "y": 0.0},
                {"x": float(i * 10 + 5), "y": 0.0},
                {"x": float(i * 10 + 2.5), "y": 5.0},
            ]

            # Enregistrer
            pointset_id = self._register_pointset(client, points)
            assert pointset_id is not None

            # Trianguler
            resp = client.get(f"/triangulation/{pointset_id}")
            assert resp.status_code == 200

            # Verifier le contenu
            binary = resp.data
            n_verts = struct.unpack("<I", binary[0:4])[0]
            assert n_verts == 3
