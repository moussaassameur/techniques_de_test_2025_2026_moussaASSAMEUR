"""
PLAN.md - Tests unitaires - Section 4: Conversion binaire / sérialisation
"""

import pytest
import struct
import requests


class TestSerialization:
    """Conversion binaire / sérialisation"""

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

    def test_binary_to_triangles(self):
        """
        Cas testé: Parser réponse binary → structures Triangles
        Résultat attendu: Conversion correcte sans perte
        Raison: Confirmer la sérialisation bidirectionnelle des triangles.
        
        À tester:
        - Lire 4 bytes = T (nombre triangles)
        - Lire T*12 bytes = triangles (3 indices chacun)
        - Vérifier indices valides et cohérents
        """
        points = [{"x": 0.0, "y": 0.0}, {"x": 1.0, "y": 0.0}, {"x": 0.5, "y": 1.0}]
        pointset_id = self._register_pointset(points)
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        assert resp.status_code == 200
        
        binary = resp.content
        n_verts = struct.unpack('<I', binary[0:4])[0]
        n_tri_off = 4 + n_verts * 8
        n_tris = struct.unpack('<I', binary[n_tri_off:n_tri_off+4])[0]
        
        tris_data = binary[n_tri_off + 4:]
        for i in range(n_tris):
            idx1, idx2, idx3 = struct.unpack('<III', tris_data[i*12:(i+1)*12])
            assert 0 <= idx1 < n_verts
            assert 0 <= idx2 < n_verts
            assert 0 <= idx3 < n_verts

    def test_binary_vertices_match_original(self, sample_10_points):
        """
        Cas testé: Vertices extraits du binary = PointSet original
        Résultat attendu: Points identiques après conversion
        Raison: Assurer l'intégrité des données lors de la sérialisation.
        
        À tester:
        - Lire N (nombre vertices)
        - Lire N*8 bytes (X,Y floats)
        - Comparer avec PointSet original
        - Vérifier précision numérique
        """
        pointset_id = self._register_pointset(sample_10_points)
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        assert resp.status_code == 200
        
        binary = resp.content
        n_verts = struct.unpack('<I', binary[0:4])[0]
        assert n_verts == len(sample_10_points)
        
        verts_data = binary[4:4 + n_verts*8]
        tol = 1e-5
        for i, orig_pt in enumerate(sample_10_points):
            x, y = struct.unpack('<ff', verts_data[i*8:(i+1)*8])
            assert abs(x - orig_pt["x"]) < tol
            assert abs(y - orig_pt["y"]) < tol

    def test_corrupted_binary_rejected(self):
        """
        Cas testé: Données binaires corrompues/invalides
        Résultat attendu: Erreur de parsing ou 500
        Raison: Tester la résistance face à des données malformées.
        
        À tester:
        - Truncated binary (trop court)
        - Invalid indices (hors limites)
        - Gestion d'erreur robuste
        """
        truncated = struct.pack('<I', 100)  # Prétend 100 points mais envoie 4 bytes
        resp = requests.post(
            f"{self.BASE_URL}{self.POINTSET_MGR}",
            data=truncated,
            headers={"Content-Type": "application/octet-stream"}
        )
        assert resp.status_code in [400, 422, 500]
