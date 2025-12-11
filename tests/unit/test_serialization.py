"""
PLAN.md - Tests unitaires - Section 4: Conversion binaire / sérialisation
"""

"""
PLAN.md - Tests unitaires - Section 4: Conversion binaire / sérialisation

Tests de sérialisation/parsing binaire (sans API).
- Points après encodage/décodage identiques
- Triangles après conversion cohérents
- Données binaires invalides → erreur
"""

import pytest
import struct
from triangulator_core import compute_triangulation, serialize_triangulation, parse_triangulation


class TestSerialization:
    """Conversion binaire / sérialisation"""

    def test_binary_to_triangles_parsing(self):
        """
        Cas testé: Parser le format binary contenant les triangles
        Résultat attendu: Structure correcte, tous les indices valides
        Raison: Confirmer la sérialisation bidirectionnelle des triangles.
        """
        points = [{"x": 0.0, "y": 0.0}, {"x": 1.0, "y": 0.0}, {"x": 0.5, "y": 1.0}]
        verts, tris = compute_triangulation(points)
        binary = serialize_triangulation(verts, tris)

        n_verts = struct.unpack('<I', binary[0:4])[0]
        n_tri_off = 4 + n_verts * 8
        n_tris = struct.unpack('<I', binary[n_tri_off:n_tri_off+4])[0]

        # Vérifier les indices des triangles
        tris_data = binary[n_tri_off + 4:]
        for i in range(n_tris):
            idx1, idx2, idx3 = struct.unpack('<III', tris_data[i*12:(i+1)*12])
            assert 0 <= idx1 < n_verts, f"Triangle {i}: idx1 out of bounds"
            assert 0 <= idx2 < n_verts, f"Triangle {i}: idx2 out of bounds"
            assert 0 <= idx3 < n_verts, f"Triangle {i}: idx3 out of bounds"

    def test_binary_vertices_match_original(self, sample_10_points):
        """
        Cas testé: Vertices extraits du binary = PointSet original
        Résultat attendu: Points identiques après conversion binaire
        Raison: Assurer l'intégrité des données lors de la sérialisation.
        """
        verts, tris = compute_triangulation(sample_10_points)
        binary = serialize_triangulation(verts, tris)

        n_verts = struct.unpack('<I', binary[0:4])[0]
        assert n_verts == len(verts), "Vertex count mismatch"

        verts_data = binary[4:4 + n_verts*8]
        tol = 1e-6  # Float32 precision
        for i, orig_pt in enumerate(verts):
            x, y = struct.unpack('<ff', verts_data[i*8:(i+1)*8])
            assert abs(x - orig_pt[0]) < tol, f"Vertex {i}: X mismatch"
            assert abs(y - orig_pt[1]) < tol, f"Vertex {i}: Y mismatch"

    def test_parse_roundtrip(self, sample_3_points):
        """
        Cas testé: Sérialiser puis parser donne les mêmes données
        Résultat attendu: Roundtrip cohérent
        Raison: Vérifier la bidirectionnalité sérialisation/parsing.
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
        """
        Cas testé: Données binaires trop courtes (corrompues)
        Résultat attendu: ValueError lors du parsing
        Raison: Tester la résistance face à des données malformées.
        """
        truncated = struct.pack('<I', 100)  # Claim 100 vertices but send only 4 bytes
        with pytest.raises(ValueError, match="too short"):
            parse_triangulation(truncated)

    def test_corrupted_binary_length_mismatch(self):
        """
        Cas testé: Données binaires avec longueur incorrecte
        Résultat attendu: ValueError lors du parsing
        Raison: Détecter les données corrompues/tronquées.
        """
        # Valid header for 1 vert + 1 tri, but incorrect length
        binary = struct.pack('<I', 1)  # 1 vertex
        binary += struct.pack('<ff', 1.0, 2.0)  # 1 vertex data
        binary += struct.pack('<I', 1)  # 1 triangle
        binary += struct.pack('<III', 0, 1, 2)  # triangle (incomplete/invalid)
        
        with pytest.raises(ValueError):
            parse_triangulation(binary)
