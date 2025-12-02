"""
PLAN.md - Tests d'intégration - Section 1: Réponse API correcte
"""

import pytest
import requests
import struct


class TestAPIResponses:
    """Réponse API correcte"""

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

    def test_triangulate_with_valid_id(self):
        """
        Cas testé: GET /triangulation/{valid-uuid}
        Résultat attendu: 200 OK + Binary (application/octet-stream)
        Raison: Vérifier que l'API retourne les triangles pour un PointSetID valide.
        
        À tester:
        - Status HTTP = 200
        - Content-Type = "application/octet-stream"
        - Body = données binaires (non vide)
        - Format binary valide (parsable)
        """
        points = [{"x": 0.0, "y": 0.0}, {"x": 1.0, "y": 0.0}, {"x": 0.5, "y": 1.0}]
        pointset_id = self._register_pointset(points)
        
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        assert resp.status_code == 200
        assert resp.headers.get("Content-Type") == "application/octet-stream"
        assert len(resp.content) > 0
        
        # Vérifier que le binary est parsable
        binary = resp.content
        n_verts = struct.unpack('<I', binary[0:4])[0]
        assert n_verts > 0

    def test_response_content_type_is_binary(self):
        """
        Cas testé: Vérifier le Content-Type de la réponse
        Résultat attendu: "application/octet-stream"
        Raison: Confirmer que la réponse est bien en format binaire.
        
        À tester:
        - Header Content-Type présent
        - Valeur = "application/octet-stream"
        - Pas "application/json" ou autre
        """
        points = [{"x": 0.0, "y": 0.0}, {"x": 1.0, "y": 0.0}, {"x": 0.5, "y": 1.0}]
        pointset_id = self._register_pointset(points)
        
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        assert resp.status_code == 200
        
        content_type = resp.headers.get("Content-Type")
        assert content_type is not None
        assert content_type == "application/octet-stream"
        assert "json" not in content_type.lower()
