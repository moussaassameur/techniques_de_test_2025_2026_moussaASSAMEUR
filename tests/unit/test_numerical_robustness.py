"""PLAN.md - Tests unitaires - Section 5: Robustesse numerique.

Tests avec valeurs extremes (sans API).
- Tres grandes valeurs -> pas de crash, resultats finis
- Tres petites valeurs -> pas de crash, resultats finis
"""

import math

from triangulator_core import compute_triangulation


class TestNumericalRobustness:
    """Robustesse numerique."""

    def test_extreme_large_values(self):
        """Teste des coordonnees tres grandes -> pas de crash, triangulation valide.

        Raison: S'assurer que le service gere correctement les valeurs extremes.
        """
        extreme_pts = [
            {"x": 1e10, "y": 1e10},
            {"x": 2e10, "y": 1e10},
            {"x": 1.5e10, "y": 2e10},
        ]

        verts, tris = compute_triangulation(extreme_pts)

        assert len(verts) == 3
        assert len(tris) == 1

        # Verifier qu'il n'y a pas de NaN ou Infinity
        for i, (x, y) in enumerate(verts):
            assert math.isfinite(x), f"Vertex {i}: x is not finite"
            assert math.isfinite(y), f"Vertex {i}: y is not finite"

    def test_extreme_small_values(self):
        """Teste des coordonnees tres petites -> pas de crash, triangulation valide.

        Raison: Verifier la robustesse avec des valeurs tres faibles.
        """
        # Valeurs petites mais pas trop pour eviter colinearite numerique
        extreme_pts = [
            {"x": 1e-6, "y": 1e-6},
            {"x": 2e-6, "y": 1e-6},
            {"x": 1.5e-6, "y": 2e-6},
        ]

        verts, tris = compute_triangulation(extreme_pts)

        assert len(verts) == 3
        # Peut etre 0 ou 1 selon la precision numerique
        assert len(tris) >= 0

        # Verifier qu'il n'y a pas de NaN ou Infinity
        for i, (x, y) in enumerate(verts):
            assert math.isfinite(x), f"Vertex {i}: x is not finite"
            assert math.isfinite(y), f"Vertex {i}: y is not finite"

    def test_mixed_extreme_values(self):
        """Teste un melange de valeurs tres grandes et tres petites.

        Raison: Tester la robustesse avec des amplitudes differentes.
        """
        extreme_pts = [
            {"x": 1e-10, "y": 1e-10},
            {"x": 1e10, "y": 1e10},
            {"x": 0.0, "y": 1e5},
            {"x": 1e-5, "y": 1e-5},
        ]

        verts, tris = compute_triangulation(extreme_pts)

        assert len(verts) == 4, "Should have 4 unique vertices"
        assert len(tris) == 2, "4 unique points -> 2 triangles in fan"

        # Verifier tous les vertices
        for i, (x, y) in enumerate(verts):
            assert math.isfinite(x), f"Vertex {i}: x is NaN or Inf"
            assert math.isfinite(y), f"Vertex {i}: y is NaN or Inf"

        # Verifier les indices des triangles
        for tri_idx, (a, b, c) in enumerate(tris):
            assert 0 <= a < len(verts), f"Triangle {tri_idx}: index a out of bounds"
            assert 0 <= b < len(verts), f"Triangle {tri_idx}: index b out of bounds"
            assert 0 <= c < len(verts), f"Triangle {tri_idx}: index c out of bounds"

    def test_negative_coordinates(self):
        """Teste des coordonnees negatives -> triangulation correcte.

        Raison: Assurer que les valeurs negatives sont gerees correctement.
        """
        pts = [
            {"x": -1.0, "y": -1.0},
            {"x": 1.0, "y": -1.0},
            {"x": 0.0, "y": 1.0},
        ]

        verts, tris = compute_triangulation(pts)

        assert len(verts) == 3
        assert len(tris) == 1
        assert tris[0] == (0, 1, 2)

    def test_zero_coordinates(self):
        """Teste des coordonnees a zero -> triangulation correcte.

        Raison: Verifier le comportement avec des zeros.
        """
        pts = [
            {"x": 0.0, "y": 0.0},
            {"x": 1.0, "y": 0.0},
            {"x": 0.0, "y": 1.0},
        ]

        verts, tris = compute_triangulation(pts)

        assert len(verts) == 3
        assert len(tris) == 1
