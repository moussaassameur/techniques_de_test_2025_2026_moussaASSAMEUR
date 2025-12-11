# PLAN DE TEST — Microservice Triangulator

## Objectif
Ce document présente le plan de tests pour le micro-service Triangulator.  
L'objectif est de garantir la fiabilité, la justesse, la performance et la qualité de l'implémentation.

---

## Stratégie
- Écrire les tests avant l'implémentation (approche Test First)  
- Viser 100 % de couverture du code  
- Privilégier la qualité et la clarté des tests  
- Réaliser différents types de tests :  
  - tests unitaires (fonctions internes)  
  - tests d’intégration (API et interactions)  
  - tests de performance (rapidité et charge)

On utilise l'algorithme de Triangulation de Delaunay :  
Nombre de triangles = 2n - 2 - h  \où n = nombre total de points, h = nombre de points sur l'enveloppe convexe.

Exemples :  
- 5 points tous sur l'enveloppe convexe → 3 triangles  
- 4 points sur l'enveloppe convexe + 1 à l'intérieur → 4 triangles  
- 3 points sur l'enveloppe convexe + 2 à l'intérieur → 5 triangles

---

## Tests unitaires
### 1. Gestion des erreurs et cas impossibles
Cas testé : 0 point → Résultat attendu : Erreur  
**Raison de réalisation** : Assurer que la triangulation ne peut pas se faire sans points.

Cas testé : 1 point → Résultat attendu : Erreur  
**Raison de réalisation** : Vérifier le comportement pour un nombre de points insuffisant.

Cas testé : 2 points → Résultat attendu : Erreur  
**Raison de réalisation** : Garantir la gestion correcte d’un cas de points insuffisants.

### 2. Cas de triangulation normale
Cas testé : 3 points non alignés → Résultat attendu : 1 triangle  
**Raison de réalisation** : Confirmer que le service triangule correctement le cas minimal.

Cas testé : Triangulation avec 10 ou 15 points → Résultat attendu : Plusieurs triangles créés  
**Raison de réalisation** : Valider que la triangulation fonctionne sur des ensembles standards de points.

### 3. Cas dégénérés ou particuliers
Cas testé : Points alignés (colinéaires) → Résultat attendu : 0 triangle  
**Raison de réalisation** : Tester la gestion de points qui ne permettent pas de former de triangles.

Cas testé : Points dupliqués → Résultat attendu : Ignorer ou erreur  
**Raison de réalisation** : Vérifier que les doublons n’affectent pas la triangulation.

### 4. Conversion binaire / sérialisation
Cas testé : Conversion binaire → points → Résultat attendu : Points identiques après encodage/décodage  
**Raison de réalisation** : Confirmer la cohérence des données lors de la sérialisation/desérialisation.

Cas testé : Conversion binaire → triangles → Résultat attendu : Triangles identiques après conversion  
**Raison de réalisation** : Assurer la fiabilité des conversions pour les triangles.

Cas testé : Données binaires invalides → Résultat attendu : Erreur ou exception  
**Raison de réalisation** : Tester la résistance du service face à des données corrompues.

### 5. Robustesse numérique
Cas testé : Valeurs extrêmes (très grandes ou très petites) → Résultat attendu : Pas de crash  
**Raison de réalisation** : S’assurer que le service gère correctement les valeurs extrêmes.

---

## Tests d’intégration
### 1. Réponse API correcte
Cas testé : API /triangulate avec ID valide → Résultat attendu : 200 + Triangles valides  
**Raison de réalisation** : Vérifier que l’API retourne correctement les triangles pour un jeu de points valide.

Cas testé : API /healthz → Résultat attendu : 200 + “ok”  
**Raison de réalisation** : Confirmer que le service est opérationnel.

### 2. Gestion d’erreur API
- Cas testé : API `/triangulate` avec ID valide → Résultat attendu : `200 OK`  
  **Raison de réalisation** : Vérifier la réponse correcte en cas de succès.

- Cas testé : API `/triangulate` avec UUID malformé → Résultat attendu : `400 Bad Request`  
  **Raison de réalisation** : Garantir la robustesse contre les formats invalides.

- Cas testé : API `/triangulate` avec ID inexistant → Résultat attendu : `404 Not Found`  
  **Raison de réalisation** : Vérifier la gestion quand le `PointSetID` n'existe pas.

- Cas testé : API `/triangulate` provoquant une erreur interne → Résultat attendu : `500 Internal Server Error`  
  **Raison de réalisation** : Vérifier le format d'erreur en cas de bug/exception côté serveur.

- Cas testé : Service indisponible / surcharge → Résultat attendu : `503 Service Unavailable`  
  **Raison de réalisation** : Confirmer le comportement et le format d'erreur lorsque le service est indisponible.

### 3. Stabilité et charge
Cas testé : Plusieurs requêtes simultanées → Résultat attendu : Pas d’erreur ni de blocage  
**Raison de réalisation** : Tester la capacité de l’API à gérer la concurrence et plusieurs requêtes en parallèle.

---

## Tests de performance
Cas testé : Triangulation de 10 points → Résultat attendu : < 0.5 s  
**Raison de réalisation** : Vérifier la rapidité et que l’algorithme est performant sur de petits ensembles.

Cas testé : Triangulation de 100 points → Résultat attendu : < 1 s  
**Raison de réalisation** : Confirmer que le service reste rapide sur un nombre moyen de points.

Cas testé : Triangulation de 1000 points → Résultat attendu : < 3 s  
**Raison de réalisation** : Tester la scalabilité et la performance sur un nombre important de points.

Cas testé : Triangulation de 10 000 points → Résultat attendu : < 10 s  
**Raison de réalisation** : Vérifier le comportement sous forte charge et grands volumes.

Cas testé : Conversion binaire (10 000 points) → Résultat attendu : < 2 s  
**Raison de réalisation** : Assurer que la conversion binaire reste efficace même pour de grandes quantités de données.

---

## Risques et limitations
- Algorithme complexe si les points sont proches ou sur l’enveloppe convexe  
- Coordonnées extrêmes peuvent créer des erreurs numériques  
- Éviter les valeurs non valides (NaN, inf, etc.)  
- Tests de performance dépendants de la machine utilisée


