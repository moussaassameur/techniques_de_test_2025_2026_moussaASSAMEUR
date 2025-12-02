"""
PLAN.md - Tests d'intégration - Section 3: Stabilité et charge
"""

import pytest
import requests
import struct
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestStabilityAndLoad:
    """Stabilité et charge"""

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

    def test_multiple_simultaneous_requests(self):
        """
        Cas testé: Plusieurs GET /triangulation simultanées
        Résultat attendu: Pas d'erreur, toutes reçoivent 200
        Raison: Tester la capacité de l'API à gérer la concurrence.
        
        À tester:
        - Lancer N requêtes parallèles (ex: 10-50)
        - Vérifier que toutes reçoivent 200
        - Pas de timeout ou deadlock
        - Réponses correctes et complètes
        - Pas de corruption de données
        """
        # Créer 5 PointSets différents pour les requêtes parallèles
        pointset_ids = []
        for i in range(5):
            points = [
                {"x": float(i), "y": 0.0},
                {"x": float(i+1), "y": 0.0},
                {"x": float(i+0.5), "y": 1.0}
            ]
            pointset_ids.append(self._register_pointset(points))
        
        # Lancer 10 requêtes parallèles (2 pour chaque PointSet)
        def fetch_triangulation(pointset_id):
            resp = requests.get(f"{self.BASE_URL}{self.TRIANGULATOR}/{pointset_id}")
            return resp.status_code, len(resp.content)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for _ in range(2):
                for pid in pointset_ids:
                    futures.append(executor.submit(fetch_triangulation, pid))
            
            # Collecter les résultats
            results = []
            for future in as_completed(futures):
                status, size = future.result()
                results.append((status, size))
        
        # Vérifier que toutes les requêtes ont réussi
        assert len(results) == 10
        for status, size in results:
            assert status == 200, f"Expected 200, got {status}"
            assert size > 0, "Response should not be empty"
