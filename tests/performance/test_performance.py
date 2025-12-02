"""
PLAN.md - Tests de performance
"""

import pytest
import requests
import struct
import time
import random


class TestPerformance:
    """Tests de performance"""

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

    def _generate_points(self, n):
        """Générer n points aléatoires"""
        points = []
        for i in range(n):
            x = random.uniform(-100.0, 100.0)
            y = random.uniform(-100.0, 100.0)
            points.append({"x": x, "y": y})
        return points

    def test_triangulation_10_points(self):
        """
        Cas testé: GET /triangulation/{uuid} avec 10 points
        Résultat attendu: Réponse < 0.5 secondes
        Raison: Vérifier la rapidité sur petits ensembles.
        
        À tester:
        - Mesurer temps requis (début requête → fin réception)
        - Vérifier < 0.5s
        - Status 200 + réponse valide
        """
        points = self._generate_points(10)
        pointset_id = self._register_pointset(points)
        
        start = time.time()
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        elapsed = time.time() - start
        
        assert resp.status_code == 200
        assert elapsed < 0.5, f"Expected < 0.5s, got {elapsed:.3f}s"

    def test_triangulation_100_points(self):
        """
        Cas testé: GET /triangulation/{uuid} avec 100 points
        Résultat attendu: Réponse < 1 seconde
        Raison: Confirmer la performance sur ensembles moyens.
        
        À tester:
        - Temps < 1s
        - Pas de timeout
        - Qualité de réponse identique aux 10 points
        """
        points = self._generate_points(100)
        pointset_id = self._register_pointset(points)
        
        start = time.time()
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        elapsed = time.time() - start
        
        assert resp.status_code == 200
        assert elapsed < 1.0, f"Expected < 1.0s, got {elapsed:.3f}s"

    def test_triangulation_1000_points(self):
        """
        Cas testé: GET /triangulation/{uuid} avec 1000 points
        Résultat attendu: Réponse < 3 secondes
        Raison: Tester la scalabilité sur grands ensembles.
        
        À tester:
        - Temps < 3s
        - Pas de crash
        - Mémoire stable
        """
        points = self._generate_points(1000)
        pointset_id = self._register_pointset(points)
        
        start = time.time()
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        elapsed = time.time() - start
        
        assert resp.status_code == 200
        assert elapsed < 3.0, f"Expected < 3.0s, got {elapsed:.3f}s"

    def test_triangulation_10000_points(self):
        """
        Cas testé: GET /triangulation/{uuid} avec 10000 points
        Résultat attendu: Réponse < 10 secondes
        Raison: Vérifier le comportement sous forte charge.
        
        À tester:
        - Temps < 10s
        - Service reste stable
        - Pas de perte de données
        """
        points = self._generate_points(10000)
        pointset_id = self._register_pointset(points)
        
        start = time.time()
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        elapsed = time.time() - start
        
        assert resp.status_code == 200
        assert elapsed < 10.0, f"Expected < 10.0s, got {elapsed:.3f}s"

    def test_binary_parsing_performance(self):
        """
        Cas testé: Parser réponse binary (10000 points)
        Résultat attendu: Parsing < 2 secondes
        Raison: Assurer que la conversion binary reste efficace.
        
        À tester:
        - Temps de parsing binary < 2s
        - Extraction vertices correcte
        - Extraction triangles correcte
        """
        points = self._generate_points(10000)
        pointset_id = self._register_pointset(points)
        
        resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
        assert resp.status_code == 200
        
        binary = resp.content
        
        # Mesurer le temps de parsing
        start = time.time()
        
        # Parser les vertices
        n_verts = struct.unpack('<I', binary[0:4])[0]
        verts_data = binary[4:4 + n_verts*8]
        vertices = []
        for i in range(n_verts):
            x, y = struct.unpack('<ff', verts_data[i*8:(i+1)*8])
            vertices.append((x, y))
        
        # Parser les triangles
        n_tri_off = 4 + n_verts * 8
        n_tris = struct.unpack('<I', binary[n_tri_off:n_tri_off+4])[0]
        tris_data = binary[n_tri_off + 4:]
        triangles = []
        for i in range(n_tris):
            idx1, idx2, idx3 = struct.unpack('<III', tris_data[i*12:(i+1)*12])
            triangles.append((idx1, idx2, idx3))
        
        elapsed = time.time() - start
        
        assert len(vertices) == n_verts
        assert len(triangles) == n_tris
        assert elapsed < 2.0, f"Parsing took {elapsed:.3f}s, expected < 2.0s"
