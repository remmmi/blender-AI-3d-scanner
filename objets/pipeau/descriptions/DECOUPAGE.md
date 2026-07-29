# Plan de découpage — Pipeau

Établi en P11. Un élément = un objet nommé = un script relançable.
Ordre de construction du plus structurant au plus cosmétique.

## Arborescence

```
pipeau
├── corps
│   ├── corps_volume          section constante extrudée, congés cranial et caudal
│   ├── panneau_ventral       creux noir enchâssé
│   ├── bouton_feu            saillie craniale
│   ├── bouton_reglage        saillie caudale
│   ├── armature              pièce crème renflée, chevron plus deux bandeaux
│   ├── skai_lateral          panneau en dépression, deux exemplaires symétriques
│   ├── skai_dorsal           revêtement dorsal et surpiqûres
│   ├── volet_caudal          volet crème rainuré
│   └── visserie              quatre vis par flanc, empreinte étoilée
├── reservoir
│   ├── embase
│   ├── bague_caudale         avec lumière d'entrée d'air
│   ├── cylindre_transparent
│   ├── bague_craniale
│   └── collerette
└── embout                    tronc de cône facetté nid d'abeille
```

## Ordre d'exécution

| Rang | Élément | Dépend de | Méthode |
|---|---|---|---|
| 1 | corps_volume | — | profil de section fermé, extrudé sur 90 mm, congés aux extrémités |
| 2 | panneau_ventral | 1 | découpe en dépression sur la face ventrale |
| 3 | bouton_feu, bouton_reglage | 2 | volumes rapportés en saillie |
| 4 | armature | 1 | pièce renflée épousant le flanc, symétrie sagittale |
| 5 | skai_lateral | 1, 4 | dépression dans le champ du chevron, symétrie sagittale |
| 6 | skai_dorsal | 1 | surface dorsale décalée, surpiqûres en relief |
| 7 | volet_caudal | 1 | dépression rainurée sur la face caudale |
| 8 | reservoir | — | profil revolu, cinq étages |
| 9 | embout | 8 | tronc de cône, facettage par motif hexagonal |
| 10 | visserie | 4 | huit exemplaires, positions déduites des écarts 46,5 et 74,5 mm |

## Règles

- Toute pièce paire se construit du côté X positif puis se reflète par symétrie
  sagittale. Aucune duplication manuelle.
- Les pièces d'assemblage masquées en configuration nominale ne sont pas
  modélisées : filetage corps vers réservoir, intérieur du réservoir.
- Les artefacts d'usure sont traités en finition de surface, pas en géométrie,
  et seulement après validation de la forme.
