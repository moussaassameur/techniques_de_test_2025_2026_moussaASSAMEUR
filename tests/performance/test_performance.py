"""PLAN.md - Tests de performance.

Tests de performance avec differentes tailles de donnees.
Utilise le test_client Flask pour eviter de demarrer un serveur.
"""

import random
import struct
import time

import pytest

from app import app


@pytest.mark.performance
class TestPerformance:
    """Tests de performance."""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        """Configure le client de test Flask."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    def _register_pointset(self, points):
        """Enregistrer un PointSet et retourner son ID.

        Args:
            points: Liste de dicts {"x": float, "y": float}

        Returns:
            PointSetID (str)

        """
        binary = struct.pack("<I", len(points))
        for p in points:
            binary += struct.pack("<ff", p["x"], p["y"])
        resp = self.client.post(
            "/pointset",
            data=binary,
            content_type="application/octet-stream",
        )
        assert resp.status_code == 200
        return resp.get_json()["pointSetId"]

    def _generate_points(self, n):
        """Generer n points aleatoires.

        Args:
            n: Nombre de points a generer

        Returns:
            Liste de dicts {"x": float, "y": float}

        """
        points = []
        for _i in range(n):
            x = random.uniform(-100.0, 100.0)
            y = random.uniform(-100.0, 100.0)
            points.append({"x": x, "y": y})
        return points

    def test_triangulation_10_points(self):
        """Teste GET /triangulation/{uuid} avec 10 points -> < 0.5 secondes.

        Raison: Verifier la rapidite sur petits ensembles.
        """
        points = self._generate_points(10)
        pointset_id = self._register_pointset(points)

        start = time.time()
        resp = self.client.get(f"/triangulation/{pointset_id}")
        elapsed = time.time() - start

        assert resp.status_code == 200
        assert elapsed < 0.5, f"Expected < 0.5s, got {elapsed:.3f}s"

    def test_triangulation_100_points(self):
        """Teste GET /triangulation/{uuid} avec 100 points -> < 1 seconde.

        Raison: Confirmer la performance sur ensembles moyens.
        """
        points = self._generate_points(100)
        pointset_id = self._register_pointset(points)

        start = time.time()
        resp = self.client.get(f"/triangulation/{pointset_id}")
        elapsed = time.time() - start

        assert resp.status_code == 200
        assert elapsed < 1.0, f"Expected < 1.0s, got {elapsed:.3f}s"

    def test_triangulation_1000_points(self):
        """Teste GET /triangulation/{uuid} avec 1000 points -> < 3 secondes.

        Raison: Tester la scalabilite sur grands ensembles.
        """
        points = self._generate_points(1000)
        pointset_id = self._register_pointset(points)

        start = time.time()
        resp = self.client.get(f"/triangulation/{pointset_id}")
        elapsed = time.time() - start

        assert resp.status_code == 200
        assert elapsed < 3.0, f"Expected < 3.0s, got {elapsed:.3f}s"

    def test_triangulation_10000_points(self):
        """Teste GET /triangulation/{uuid} avec 10000 points -> < 10 secondes.

        Raison: Verifier le comportement sous forte charge.
        """
        points = self._generate_points(10000)
        pointset_id = self._register_pointset(points)

        start = time.time()
        resp = self.client.get(f"/triangulation/{pointset_id}")
        elapsed = time.time() - start

        assert resp.status_code == 200
        assert elapsed < 10.0, f"Expected < 10.0s, got {elapsed:.3f}s"

    def test_binary_parsing_performance(self):
        """Teste le parsing de reponse binary (10000 points) -> < 2 secondes.

        Raison: Assurer que la conversion binary reste efficace.
        """
        points = self._generate_points(10000)
        pointset_id = self._register_pointset(points)

        resp = self.client.get(f"/triangulation/{pointset_id}")
        assert resp.status_code == 200

        binary = resp.data

        # Mesurer le temps de parsing
        start = time.time()

        # Parser les vertices
        n_verts = struct.unpack("<I", binary[0:4])[0]
        verts_data = binary[4 : 4 + n_verts * 8]
        vertices = []
        for i in range(n_verts):
            x, y = struct.unpack("<ff", verts_data[i * 8 : (i + 1) * 8])
            vertices.append((x, y))

        # Parser les triangles
        n_tri_off = 4 + n_verts * 8
        n_tris = struct.unpack("<I", binary[n_tri_off : n_tri_off + 4])[0]
        tris_data = binary[n_tri_off + 4 :]
        triangles = []
        for i in range(n_tris):
            idx1, idx2, idx3 = struct.unpack("<III", tris_data[i * 12 : (i + 1) * 12])
            triangles.append((idx1, idx2, idx3))

        elapsed = time.time() - start

        assert len(vertices) == n_verts
        assert len(triangles) == n_tris
        assert elapsed < 2.0, f"Parsing took {elapsed:.3f}s, expected < 2.0s"
