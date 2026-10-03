# Déclarer et examiner plusieurs versions d’un même fait

Le rapport de cohérence est un contrôle séparé du livre. Il compare des objets **Événement** distincts uniquement quand vous leur attribuez volontairement le même `BOOK_FACT_ID`. Il ne rapproche pas automatiquement deux événements semblables et ne supprime aucune version du livre.

1. Dans Gramps, ouvrez le premier objet Événement à examiner. Dans son onglet **Attributs**, ajoutez un attribut de type personnalisé `BOOK_FACT_ID` avec une valeur de votre choix, par exemple `naissance-personne-42`. Enregistrez l’événement.
2. Ouvrez le second objet Événement qui décrit ce même fait. Ajoutez le même type d’attribut avec **exactement la même valeur**, puis enregistrez. L’attribut appartient aux objets Événement, pas à leurs références dans une fiche de personne ou de famille.
3. Lancez **Gramps Fancy Genealogical Book** depuis **Rapports → Pages Web**. Choisissez la famille de référence, confirmez l’option de confidentialité, sélectionnez **Instantané JSON et rapport de cohérence**, puis une destination comme `famille.json` dans un dossier existant.
4. Ouvrez le fichier voisin `famille_consistency.json`. La section `groups` liste les événements comparés ; `findings` contient les conclusions. Une liste `findings` vide signifie qu’aucune divergence prévue par ce contrôle n’a été détectée parmi les groupes comparés.

Dans `findings`, `disjoint_event_date_ranges` avec `confirmed_conflict` indique deux plages de dates Gramps sans chevauchement. `different_event_place_references` avec `review_required` signale des références de lieux différentes : cela demande une vérification humaine et ne prouve pas que les lieux sont incompatibles. Les dates absentes, textuelles ou non comparables restent visibles dans `groups`, sans conclusion de conflit de dates.

La valeur de `BOOK_FACT_ID` est sensible à la casse ; les espaces au début et à la fin sont ignorés. Employez une valeur unique pour chaque fait à l’échelle de la base. Si un événement porte plusieurs valeurs distinctes, il est exclu des comparaisons et figure dans `diagnostics`. Le rapport peut contenir des données privées et des identifiants internes : appliquez les mêmes précautions de partage que pour l’instantané JSON.

Le parcours de saisie dans l’interface est décrit d’après les composants de Gramps 6.0.8 ; sa recette manuelle reste ouverte. Voir les [décisions 005](decisions/005-event-fact-identity.md) et [006](decisions/006-consistency-report.md) pour le contrat exact.
