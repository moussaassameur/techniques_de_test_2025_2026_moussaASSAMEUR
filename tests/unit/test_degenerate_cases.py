"""
PLAN.md - Tests unitaires - Section 3: Cas dégénérés ou particuliers
"""

"""
PLAN.md - Tests unitaires - Section 3: Cas dégénérés ou particuliers

Tests des cas limites sans API.
- Points colinéaires → 0 triangle
- Points dupliqués → Déduplication automatique
"""

import pytest
from triangulator_core import compute_triangulation


class TestDegenerateCases:
    """Cas dégénérés ou particuliers"""

    def test_collinear_points_returns_empty_triangles(self, collinear_points):
        """
        Cas testé: Points alignés (colinéaires)
        Résultat attendu: 0 triangle
        Raison: Tester la gestion de points qui ne permettent pas de former de triangles.
        """
        verts, tris = compute_triangulation(collinear_points)
        
        assert len(verts) == 3, "Should have 3 vertices (non-deduplicated)"
        assert len(tris) == 0, "Collinear points should yield no triangles"

    def test_duplicate_points_are_deduplicated(self, duplicate_points):
        """
        Cas testé: Points dupliqués
        Résultat attendu: Déduplication avant triangulation
        Raison: Vérifier que les doublons n'affectent pas la triangulation.
        """
        verts, tris = compute_triangulation(duplicate_points)
        
        # duplicate_points = [p0, p1, p2, p1 (dup)]
        # After dedup should have 3 unique points
        assert len(verts) == 3, "Duplicates should be removed"
        
        # With 3 unique points (non-collinear), should have 1 triangle
        assert len(tris) == 1, "3 unique points should yield 1 triangle"

    def test_many_duplicate_points_single_triangle(self):
        """
        Cas testé: Plusieurs points dupliqués
        Résultat attendu: Déduplication et triangulation correcte
        Raison: Assurer que la triangulation fonctionne avec doublons multiples.
        """
        points = [
            {"x": 0.0, "y": 0.0},
            {"x": 0.0, "y": 0.0},
            {"x": 1.0, "y": 0.0},
            {"x": 1.0, "y": 0.0},
            {"x": 0.5, "y": 1.0},
            {"x": 0.5, "y": 1.0},
        ]
        verts, tris = compute_triangulation(points)
        
        assert len(verts) == 3, "Should deduplicate to 3 unique points"
        assert len(tris) == 1, "3 unique non-collinear points → 1 triangle"
