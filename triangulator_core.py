"""Module de triangulation pur (sans dependances API).

Fournit les fonctions de base pour:
- Calculer une triangulation simple (fan triangulation)
- Serialiser en format binaire
- Parser le format binaire
- Gerer les cas degeneres (points colineaires, doublons)

Utilise par les tests unitaires et par l'application Flask.
"""

import struct


def _dedupe_points(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Supprimer les points dupliques en conservant l'ordre.

    Args:
        points: Liste de tuples (x, y)

    Returns:
        Liste sans doublons

    """
    seen = {}
    out = []
    for p in points:
        key = (float(p[0]), float(p[1]))
        if key not in seen:
            seen[key] = len(out)
            out.append(key)
    return out


def _is_collinear(points: list[tuple[float, float]], eps: float = 1e-12) -> bool:
    """Check if all points are aligned (collinear).

    Utilise l'aire signee du triangle forme par (p0, p1, pi).
    Si toutes les aires sont ~0, les points sont alignes.

    Args:
        points: Liste d'au moins 3 points
        eps: Tolerance numerique

    Returns:
        True si colineaires, False sinon

    """
    if len(points) < 3:
        return True
    x0, y0 = points[0]
    x1, y1 = points[1]
    for i in range(2, len(points)):
        xi, yi = points[i]
        # Aire signee * 2 = determinant
        area2 = (x1 - x0) * (yi - y0) - (y1 - y0) * (xi - x0)
        if abs(area2) > eps:
            return False
    return True


def compute_triangulation(
    points: list[dict],
) -> tuple[list[tuple[float, float]], list[tuple[int, int, int]]]:
    """Compute simple triangulation for a set of points.

    Algorithme: Fan triangulation (simple et deterministe)
    - Dedupliquer les points identiques
    - Si < 3 points uniques -> ValueError
    - Si points colineaires -> 0 triangle
    - Sinon: triangles en eventail depuis le premier point (0, i, i+1)

    Args:
        points: Liste de dicts {"x": float, "y": float} ou tuples (x, y)

    Returns:
        Tuple (vertices, triangles) ou:
        - vertices: liste de (x, y)
        - triangles: liste de (i, j, k) indices dans vertices

    Raises:
        ValueError: Si moins de 3 points uniques

    """
    # Convertir en tuples (x, y)
    pts = []
    for p in points:
        if isinstance(p, dict):
            pts.append((float(p["x"]), float(p["y"])))
        else:
            pts.append((float(p[0]), float(p[1])))

    # Dedupliquer
    verts = _dedupe_points(pts)
    if len(verts) < 3:
        raise ValueError("Au moins 3 points uniques sont requis pour la triangulation")

    # Cas colineaire: pas de triangles possibles
    if _is_collinear(verts):
        return verts, []

    # Fan triangulation: (0, i, i+1) pour i de 1 a n-2
    n = len(verts)
    tris = []
    for i in range(1, n - 1):
        tris.append((0, i, i + 1))
    return verts, tris


def serialize_triangulation(
    vertices: list[tuple[float, float]],
    triangles: list[tuple[int, int, int]],
) -> bytes:
    """Serialize vertices and triangles to binary format.

    Format:
    - 4 bytes (uint32 LE): N = nombre de vertices
    - N x 8 bytes: pour chaque vertex (float32 x, float32 y)
    - 4 bytes (uint32 LE): T = nombre de triangles
    - T x 12 bytes: pour chaque triangle (uint32 i, uint32 j, uint32 k)

    Args:
        vertices: Liste de (x, y)
        triangles: Liste de (i, j, k) indices

    Returns:
        Bytes du format binaire

    """
    out = struct.pack("<I", len(vertices))
    for x, y in vertices:
        out += struct.pack("<ff", float(x), float(y))
    out += struct.pack("<I", len(triangles))
    for a, b, c in triangles:
        out += struct.pack("<III", int(a), int(b), int(c))
    return out


def parse_triangulation(
    binary: bytes,
) -> tuple[list[tuple[float, float]], list[tuple[int, int, int]]]:
    """Parser le format binaire en (vertices, triangles).

    Verifie la coherence des longueurs et leve ValueError si invalide.

    Args:
        binary: Bytes au format attendu

    Returns:
        Tuple (vertices, triangles)

    Raises:
        ValueError: Si le format est invalide ou corrompu

    """
    if len(binary) < 4:
        raise ValueError("Binaire trop court: nombre de vertices manquant")
    off = 0
    n_verts = struct.unpack_from("<I", binary, off)[0]
    off += 4
    expected_verts_bytes = n_verts * 8
    if len(binary) < off + expected_verts_bytes + 4:
        raise ValueError(
            "Binaire trop court: donnees vertices ou nombre de triangles manquant"
        )
    verts = []
    for _i in range(n_verts):
        x, y = struct.unpack_from("<ff", binary, off)
        verts.append((x, y))
        off += 8
    n_tris = struct.unpack_from("<I", binary, off)[0]
    off += 4
    expected_tris_bytes = n_tris * 12
    if len(binary) != off + expected_tris_bytes:
        raise ValueError("Longueur binaire invalide pour les triangles")
    tris = []
    for _i in range(n_tris):
        a, b, c = struct.unpack_from("<III", binary, off)
        tris.append((a, b, c))
        off += 12
    return verts, tris


__all__ = [
    "compute_triangulation",
    "serialize_triangulation",
    "parse_triangulation",
]
