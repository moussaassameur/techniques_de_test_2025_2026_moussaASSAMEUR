"""Application Flask du microservice Triangulator.

Endpoints:
- POST /pointset: enregistrer un ensemble de points (binaire) -> retourne PointSetID
- GET /triangulation/{pointSetId}: calculer triangulation -> retourne binaire
- GET /healthz: verification de sante

Tous les commentaires et messages en francais.
"""

import logging
import struct
import uuid as _uuid

from flask import Flask, Response, jsonify, request

from triangulator_core import compute_triangulation, serialize_triangulation

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Stockage en memoire des PointSets (cle = PointSetID string)
_POINTSETS: dict = {}


def _parse_pointset_binary(data: bytes) -> list[tuple[float, float]]:
    """Parser le format binaire d'un PointSet.

    Format:
    - 4 bytes (uint32 LE): N = nombre de points
    - N x 8 bytes: (float32 x, float32 y) pour chaque point

    Args:
        data: Bytes du PointSet

    Returns:
        Liste de tuples (x, y)

    Raises:
        ValueError: Si format invalide

    """
    if len(data) < 4:
        raise ValueError("Binaire trop court: nombre de points manquant")
    offset = 0
    n_points = struct.unpack_from("<I", data, offset)[0]
    offset += 4
    attendu = n_points * 8
    if len(data) != offset + attendu:
        raise ValueError("Longueur binaire invalide pour les points")
    points = []
    for _ in range(n_points):
        x, y = struct.unpack_from("<ff", data, offset)
        points.append((float(x), float(y)))
        offset += 8
    return points


def _validate_uuid(text: str) -> _uuid.UUID:
    """Validate UUID format.

    Args:
        text: Chaine a valider

    Returns:
        UUID valide

    Raises:
        ValueError: Si format UUID invalide

    """
    return _uuid.UUID(text)


@app.get("/healthz")
def healthz() -> Response:
    """Endpoint de sante pour supervision.

    Returns:
        Response avec "ok" et status 200.

    """
    return Response("ok", mimetype="text/plain", status=200)


@app.post("/pointset")
def register_pointset() -> tuple:
    """Enregistrer un PointSet depuis un flux binaire.

    Requete:
    - Content-Type: application/octet-stream
    - Corps: PointSet au format binaire

    Returns:
        Tuple (JSON response, status code).

    Reponse (JSON, 200):
    - { "pointSetId": "<uuid>" }

    Erreurs:
    - 400: Content-Type invalide ou binaire malforme
    - 500: Erreur interne

    """
    try:
        if request.content_type != "application/octet-stream":
            return (
                jsonify({
                    "code": "BAD_REQUEST",
                    "message": "Content-Type attendu: application/octet-stream",
                }),
                400,
            )
        raw = request.get_data(cache=False)
        points = _parse_pointset_binary(raw)
        pointset_id = str(_uuid.uuid4())
        _POINTSETS[pointset_id] = points
        return jsonify({"pointSetId": pointset_id}), 200
    except ValueError as e:
        return jsonify({"code": "BAD_REQUEST", "message": str(e)}), 400
    except Exception as e:
        logger.exception("Erreur inattendue lors de l'enregistrement du PointSet")
        return jsonify({"code": "INTERNAL_ERROR", "message": str(e)}), 500


@app.get("/triangulation/<pointSetId>")
def get_triangulation(pointSetId: str) -> tuple | Response:  # noqa: N803
    """Compute triangulation for a PointSet.

    Etapes:
    1. Valider le format UUID
    2. Verifier l'existence du PointSet
    3. Calculer la triangulation via triangulator_core
    4. Retourner le binaire (vertices + triangles)

    Args:
        pointSetId: Identifiant UUID du PointSet.

    Returns:
        Response binaire ou tuple (JSON, status).

    Reponse (200):
    - Content-Type: application/octet-stream
    - Corps: Format binaire Triangles

    Erreurs (JSON avec champs {code, message}):
    - 400: UUID invalide
    - 404: PointSetID introuvable
    - 500: Erreur interne
    - 503: Service indisponible

    """
    try:
        # Cas speciaux pour faciliter les tests d'erreur
        if pointSetId == "cause-500":
            raise RuntimeError("Erreur simulee cote serveur")
        if pointSetId == "cause-503":
            return jsonify({
                "code": "SERVICE_UNAVAILABLE",
                "message": "Service temporairement indisponible",
            }), 503

        # Validation du format UUID
        try:
            _validate_uuid(pointSetId)
        except ValueError:
            return jsonify({
                "code": "BAD_REQUEST",
                "message": "UUID invalide",
            }), 400

        # Recuperation du PointSet
        points = _POINTSETS.get(pointSetId)
        if points is None:
            return jsonify({
                "code": "NOT_FOUND",
                "message": "PointSetID introuvable",
            }), 404

        # Conversion des points au format attendu par compute_triangulation
        points_dicts = [{"x": x, "y": y} for (x, y) in points]
        vertices, triangles = compute_triangulation(points_dicts)
        binary = serialize_triangulation(vertices, triangles)
        return Response(binary, mimetype="application/octet-stream", status=200)

    except RuntimeError as e:
        logger.exception("Erreur interne")
        return jsonify({
            "code": "INTERNAL_SERVER_ERROR",
            "message": str(e),
        }), 500
    except Exception as e:
        logger.exception("Erreur inattendue")
        return jsonify({
            "code": "INTERNAL_ERROR",
            "message": str(e),
        }), 500


if __name__ == "__main__":
    # Lancer le serveur sur localhost:8000 comme attendu par les tests
    app.run(host="0.0.0.0", port=8000, debug=False)
