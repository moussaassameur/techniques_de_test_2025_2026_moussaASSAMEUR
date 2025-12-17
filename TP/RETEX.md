# Retour d'Experience

Ce document presente mon retour d'experience sur le projet de microservice Triangulator realise dans le cadre du TP "Techniques de Test 2025/2026".

## Ce qui a bien fonctionne

- Ecrire le PLAN.md en premier m'a oblige a bien reflechir aux differents cas de test avant de commencer l'implementation.
- La separation entre `triangulator_core.py` (logique pure) et `app.py` (API Flask) a facilite les tests unitaires sans dependance externe.
- Une fois les tests en place, j'ai pu modifier l'implementation avec confiance grace a la couverture de 96%.
- L'utilisation de `app.test_client()` a permis de tester l'API sans avoir a demarrer un serveur.
- Les commandes `make` (`make test`, `make lint`, `make coverage`) ont automatise la verification et m'ont fait gagner du temps.

## Ce qui aurait pu etre mieux fait

### Plan de tests initial

Mon plan de tests etait bien structure mais incomplet. J'ai du ajouter des tests supplementaires pour les cas d'erreur de l'API car au debut je n'avais pas couvert tous les cas possibles. J'ai aussi du faire des ajustements de precision numerique (epsilon) pour la detection des points colineaires.

### Algorithme de triangulation

J'ai choisi un algorithme simple (fan triangulation) pour sa facilite d'implementation et son caractere deterministe. Cependant, pour un projet reel, un algorithme comme Delaunay serait preferable car il produit des triangles de meilleure qualite geometrique.

### Tests de performance initiaux

Mes tests de performance utilisaient initialement la bibliotheque `requests` et necessitaient un serveur actif. J'ai perdu du temps avant de realiser qu'il fallait utiliser `app.test_client()` comme pour les tests d'integration.

## Ce que je ferais differemment

- Utiliser `pytest.mark.parametrize` des le debut pour eviter la duplication de code dans les tests.
- Implementer un algorithme de triangulation plus avance (Delaunay) pour une meilleure qualite.
- Ajouter des property-based tests avec `hypothesis` pour generer automatiquement des cas de test complexes.

## Conclusion

Ce TP m'a permis de comprendre l'interet reel du TDD. Ecrire les tests d'abord oblige a reflechir aux differents cas possibles avant de coder, ce qui evite d'oublier les cas limites et les erreurs. Meme si j'ai rencontre des difficultes (erreurs ruff, problemes avec requests), le fait d'avoir un plan de tests clair m'a guide tout au long du developpement. Au final, j'ai obtenu un code bien teste (96% de couverture) et fonctionnel. C'est une approche que je compte reutiliser dans mes futurs projets car elle donne plus de confiance dans la qualite du code produit.

