# Makefile pour le projet Triangulator
# Commandes pour tests, couverture, qualité et documentation

.PHONY: test unit_test perf_test coverage lint doc clean help

# Par défaut: afficher l'aide
help:
	@echo "Commandes disponibles:"
	@echo "  make test       - Lancer tous les tests (unitaires + integration + performance)"
	@echo "  make unit_test  - Lancer seulement les tests unitaires et integration (sans performance)"
	@echo "  make perf_test  - Lancer seulement les tests de performance"
	@echo "  make coverage   - Generer le rapport de couverture de code"
	@echo "  make lint       - Verifier la qualite du code avec ruff"
	@echo "  make doc        - Generer la documentation HTML"
	@echo "  make clean      - Nettoyer les fichiers generes"

# Lancer tous les tests
test:
	pytest tests/ -v

# Lancer tests unitaires et integration (exclure performance)
unit_test:
	pytest tests/unit/ tests/integration/ -v

# Lancer uniquement les tests de performance
perf_test:
	pytest tests/performance/ -v -m performance

# Generer le rapport de couverture
coverage:
	coverage run -m pytest tests/unit/ tests/integration/
	coverage report
	coverage html
	@echo "Rapport HTML genere dans htmlcov/index.html"

# Verifier la qualite du code
lint:
	ruff check .

# Generer la documentation
doc:
	pdoc --html --output-dir docs --force triangulator_core app
	@echo "Documentation generee dans docs/"

# Nettoyer les fichiers temporaires
clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov docs
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
