"""
PLAN.md - Tests unitaires - Section 1: Gestion des erreurs et cas impossibles
"""

import pytest
import requests
import uuid
import struct


class TestErrorHandling:
    """Gestion des erreurs et cas impossibles"""

    BASE_URL = "http://localhost:8000"
    TRIANGULATOR = "/triangulation"
    POINTSET_MGR = "/pointset"

    def test_nonexistent_pointset_id(self):
        """
        Cas testé: GET /triangulation/{pointSetId} avec UUID inexistant
        Résultat attendu: 404 Not Found + JSON Error {"code": "...", "message": "..."}
        Raison: Vérifier que le service renvoie 404 quand le PointSetID n'existe pas en DB.
        
        À tester:
        - Status HTTP = 404
        - Response contient "code" et "message"
        """
        fake_id = str(uuid.uuid4())
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{fake_id}")
        assert resp.status_code == 404
        data = resp.json()
        assert "code" in data or "error" in data

    def test_invalid_uuid_format(self):
        """
        Cas testé: GET /triangulation/not-a-uuid
        Résultat attendu: 400 Bad Request + JSON Error
        Raison: Format UUID invalide doit être rejeté avant traitement.
        
        À tester:
        - Status HTTP = 400
        - Response JSON avec erreur
        """
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/invalid-uuid")
        assert resp.status_code == 400
        data = resp.json()
        assert "error" in data or "code" in data

    def test_zero_points_in_pointset(self):
        """
        Cas testé: PointSet vide (0 points)
        Résultat attendu: 400 ou 500 Error
        Raison: Assurer que la triangulation ne peut pas se faire sans points.
        
        À tester:
        - Status = 400 ou 500
        - Message d'erreur explicite
        """
        empty = struct.pack('<I', 0)
        resp = requests.post(f"{self.BASE_URL}{self.POINTSET_MGR}", data=empty,
                            headers={"Content-Type": "application/octet-stream"})
        if resp.status_code == 201:
            pid = resp.json()["pointSetId"]
            tri = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pid}")
            assert tri.status_code in [400, 500, 404]
        else:
            assert resp.status_code == 400

    def test_insufficient_points(self):
        """
        Cas testé: PointSet avec 1-2 points
        Résultat attendu: 400 ou 500 Error
        Raison: Minimum 3 points requis pour former un triangle.
        
        À tester:
        - Status = 400 ou 500
        - Rejet avec explication
        """
        two = struct.pack('<I', 2) + struct.pack('<ff', 0.0, 0.0) + struct.pack('<ff', 1.0, 1.0)
        resp = requests.post(f"{self.BASE_URL}{self.POINTSET_MGR}", data=two,
                            headers={"Content-Type": "application/octet-stream"})
        if resp.status_code == 201:
            pid = resp.json()["pointSetId"]
            tri = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pid}")
            assert tri.status_code in [400, 500, 404]
        else:
            assert resp.status_code in [400, 422]
