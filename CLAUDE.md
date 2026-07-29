# CLAUDE.md — Scanner 3D par référence photographique (Blender)

## 0. Nature du projet

Chaîne de production permettant de reconstruire un objet réel en modèle 3D Blender
à partir d'un lot de photographies, en passant obligatoirement par une **étape de
description anatomique textuelle** servant de contrat de spécification entre
l'utilisateur et Claude.

**Nom d'usage** : « scanner 3D par photogrammétrie ».
**Méthode réelle** : modélisation 3D assistée par référence photographique
multi-vues, avec spécification anatomique intermédiaire. Ce n'est pas de la
photogrammétrie par triangulation automatique — c'est de la reconstruction
raisonnée, donc contrôlable et éditable.

**Contrainte cadre** : l'utilisateur ne connaît pas Blender et ne pourra pas
assister Claude techniquement. Claude opère en autonomie sur Blender. L'utilisateur
est en revanche **expert en description anatomique** — c'est le langage commun
imposé.

---

## 1. Communication avec l'utilisateur

### 1.1 Langage imposé : description anatomique

Toute communication sur la géométrie, l'orientation, la position ou la structure
d'un objet **doit** utiliser la terminologie anatomique standard.

**Autorisé et attendu :**

| Catégorie | Termes |
|---|---|
| Axes | craniocaudal (ou rostro-caudal), ventro-dorsal, médio-latéral, proximo-distal |
| Plans | sagittal , frontal (= coronal), horizontal |
| Directions | ventral, dorsal, cranial, caudal, médial, latéral, proximal, distal, superficiel, profond |
| Rapports | jouxte, surplombe, s'insère sur, s'articule avec, est contigu à, converge vers, s'évase, se rétrécit |
| Descripteurs de forme | convexe, concave, plan, cylindrique, tronconique, fusiforme, discoïde, lenticulaire, ovoïde, prismatique, en gouttière, échancré, festonné, crénelé, depression, eminence |
| Relief | crête, sillon, fosse, foramen, tubercule, épine, apophyse, incisure, bord, face, angle, sommet, base |
| Symétrie | symétrique bilatéral, asymétrique, radial d'ordre n |

**Interdit :**
- téguments, phanères (poils, ongles, écailles, plumes)
- toute analogie histologique ou tissulaire
- vocabulaire 3D/technique dans les échanges avec l'utilisateur (vertex, edge loop,
  normale, UV, subdiv, bevel…) — réservé au journal technique interne, mais peut etre distilé à petite dose de manière claire et pédagogique pour faire monter très doucement l'user en compétence

### 1.2 Registre

- **Terse.** Pas de préambule, pas de reformulation de la question, pas de
  « Excellente question ». On entre dans le sujet.
- **NO sycophancy** Le user doit etre respecté, le flatter sans cesse le mettrait mal à l'aise.
- **Dense.** Ne jamais sacrifier de l'information pour raccourcir. Sacrifier les
  mots de liaison, pas les faits.
- **Jargon projet** Rester au standard. Attention à ne pas emmener l'user dans un engrenage de concepts trop projet. les phrases doivent etre comprises par quelqu'un qui reprend le projet sans qu'il ait besoin de relire tout le fil.
- **Non ambigu.** Une question = une chose à trancher. Jamais deux inconnues dans
  la même phrase ou un askuser.
- **Orienté.** Toujours proposer une interprétation par défaut, classée du plus
  probable au moins probable, avec une option ouverte terminale.

### 1.3 Format des questions (AskUserQuestion)

Structure obligatoire de chaque question :
[Zone anatomique concernée] — [propriété en cause] - orientation
Options, du plus probable au moins probable :
  A) … (défaut retenu si silence)
  B) …
  C) …
  D) Autre — précise

- Si plusieurs propriétés indépendantes → plusieurs questions, jamais fusionnées.
- Si l'utilisateur doit décrire quelque chose que Claude ne peut pas anticiper →
  question ouverte assumée, sans QCM factice.
- **En cas de doute réel, poser la question.** Ne jamais combler un flou par une
  invention silencieuse.
- Grouper les questions par lots thématiques cohérents (ex. « géométrie du corps »,
  puis « matières et couleurs », puis « artefacts »).

### 1.4 Champs d'interrogation à couvrir systématiquement

Checklist à balayer avant de considérer une spécification complète :

1. **Identification** — nature de l'objet, fonction, nom vernaculaire
2. **Orientation** — face ventrale, axe craniocaudal (voir §3)
3. **Géométrie globale** — proportions, symétries, nombre de sous-ensembles
4. **Géométrie locale** — courbures, rayons de congé, arêtes vives vs adoucies,
   épaisseurs
5. **Zones occultées** — tout ce qu'aucune photo ne montre
6. **Éléments distincts** — pièces séparées, mobiles, démontables, articulées
7. **Couleurs** — par zone, avec dégradés / limites nettes ou floues
8. **Matières** — métal, plastique, bois, verre, textile, céramique, composite
9. **Textures / finition** — lisse, satiné, mat, brossé, granuleux, moleté, tissé
10. **Transparence / translucidité / réflectivité**
11. **Inscriptions, marquages, gravures, logos, sérigraphies**
12. **Artefacts** — usure, rayures, éclats, déformations, réparations, salissures
13. **Écarts photo/réalité** — reflets parasites, ombres, distorsion optique,
    déformations dues à l'angle
14. **Dimensions** — voir §7
15. **État de l'objet** — l'objet photographié est-il dans sa configuration
    nominale ou dans un état particulier (plié, ouvert, incomplet) ?
16 **Attention au reset de scene** connu pour déconnecter le mcp

---

## 2. Pipeline complet

P0  Initialisation projet    → dossier, structure, journal, aide la mide en place du serveur mcp de blender, bibliothèque de skills Blender + index sémantique (voir §9)
P1  Ingestion photos          → resize 1200px max, ratio conservé
P2  Identification            → lecture 1 photo → confirmation objet
P3  Planches photo            → 1 description anatomique / photo
P4  Corrélation               → mise en rapport, choix face ventrale + axe vertical
P5  Description anatomique v1 → représentation textuelle poussée de l'objet
P6  Registre d'incertitudes   → liste des flous, classés
P7  Interrogation             → AskUserQuestion, par lots
P8  Révision planches         → mise à jour des descriptions photo
P9  Description anatomique v2 → mise à jour + VALIDATION utilisateur (bloquant)
P10 Étalonnage dimensionnel   → voir §7
P11 Plan de découpage         → arborescence des éléments distincts
P12 Implémentation Blender    → construction élément par élément
P13 Vérification              → rendus de contrôle vs photos, proposition d'itération
P14 Auto-critique             → capturer dans blender 2 à 4 vue approchant les photos grace a l'orientation disponible dans la description anatomique, lancement d'un subagent critique qui va te faire des remontées en comparant avec les photos(source de vérité) et te poser des questions et te formuler ses critiques sur differentes dimension de réalisme.
P15 Itérations                 → theorisation des retours de l'agent, validation ou invalidation en askuser/qcm+open par l'utilisateur, prise d'information d'un retour libre de l'utilisateur, retour à P8 (sauter p10, eventuelle revision P11 mais rare)
P16 Arret ou shunt de l'itération   → l'utilisateur peut te demander de petites retouches sans forcément passer par la boucle d'iteration si tu sens que c'est du détail et qu'il te dit qu'il va faire ça a l'oeil.
P17 Livraison                 → proposer export, documentation de l'objet, rangement nettoyage artefact des descriptions et des photos et du dossier de travail en général,
P18 Capitalisation des lessons learned (blender, interaction user, strategie et toute autre dimension utile) sur claude.md ou un fichiers independant si claude trop gros

---

## 3. Convention d'orientation

Référentiel fixé une fois pour toutes en P4, puis jamais renégocié sans le dire.

| Axe anatomique | Axe Blender | Sens positif |
|---|---|---|
| ventro-dorsal | Y | dorsal (Y+ = vers l'arrière de l'objet) |
| médio-latéral | X | latéral droit de l'objet |
| craniocaudal | Z | cranial (Z+ = vers le haut) |

Plan sagittal médian = plan X=0. Origine du monde = point le plus caudal du plan
sagittal médian, sauf spécification contraire consignée en P4.

Toute vue de rendu est nommée par sa direction anatomique d'observation :
`vue_ventrale`, `vue_dorsale`, `vue_laterale_droite`, `vue_laterale_gauche`,
`vue_craniale`, `vue_caudale`.

---

## 4. Arborescence de travail

Un objet reconstruit = un sous-projet sous `objets/`. L'outillage et la méthode
sont partagés à la racine.

```
CLAUDE.md               méthode (ce fichier)
SETUP.md                installation de la chaîne Blender
SKILLS_INDEX.md         index des skills
LESSONS.md              capitalisation P18
blender/scripts/        outillage partagé : mcp.py, eclairage_controle.py,
                        vues_controle.py, blender_start.sh, blender_stop.sh
objets/ACTIF            nom du sous-projet en cours, lu par l'outillage
objets/<nom>/           un sous-projet par objet
```

Structure d'un sous-projet :

```
photos/source/          originaux, jamais modifiés
photos/work/            versions 1200px max (P1), seules lues par Claude
photos/CORRESPONDANCE.txt  nom de travail vers nom d'origine
descriptions/planches/  P3 puis P8 — une planche par photo
descriptions/anatomie/  P5 (v1), P9 (v2), versions ultérieures
descriptions/           INCERTITUDES.md (P6), DIMENSIONS.md (P10), DECOUPAGE.md (P11)
blender/scene.blend     fichier de travail
blender/scripts/        scripts de construction, un par élément si possible
blender/renders/        rendus de contrôle P13/P14
blender/exports/        sorties P17
livraison/              paquet final P17
JOURNAL.md              journal technique interne (vocabulaire 3D autorisé)
```

---

## 5. Journal technique

`JOURNAL.md` est le seul endroit où le vocabulaire 3D est libre. Une entrée par
étape de pipeline franchie, datée, avec : ce qui a été fait, ce qui a résisté,
ce qui a été décidé. Il n'est pas montré à l'utilisateur en l'état.

---

## 6. Serveur MCP Blender

Voir `SETUP.md`. Points de vigilance opérationnels :

- Le serveur socket vit dans Blender. Blender fermé = MCP mort.
- **Un reset de scène déconnecte le MCP.** Ne jamais appeler d'opérateur de
  réinitialisation de fichier depuis le MCP. Pour repartir d'une scène propre,
  supprimer les objets un par un.
- Travailler par petits scripts idempotents plutôt que par une longue passe unique :
  une erreur au milieu d'un gros script laisse la scène dans un état hybride.
- Sauvegarder le .blend après chaque élément terminé.

---

## 7. Étalonnage dimensionnel (P10)

Une seule cote réelle suffit à fixer l'échelle de tout le modèle, à condition
qu'elle porte sur un segment identifiable dans une photo et dans la description
anatomique.

Ordre de préférence de la cote de référence :
1. cote donnée par l'utilisateur au mm sur un segment rectiligne franc
2. objet-étalon présent dans la photo (pièce de monnaie, règle, main)
3. dimension normalisée déductible de la nature de l'objet
4. estimation assumée, consignée comme incertitude ouverte

Unité de scène : le mètre. 1 unité Blender = 1 m. Les cotes sont consignées en
millimètres dans `descriptions/DIMENSIONS.md`.

---

## 8. Bibliothèque de skills Blender

Six skills dans `.claude/skills/`, à déclencher sur l'intention. Table de
correspondance intention → skill dans `SKILLS_INDEX.md`, à consulter dès qu'une
opération Blender se présente.

| Skill | Domaine |
|---|---|
| `blender-session` | connexion, garde-fous, exécution de code, sauvegarde |
| `blender-modelisation` | géométrie : formes, symétrie, épaisseur, congés, découpes |
| `blender-materiaux` | couleurs, matières, finitions, transparence, inscriptions |
| `blender-eclairage` | éclairage de contrôle, passe argile, moteur de rendu |
| `blender-vues` | vues anatomiques normalisées, reproduction d'angle photo |
| `blender-export` | GLB, STL, OBJ, FBX, documentation de livraison |

`blender-session` est un prérequis de toutes les autres.

Base de départ : https://github.com/kevinbadi/blender-skills, entièrement
réécrite et généralisée. Sélection et motifs d'écart consignés dans
`SKILLS_INDEX.md`.

---

## 9. Registre d'incertitudes (P6)

Chaque incertitude porte : zone anatomique, propriété en cause, hypothèse par
défaut retenue, criticité.

Criticité :
- **bloquante** — empêche de construire, question obligatoire avant P12
- **structurante** — n'empêche pas de construire mais coûte cher à corriger après
- **cosmétique** — corrigeable tard, sans reprise de géométrie
