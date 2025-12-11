"""
PLAN.md - Tests unitaires - Section 5: Robustesse numérique
"""

"""
PLAN.md - Tests unitaires - Section 5: Robustesse numérique

Tests avec valeurs extrêmes (sans API).
- Très grandes valeurs → pas de crash, résultats finis
- Très petites valeurs → pas de crash, résultats finis
"""

import pytest
import math
from triangulator_core import compute_triangulation


class TestNumericalRobustness:
    """Robustesse numérique"""

    def test_extreme_large_values(self):
        """
        Cas testé: Coordonnées très grandes
        Résultat attendu: Pas de crash, triangulation valide
        Raison: S'assurer que le service gère correctement les valeurs extrêmes.
        """
        extreme_pts = [
            {"x": 1e10, "y": 1e10},
            {"x": 2e10, "y": 1e10},
            {"x": 1.5e10, "y": 2e10},
        ]
        
        verts, tris = compute_triangulation(extreme_pts)
        
        assert len(verts) == 3
        assert len(tris) == 1
        
        # Vérifier qu'il n'y a pas de NaN ou Infinity
        for i, (x, y) in enumerate(verts):
            assert math.isfinite(x), f"Vertex {i}: x is not finite"
            assert math.isfinite(y), f"Vertex {i}: y is not finite"

    def test_extreme_small_values(self):
        """
        Cas testé: Coordonnées très petites
        Résultat attendu: Pas de crash, triangulation valide
        Raison: Vérifier la robustesse avec des valeurs très faibles.
        """
        extreme_pts = [
            {"x": 1e-10, "y": 1e-10},
            {"x": 2e-10, "y": 1e-10},
            {"x": 1.5e-10, "y": 2e-10},
        ]
        
        verts, tris = compute_triangulation(extreme_pts)
        
        assert len(verts) == 3
        assert len(tris) == 1
        
        # Vérifier qu'il n'y a pas de NaN ou Infinity
        for i, (x, y) in enumerate(verts):
            assert math.isfinite(x), f"Vertex {i}: x is not finite"
            assert math.isfinite(y), f"Vertex {i}: y is not finite"

    def test_mixed_extreme_values(self):
        """
        Cas testé: Mélange de valeurs très grandes et très petites
        Résultat attendu: Triangulation correcte sans débordement
        Raison: Tester la robustesse avec des amplitudes différentes.
        """
        extreme_pts = [
            {"x": 1e-10, "y": 1e-10},
            {"x": 1e10, "y": 1e10},
            {"x": 0.0, "y": 1e5},
            {"x": 1e-5, "y": 1e-5},
        ]
        
        verts, tris = compute_triangulation(extreme_pts)
        
        assert len(verts) == 4, "Should have 4 unique vertices"
        assert len(tris) == 2, "4 unique points → 2 triangles in fan"
        
        # Vérifier tous les vertices
        for i, (x, y) in enumerate(verts):
            assert math.isfinite(x), f"Vertex {i}: x is NaN or Inf"
            assert math.isfinite(y), f"Vertex {i}: y is NaN or Inf"
        
        # Vérifier les indices des triangles
        for tri_idx, (a, b, c) in enumerate(tris):
            assert 0 <= a < len(verts), f"Triangle {tri_idx}: index a out of bounds"
            assert 0 <= b < len(verts), f"Triangle {tri_idx}: index b out of bounds"
            assert 0 <= c < len(verts), f"Triangle {tri_idx}: index c out of bounds"

    def test_negative_coordinates(self):
        """
        Cas testé: Coordonnées négatives
        Résultat attendu: Triangulation correcte
        Raison: Assurer que les valeurs négatives sont gérées correctement.
        """
        pts = [
            {"x": -1.0, "y": -1.0},
            {"x": 1.0, "y": -1.0},
            {"x": 0.0, "y": 1.0},
        ]
        
        verts, tris = compute_triangulation(pts)
        
        assert len(verts) == 3
        assert len(tris) == 1
        
        for x, y in verts:
            assert math.isfinite(x)
            assert math.isfinite(y)
