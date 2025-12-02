"""
PLAN.md - Tests d'intégration - Section 2: Gestion d'erreur API
"""

import pytest
import requests
import uuid


class TestAPIErrors:
    """Gestion d'erreur API"""

    BASE_URL = "http://localhost:8000"
    TRIANGULATOR = "/triangulation"

    def test_triangulate_with_nonexistent_id(self):
        """
        Cas testé: GET /triangulation/{uuid-not-in-db}
        Résultat attendu: 404 Not Found + JSON Error
        Raison: Vérifier la gestion quand le PointSetID n'existe pas.
        
        À tester:
        - Status HTTP = 404
        - Content-Type = "application/json"
        - Body = {"code": "...", "message": "..."}
        - Message explicite sur l'absence de l'ID
        """
        fake_id = str(uuid.uuid4())
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{fake_id}")
        
        assert resp.status_code == 404
        assert "application/json" in resp.headers.get("Content-Type", "")
        
        data = resp.json()
        assert "code" in data or "error" in data
        assert "message" in data or "detail" in data

    def test_triangulate_with_invalid_uuid_format(self):
        """
        Cas testé: GET /triangulation/not-a-uuid
        Résultat attendu: 400 Bad Request + JSON Error
        Raison: Garantir la robustesse contre les UUID malformés.
        
        À tester:
        - Status HTTP = 400
        - Content-Type = "application/json"
        - Body = {"code": "...", "message": "..."}
        - Message sur le format invalide
        """
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/not-a-uuid")
        
        assert resp.status_code == 400
        assert "application/json" in resp.headers.get("Content-Type", "")
        
        data = resp.json()
        assert "code" in data or "error" in data
        assert "message" in data or "detail" in data
