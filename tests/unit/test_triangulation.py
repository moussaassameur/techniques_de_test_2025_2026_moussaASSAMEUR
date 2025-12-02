"""
PLAN.md - Tests unitaires - Section 2: Cas de triangulation normale
"""

import pytest
import requests
import struct


class TestNormalTriangulation:
    """Cas de triangulation normale"""

    BASE_URL = "http://localhost:8000"
    TRIANGULATOR = "/triangulation"
    POINTSET_MGR = "/pointset"

    def _register_pointset(self, points):
        """Enregistrer un PointSet et retourner son ID"""
        binary = struct.pack('<I', len(points))
        for p in points:
            binary += struct.pack('<ff', p["x"], p["y"])
        resp = requests.post(
            f"{self.BASE_URL}{self.POINTSET_MGR}",
            data=binary,
            headers={"Content-Type": "application/octet-stream"}
        )
        assert resp.status_code == 201
        return resp.json()["pointSetId"]

    def test_three_non_collinear_points(self, sample_3_points):
        """
        Cas testé: GET /triangulation/{uuid} avec 3 points non alignés
        Résultat attendu: 200 + Binary format valide avec 1 triangle
        Raison: Confirmer que le service triangule correctement le cas minimal.
        
        À tester:
        - Status HTTP = 200
        - Content-Type = "application/octet-stream"
        - Binary parse: 3 vertices + 1 triangle
        - Indices triangle = [0, 1, 2]
        """
        pointset_id = self._register_pointset(sample_3_points)
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        assert resp.status_code == 200
        assert resp.headers.get("Content-Type") == "application/octet-stream"
        
        binary = resp.content
        n_verts = struct.unpack('<I', binary[0:4])[0]
        assert n_verts == 3
        
        n_tri_off = 4 + n_verts * 8
        n_tris = struct.unpack('<I', binary[n_tri_off:n_tri_off+4])[0]
        assert n_tris == 1

    def test_triangulation_10_points(self, sample_10_points):
        """
        Cas testé: GET /triangulation/{uuid} avec 10 points
        Résultat attendu: 200 + Binary avec plusieurs triangles
        Raison: Valider que la triangulation fonctionne sur des ensembles standards.
        
        À tester:
        - Status HTTP = 200
        - Nombre de vertices = 10
        - Nombre de triangles > 1
        - Tous les triangles ont indices valides
        """
        pointset_id = self._register_pointset(sample_10_points)
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        assert resp.status_code == 200
        
        binary = resp.content
        n_verts = struct.unpack('<I', binary[0:4])[0]
        assert n_verts == 10
        
        n_tri_off = 4 + n_verts * 8
        n_tris = struct.unpack('<I', binary[n_tri_off:n_tri_off+4])[0]
        assert n_tris > 1
        
        # Vérifier les indices des triangles
        tris_data = binary[n_tri_off + 4:]
        for i in range(n_tris):
            idx1, idx2, idx3 = struct.unpack('<III', tris_data[i*12:(i+1)*12])
            assert 0 <= idx1 < n_verts
            assert 0 <= idx2 < n_verts
            assert 0 <= idx3 < n_verts

    def test_binary_format_structure(self):
        """
        Cas testé: Parser le format binary de la réponse
        Résultat attendu: Structure correcte (N vertices + indices triangles)
        Raison: Assurer la fidélité du format binary.
        
        À tester:
        - Premiers 4 bytes = N (nombre vertices)
        - Suivants N*8 bytes = vertices (X,Y floats)
        - Suivants 4 bytes = T (nombre triangles)
        - Suivants T*12 bytes = triangles (3 indices)
        """
        points = [{"x": 0.0, "y": 0.0}, {"x": 1.0, "y": 0.0}, {"x": 0.5, "y": 1.0}]
        pointset_id = self._register_pointset(points)
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        assert resp.status_code == 200
        
        binary = resp.content
        n_verts = struct.unpack('<I', binary[0:4])[0]
        assert n_verts > 0
        
        verts_end = 4 + n_verts * 8
        n_tris = struct.unpack('<I', binary[verts_end:verts_end+4])[0]
        assert n_tris >= 0
        
        tris_end = verts_end + 4 + n_tris * 12
        assert len(binary) == tris_end
