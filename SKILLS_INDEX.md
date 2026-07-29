# Index semantique des skills Blender du projet

Six skills, dans `.claude/skills/`. Elles se declenchent sur l'intention, pas sur
un nom a retenir. Cette page est la table de correspondance entre ce que je suis
en train de penser et la skill a ouvrir.

## Table de declenchement

| Ce que je pense ou constate | Skill |
|---|---|
| « je vais toucher a Blender » | blender-session |
| « le port 9876 ne repond pas », « connection refused » | blender-session |
| « je veux repartir d'une scene propre » | blender-session |
| « il faut sauvegarder » | blender-session |
| « je dois creer cette forme » | blender-modelisation |
| « la courbure est fausse », « la proportion ne va pas » | blender-modelisation |
| « cet element est symetrique » | blender-modelisation |
| « il y a un trou, une echancrure, un evidement » | blender-modelisation |
| « cette arete doit etre vive / adoucie » | blender-modelisation |
| « c'est une coque, il faut une epaisseur » | blender-modelisation |
| « quelle couleur, quelle matiere » | blender-materiaux |
| « c'est brillant / mat / satine / brosse » | blender-materiaux |
| « c'est transparent, translucide » | blender-materiaux |
| « il y a une inscription, un logo, une gravure » | blender-materiaux |
| « il y a des rayures, de l'usure » | blender-materiaux |
| « le rendu est trop sombre / crame / plat » | blender-eclairage |
| « les reflets ne ressemblent pas a la photo » | blender-eclairage |
| « je veux juger la forme sans etre gene par la matiere » | blender-eclairage (passe argile) |
| « EEVEE ou Cycles ? » | blender-eclairage |
| « je veux voir ou montrer l'etat du modele » | blender-vues |
| « il me faut des vues pour comparer aux photos » | blender-vues |
| « je prepare l'auto-critique » | blender-vues |
| « reproduire l'angle de cette photo » | blender-vues |
| « l'utilisateur veut un fichier » | blender-export |
| « impression 3D » | blender-export |
| « voir le modele hors de Blender » | blender-export |

## Correspondance avec le pipeline

| Etape | Skills |
|---|---|
| P0 initialisation | blender-session |
| P12 implementation | blender-session, blender-modelisation, blender-materiaux |
| P13 verification | blender-eclairage, blender-vues |
| P14 auto-critique | blender-vues |
| P15 iterations | blender-modelisation, blender-materiaux, blender-vues |
| P17 livraison | blender-export, blender-eclairage |

## Enchainements types

- **Nouvel element** : session, modelisation, materiaux, vues.
- **Boucle d'iteration** : modelisation ou materiaux selon la critique, puis
  vues avec le meme prefixe d'iteration et les memes angles que la fois
  precedente.
- **Livraison** : vues en regime restitution, export, documentation.

## Origine

Base de depart : https://github.com/kevinbadi/blender-skills — bibliotheque
orientee prise de vue produit et animation marketing. Rien n'a ete repris tel
quel : les skills du projet sont des generalisations reecrites pour la
reconstruction fidele.

Retenu et generalise :

| Source | Devenu | Transformation |
|---|---|---|
| polyhaven-studio-setup | blender-eclairage | ajout d'un regime de controle neutre, d'une passe argile et des reglages moteur ; HDRI relegue a la livraison |
| polyhaven-texture-apply | blender-materiaux | integre a un bareme de traduction des descripteurs verbaux en valeurs PBR |
| threejs-export | blender-export | elargi aux formats STL, OBJ, FBX, avec verification de fermeture du volume |
| turntable, crane-shot, dolly-rotate, slow-zoom, perfect-loop, dynamic-full-loop | blender-vues | seule la geometrie d'orbite est conservee, convertie en vues anatomiques normalisees ; l'animation est abandonnee |
| blender-toolkit | blender-session, blender-modelisation | concepts seulement, le code est inutilisable ici (autre addon, autre port, client TypeScript externe) |

Ecarte :

| Source | Motif |
|---|---|
| image-to-3d, multi-image-to-3d | reconstruction automatique par API Meshy, payante, et contraire a la methode du projet, qui est une reconstruction raisonnee et editable |
| product-polish | esthetique marketing brillante qui flatte l'objet et masque les ecarts de forme |
| polyhaven-hdri-showcase, polyhaven-material-swap, polyhaven-scene-builder | variantes de presentation commerciale, sans emploi ici |

Briques executables ecrites pour le projet, toutes testees sur cette machine :

| Script | Role |
|---|---|
| `blender/scripts/mcp.py` | client socket, secours et diagnostic |
| `blender/scripts/eclairage_controle.py` | eclairage neutre calibre sur la taille de l'objet |
| `blender/scripts/vues_controle.py` | vues anatomiques cadrees automatiquement |
| `blender/scripts/blender_start.sh` et `blender_stop.sh` | cycle de vie de Blender |
