"""PLAN.md - Tests unitaires - Section 4: Conversion binaire / serialisation.

Tests de serialisation/parsing binaire.
- Points apres encodage/decodage identiques
- Triangles apres conversion coherents
- Donnees binaires invalides -> erreur
"""

import struct

import pytest

from triangulator_core import (
    compute_triangulation,
    parse_triangulation,
    serialize_triangulation,
)


class TestSerialization:
    """Conversion binaire / serialisation."""

    def test_binary_to_triangles_parsing(self):
        """Teste le parsing du format binary contenant les triangles.

        Raison: Confirmer la serialisation bidirectionnelle des triangles.
        """
        points = [{"x": 0.0, "y": 0.0}, {"x": 1.0, "y": 0.0}, {"x": 0.5, "y": 1.0}]
        verts, tris = compute_triangulation(points)
        binary = serialize_triangulation(verts, tris)

        n_verts = struct.unpack("<I", binary[0:4])[0]
        n_tri_off = 4 + n_verts * 8
        n_tris = struct.unpack("<I", binary[n_tri_off : n_tri_off + 4])[0]

        # Verifier les indices des triangles
        tris_data = binary[n_tri_off + 4 :]
        for i in range(n_tris):
            idx1, idx2, idx3 = struct.unpack(
                "<III", tris_data[i * 12 : (i + 1) * 12]
            )
            assert 0 <= idx1 < n_verts, f"Triangle {i}: idx1 out of bounds"
            assert 0 <= idx2 < n_verts, f"Triangle {i}: idx2 out of bounds"
            assert 0 <= idx3 < n_verts, f"Triangle {i}: idx3 out of bounds"

    def test_binary_vertices_match_original(self, sample_10_points):
        """Teste que les vertices extraits du binary = PointSet original.

        Raison: Assurer l'integrite des donnees lors de la serialisation.
        """
        verts, tris = compute_triangulation(sample_10_points)
        binary = serialize_triangulation(verts, tris)

        n_verts = struct.unpack("<I", binary[0:4])[0]
        assert n_verts == len(verts), "Vertex count mismatch"

        verts_data = binary[4 : 4 + n_verts * 8]
        tol = 1e-6  # Float32 precision
        for i, orig_pt in enumerate(verts):
            x, y = struct.unpack("<ff", verts_data[i * 8 : (i + 1) * 8])
            assert abs(x - orig_pt[0]) < tol, f"Vertex {i}: X mismatch"
            assert abs(y - orig_pt[1]) < tol, f"Vertex {i}: Y mismatch"

    def test_parse_roundtrip(self, sample_3_points):
        """Teste que serialiser puis parser donne les memes donnees.

        Raison: Verifier la bidirectionnalite serialisation/parsing.
        """
        verts_orig, tris_orig = compute_triangulation(sample_3_points)
        binary = serialize_triangulation(verts_orig, tris_orig)
        verts_parsed, tris_parsed = parse_triangulation(binary)

        assert len(verts_parsed) == len(verts_orig)
        assert len(tris_parsed) == len(tris_orig)

        tol = 1e-6
        for i, (x_orig, y_orig) in enumerate(verts_orig):
            x_p, y_p = verts_parsed[i]
            assert abs(x_orig - x_p) < tol
            assert abs(y_orig - y_p) < tol

        assert tris_parsed == tris_orig

    def test_corrupted_binary_too_short(self):
        """Teste que des donnees binaires trop courtes levent ValueError.

        Raison: Tester la resistance face a des donnees malformees.
        """
        truncated = struct.pack("<I", 100)  # Claim 100 vertices but send only 4 bytes
        with pytest.raises(ValueError, match="trop court"):
            parse_triangulation(truncated)

    def test_corrupted_binary_length_mismatch(self):
        """Teste que des donnees binaires avec longueur incorrecte levent ValueError.

        Raison: Detecter les donnees corrompues/tronquees.
        """
        # Header claims 1 vertex + 2 triangles, but only provides 1 triangle data
        binary = struct.pack("<I", 1)  # 1 vertex
        binary += struct.pack("<ff", 1.0, 2.0)  # 1 vertex data
        binary += struct.pack("<I", 2)  # Claims 2 triangles
        binary += struct.pack("<III", 0, 0, 0)  # Only 1 triangle data (incomplete)

        with pytest.raises(ValueError):
            parse_triangulation(binary)
