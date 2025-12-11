"""
PLAN.md - Tests unitaires - Section 1: Gestion des erreurs et cas impossibles
"""

"""
PLAN.md - Tests unitaires - Section 1: Gestion des erreurs et cas impossibles

Tests des fonctions de triangulation (sans API).
- 0 point → ValueError
- 1 point → ValueError  
- 2 points → ValueError
"""

import pytest
from triangulator_core import compute_triangulation


class TestErrorHandling:
    """Gestion des erreurs et cas impossibles"""

    def test_zero_points_raises_error(self):
        """
        Cas testé: 0 points
        Résultat attendu: ValueError
        Raison: Assurer que la triangulation ne peut pas se faire sans points.
        """
        with pytest.raises(ValueError):
            compute_triangulation([])

    def test_one_point_raises_error(self):
        """
        Cas testé: 1 point
        Résultat attendu: ValueError
        Raison: Vérifier le comportement pour un nombre de points insuffisant.
        """
        with pytest.raises(ValueError):
            compute_triangulation([{"x": 0.0, "y": 0.0}])

    def test_two_points_raises_error(self):
        """
        Cas testé: 2 points
        Résultat attendu: ValueError
        Raison: Garantir la gestion correcte d'un cas de points insuffisants.
        """
        points = [{"x": 0.0, "y": 0.0}, {"x": 1.0, "y": 1.0}]
        with pytest.raises(ValueError):
            compute_triangulation(points)

    def test_error_message_includes_point_count(self):
        """Vérifier que le message d'erreur inclut le nombre de points."""
        points = [{"x": 0.0, "y": 0.0}]
        with pytest.raises(ValueError, match="3 unique points"):
            compute_triangulation(points)
