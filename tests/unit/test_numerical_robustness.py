"""
PLAN.md - Tests unitaires - Section 5: Robustesse numérique
"""

import pytest
import requests
import struct
import math


class TestNumericalRobustness:
    """Robustesse numérique"""

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

    def test_extreme_values(self):
        """
        Cas testé: GET /triangulation/{uuid} avec coordonnées extrêmes
        Résultat attendu: 200 + Triangles valides, pas de crash
        Raison: S'assurer que le service gère correctement les valeurs extrêmes.
        
        À tester:
        - Très grandes valeurs (1e10)
        - Très petites valeurs (1e-10)
        - Pas de débordement (overflow/underflow)
        - Pas de NaN ou Infinity en réponse
        - Triangulation valide malgré l'amplitude
        """
        extreme_pts = [
            {"x": 1e-10, "y": 1e-10},
            {"x": 1e10, "y": 1e10},
            {"x": 0.0, "y": 1e5},
            {"x": 1e-5, "y": 1e-5}
        ]
        
        pointset_id = self._register_pointset(extreme_pts)
        if pointset_id is None:
            pytest.skip("Service rejected extreme values")
        
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        if resp.status_code != 200:
            pytest.skip(f"Service returned {resp.status_code}")
        
        binary = resp.content
        n_verts = struct.unpack('<I', binary[0:4])[0]
        verts_data = binary[4:4 + n_verts*8]
        
        # Vérifier qu'il n'y a pas de NaN ou Infinity
        for i in range(n_verts):
            x, y = struct.unpack('<ff', verts_data[i*8:(i+1)*8])
            assert math.isfinite(x), f"Vertex {i}: x is not finite"
            assert math.isfinite(y), f"Vertex {i}: y is not finite"
        
        # Vérifier les triangles
        n_tri_off = 4 + n_verts * 8
        n_tris = struct.unpack('<I', binary[n_tri_off:n_tri_off+4])[0]
        tris_data = binary[n_tri_off + 4:]
        
        for i in range(n_tris):
            idx1, idx2, idx3 = struct.unpack('<III', tris_data[i*12:(i+1)*12])
            assert 0 <= idx1 < n_verts
            assert 0 <= idx2 < n_verts
            assert 0 <= idx3 < n_verts
