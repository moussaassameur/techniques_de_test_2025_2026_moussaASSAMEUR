"""Fixtures reutilisables pour tous les tests."""

import os
import sys

import pytest

# Ajouter le repertoire racine au PYTHONPATH pour importer triangulator_core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_3_points():
    """Retourne 3 points non alignes formant un triangle."""
    return [
        {"x": 0.0, "y": 0.0},
        {"x": 1.0, "y": 0.0},
        {"x": 0.5, "y": 1.0},
    ]


@pytest.fixture
def sample_10_points():
    """Retourne 10 points pour triangulation."""
    return [
        {"x": 0.0, "y": 0.0},
        {"x": 1.0, "y": 0.0},
        {"x": 1.5, "y": 0.5},
        {"x": 1.0, "y": 1.0},
        {"x": 0.5, "y": 1.2},
        {"x": 0.0, "y": 1.0},
        {"x": -0.5, "y": 0.5},
        {"x": 0.2, "y": 0.3},
        {"x": 0.5, "y": 0.5},
        {"x": 0.8, "y": 0.7},
    ]


@pytest.fixture
def collinear_points():
    """Retourne des points alignes sur une ligne."""
    return [
        {"x": 0.0, "y": 0.0},
        {"x": 1.0, "y": 1.0},
        {"x": 2.0, "y": 2.0},
    ]


@pytest.fixture
def duplicate_points():
    """Retourne des points avec doublons."""
    return [
        {"x": 0.0, "y": 0.0},
        {"x": 1.0, "y": 0.0},
        {"x": 0.5, "y": 1.0},
        {"x": 1.0, "y": 0.0},
    ]
