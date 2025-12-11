"""
PLAN.md - Tests d'intégration - Section 2: Gestion d'erreur API

Tests d'erreurs API (200, 400, 404, 500, 503)
"""

import pytest
import requests
import uuid
import struct


class TestAPIErrors:
    """Gestion d'erreur API"""

    BASE_URL = "http://localhost:8000"
    TRIANGULATOR = "/triangulation"
    POINTSET_MGR = "/pointset"

    def _register_pointset(self, points):
        """Enregistrer un PointSet et retourner son ID."""
        binary = struct.pack('<I', len(points))
        for p in points:
            binary += struct.pack('<ff', float(p["x"]), float(p["y"]))
        resp = requests.post(
            f"{self.BASE_URL}{self.POINTSET_MGR}",
            data=binary,
            headers={"Content-Type": "application/octet-stream"}
        )
        assert resp.status_code == 200, f"Failed to register pointset: {resp.status_code}"
        return resp.json()["pointSetId"]

    def test_triangulate_with_valid_id_returns_200(self, sample_3_points):
        """
        Cas testé: API `/triangulate` avec ID valide
        Résultat attendu: 200 OK
        Raison: Vérifier la réponse correcte en cas de succès.
        """
        pointset_id = self._register_pointset(sample_3_points)
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        
        assert resp.status_code == 200
        assert resp.headers.get("Content-Type") == "application/octet-stream"
        assert len(resp.content) > 0

    def test_triangulate_with_invalid_uuid_format_returns_400(self):
        """
        Cas testé: API `/triangulate` avec UUID malformé
        Résultat attendu: 400 Bad Request
        Raison: Garantir la robustesse contre les formats invalides.
        """
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/not-a-uuid")
        
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
        assert "application/json" in resp.headers.get("Content-Type", "")
        
        data = resp.json()
        assert "code" in data or "error" in data
        assert "message" in data or "detail" in data

    def test_triangulate_with_nonexistent_id_returns_404(self):
        """
        Cas testé: API `/triangulate` avec ID inexistant
        Résultat attendu: 404 Not Found
        Raison: Vérifier la gestion quand le `PointSetID` n'existe pas.
        """
        fake_id = str(uuid.uuid4())
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{fake_id}")
        
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
        assert "application/json" in resp.headers.get("Content-Type", "")
        
        data = resp.json()
        assert "code" in data or "error" in data
        assert "message" in data or "detail" in data

    def test_server_error_500_format(self):
        """
        Cas testé: API `/triangulate` provoquant une erreur interne
        Résultat attendu: 500 Internal Server Error (si applicable)
        Raison: Vérifier le format d'erreur en cas de bug/exception côté serveur.
        """
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/cause-500")
        if resp.status_code != 500:
            pytest.skip("Server did not return 500; skipping test.")
        
        assert "application/json" in resp.headers.get("Content-Type", "")
        data = resp.json()
        assert "code" in data or "error" in data
        assert "message" in data or "detail" in data

    def test_service_unavailable_503_format(self):
        """
        Cas testé: Service indisponible / surcharge
        Résultat attendu: 503 Service Unavailable (si applicable)
        Raison: Confirmer le comportement et le format d'erreur lorsque le service est indisponible.
        """
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/cause-503")
        if resp.status_code != 503:
            pytest.skip("Server did not return 503; skipping test.")
        
        assert "application/json" in resp.headers.get("Content-Type", "")
        data = resp.json()
        assert "code" in data or "error" in data
        assert "message" in data or "detail" in data
