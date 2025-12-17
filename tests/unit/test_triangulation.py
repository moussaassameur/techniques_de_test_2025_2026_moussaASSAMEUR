"""PLAN.md - Tests unitaires - Section 2: Cas de triangulation normale.

Tests des fonctions de triangulation.
- 3 points non alignes -> 1 triangle
- 10 points -> Plusieurs triangles
"""

from triangulator_core import compute_triangulation


class TestNormalTriangulation:
    """Cas de triangulation normale."""

    def test_three_non_collinear_points(self, sample_3_points):
        """Teste 3 points non alignes -> 1 triangle avec indices (0, 1, 2).

        Raison: Confirmer que le service triangule correctement le cas minimal.
        """
        verts, tris = compute_triangulation(sample_3_points)

        assert len(verts) == 3, "Should have 3 vertices"
        assert len(tris) == 1, "Should have exactly 1 triangle"
        assert tris[0] == (0, 1, 2), "Triangle should connect all 3 points"

    def test_triangulation_10_points(self, sample_10_points):
        """Teste 10 points non colineaires -> n-2 = 8 triangles en fan.

        Raison: Valider que la triangulation fonctionne sur des ensembles standards.
        """
        verts, tris = compute_triangulation(sample_10_points)

        assert len(verts) == 10, "Should have 10 unique vertices"
        assert len(tris) == 8, "Fan triangulation: n-2 = 8 triangles"

        # Verifier que tous les indices des triangles sont valides
        for tri in tris:
            a, b, c = tri
            assert 0 <= a < len(verts), f"Index {a} out of bounds"
            assert 0 <= b < len(verts), f"Index {b} out of bounds"
            assert 0 <= c < len(verts), f"Index {c} out of bounds"

    def test_triangle_vertex_references_valid(self, sample_10_points):
        """Teste que tous les indices de triangles pointent vers des vertices valides.

        Raison: Assurer l'integrite des donnees de triangulation.
        """
        verts, tris = compute_triangulation(sample_10_points)
        n_verts = len(verts)

        for tri_idx, (a, b, c) in enumerate(tris):
            assert 0 <= a < n_verts, f"Triangle {tri_idx}: index a={a} invalid"
            assert 0 <= b < n_verts, f"Triangle {tri_idx}: index b={b} invalid"
            assert 0 <= c < n_verts, f"Triangle {tri_idx}: index c={c} invalid"
            assert (
                a != b and b != c and a != c
            ), f"Triangle {tri_idx}: has duplicate indices"
