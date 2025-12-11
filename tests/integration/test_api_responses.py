"""
PLAN.md - Tests d'intégration - Section 1: Réponse API correcte

"""

import requests
import pytest
import struct


class TestAPIResponses:
    """Réponse API correcte"""

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
        Cas testé: API /triangulation/{valid-uuid}
        Résultat attendu: 200 OK + triangles en format binaire
        Raison: Vérifier que l'API retourne correctement les triangles pour un jeu de points valide.
        """
        pointset_id = self._register_pointset(sample_3_points)
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        
        assert resp.status_code == 200
        assert resp.headers.get("Content-Type") == "application/octet-stream"
        assert len(resp.content) > 0
        
        # Vérifier que le format binary est parsable
        binary = resp.content
        n_verts = struct.unpack('<I', binary[0:4])[0]
        assert n_verts > 0

    def test_response_content_type_is_binary(self, sample_10_points):
        """
        Cas testé: Vérifier le Content-Type de la réponse
        Résultat attendu: "application/octet-stream"
        Raison: Confirmer que la réponse est bien en format binaire, pas JSON.
        """
        pointset_id = self._register_pointset(sample_10_points)
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        
        assert resp.status_code == 200
        content_type = resp.headers.get("Content-Type")
        assert content_type is not None
        assert content_type == "application/octet-stream"
        assert "json" not in content_type.lower()

    def test_binary_response_has_valid_structure(self, sample_3_points):
        """
        Cas testé: Parser la réponse binary
        Résultat attendu: Structure valide (N vertices + T triangles)
        Raison: Vérifier que la réponse respecte le format attendu.
        """
        pointset_id = self._register_pointset(sample_3_points)
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        
        assert resp.status_code == 200
        binary = resp.content
        
        # Vérifier la structure
        n_verts = struct.unpack('<I', binary[0:4])[0]
        assert n_verts == len(sample_3_points), "Vertex count should match input"
        
        verts_end = 4 + n_verts * 8
        n_tris = struct.unpack('<I', binary[verts_end:verts_end+4])[0]
        assert n_tris >= 0, "Triangle count must be non-negative"
        
        tris_end = verts_end + 4 + n_tris * 12
        assert len(binary) == tris_end, "Binary length must match structure"
