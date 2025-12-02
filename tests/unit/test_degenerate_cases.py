"""
PLAN.md - Tests unitaires - Section 3: Cas dégénérés ou particuliers
"""

import pytest
import requests
import struct


class TestDegenerateCases:
    """Cas dégénérés ou particuliers"""

    BASE_URL = "http://localhost:8000"
    TRIANGULATOR = "/triangulation"
    POINTSET_MGR = "/pointset"

    def _register_pointset(self, points):
        """Enregistrer un PointSet et retourner son ID ou None"""
        binary = struct.pack('<I', len(points))
        for p in points:
            binary += struct.pack('<ff', p["x"], p["y"])
        resp = requests.post(
            f"{self.BASE_URL}{self.POINTSET_MGR}",
            data=binary,
            headers={"Content-Type": "application/octet-stream"}
        )
        if resp.status_code == 201:
            return resp.json()["pointSetId"]
        return None

    def test_collinear_points(self, collinear_points):
        """
        Cas testé: GET /triangulation/{uuid} avec points colinéaires
        Résultat attendu: 0 triangle ou erreur
        Raison: Tester la gestion de points qui ne peuvent pas former de triangles.
        
        À tester:
        - Soit status 400/500 (erreur)
        - Soit 200 avec 0 triangles
        - Comportement cohérent et documenté
        """
        pointset_id = self._register_pointset(collinear_points)
        if pointset_id is None:
            pytest.skip("PointSetManager rejected collinear points")
        
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        if resp.status_code in [400, 500, 404]:
            pass  # Rejet - acceptable
        elif resp.status_code == 200:
            binary = resp.content
            n_verts = struct.unpack('<I', binary[0:4])[0]
            n_tri_off = 4 + n_verts * 8
            n_tris = struct.unpack('<I', binary[n_tri_off:n_tri_off+4])[0]
            assert n_tris == 0
        else:
            pytest.fail(f"Unexpected status: {resp.status_code}")

    def test_duplicate_points(self, duplicate_points):
        """
        Cas testé: GET /triangulation/{uuid} avec points dupliqués
        Résultat attendu: Gestion appropriée (ignorer ou erreur)
        Raison: Vérifier que les doublons n'affectent pas la triangulation.
        
        À tester:
        - Soit déduplication automatique
        - Soit rejet avec erreur
        - Comportement cohérent
        """
        pointset_id = self._register_pointset(duplicate_points)
        if pointset_id is None:
            pytest.skip("PointSetManager rejected duplicate points")
        
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        if resp.status_code in [400, 500, 404]:
            pass  # Rejet - acceptable
        elif resp.status_code == 200:
            binary = resp.content
            n_verts = struct.unpack('<I', binary[0:4])[0]
            assert n_verts <= len(duplicate_points)
        else:
            pytest.fail(f"Unexpected status: {resp.status_code}")
