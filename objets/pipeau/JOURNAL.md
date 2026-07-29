# Journal technique — Pipeau

## 2026-07-29 — P1 a P12

**Ingestion.** Sept photos, 684x912, deja sous 1200 px. Renommees p01 a p07 dans
l'ordre chronologique, correspondance dans `photos/CORRESPONDANCE.txt`. Premiere
copie ratee : le motif de copie etait `IMG_2026*_0049*`, il excluait la photo de
00:48:53.

**Orientation.** Cranial = embout, ventral = face a panneau noir. Les faces
larges sont donc laterales. Attribution confirmee par deux mesures independantes
sur photo, rapportees au diametre du reservoir, avant que l'utilisateur ne
confirme par ses cotes.

**Cotes.** Toutes fournies par l'utilisateur a la regle. Piege : elles portent sur
l'objet fini, renflement de la piece creme et saillie des boutons compris. La
premiere passe les avait appliquees au corps nu, d'ou une boite englobante de
30 x 57.5 mm au lieu de 27 x 55. Corps nu ramene a 24 x 51.5 mm.

**Section.** Definie une fois dans `_geom.py`, partagee par tous les scripts
d'element. Face ventrale plane de 21 mm, deux biseaux plans de 10 mm, flancs
plans, moitie dorsale en superellipse d'exposant 3.

**Nappes.** Machinerie commune : une surface epousant le flanc, restreinte a une
region decrite en coordonnees curvilignes (su, z), puis epaissie par SOLIDIFY.
Elle sert a l'armature, au logement du skai et aux surpiqures. Une seule region a
ecrire par element, la symetrie bilaterale est automatique.

**Ce qui a resiste**

1. Nappes vides ou tronquees. La section n'avait que deux points sur chaque flanc
   plan, soit un segment de 25 mm : aucune limite de region ne pouvait y tomber.
   Corrige par un reechantillonnage a pas curviligne constant de 0.4 mm.
2. Vues craniale et caudale a l'envers. `to_track_quat` est degenere quand l'axe
   de visee est l'axe de reference : l'orientation de l'image y est desormais
   fixee explicitement, dorsal vers le haut dans les deux cas.
3. Reservoir plaque contre la face ventrale. Son axe de revolution etait a
   l'origine du monde, qui est au ras de la face ventrale et non au milieu de la
   section. Deplace a Y = 25.75 mm.
4. Boutons saillants de 3 mm au lieu de 2. Le pave etait centre a mi-saillie au
   lieu d'etre centre sur la face ventrale.

**Verifie**

Boite englobante finale 27 x 55 x 140 mm, conforme aux trois cotes de reference.

## 2026-07-29 — Reprise du reservoir et premiere passe de matieres

**Releve photogrammetrique du reservoir.** Silhouette mesuree ligne par ligne sur
la planche p01, apres seuillage. Echelle etablie par deux calibrations
independantes concordantes a 1 pour cent : largeur de la face laterale du corps
(55 mm) et diametre de l'embout (15 mm).

Trois corrections en decoulent :

1. Le point le plus large de l'ensemble n'est pas le verre mais la **bague de
   base**, a 30 mm de diametre. Le reservoir deborde donc du corps en
   medio-lateral, ce que confirme la planche p04. La valeur de 26 mm retenue en
   P7 venait de ma propre liste d'options : anchoring, a ne pas reproduire.
2. La **lumiere d'entree d'air est craniale**, dans la gorge du chapeau, et non
   caudale. Nettement lisible sur p04.
3. Le **verre est renfle en tonneau**, rayon passant de 13.0 a 14.3 mm.

**Matieres.** Neuf materiaux, quatorze objets habilles. Grain du skai et
facettage en nid d'abeille de l'embout traites en relief de surface, sans
geometrie.

**Ce qui a resiste**

1. Embout invisible, zero face, sans aucune erreur. Deux causes cumulees : le
   profil etait ferme, et surtout le seuil de fusion de SCREW vaut 0.01 m par
   defaut, soit 10 mm, ce qui fusionnait toute une piece de 3.6 mm de rayon.
2. Panneau ventral invisible : sa face etait strictement coplanaire avec la face
   ventrale du corps. Decale de 0.03 mm.

**Reste a faire**

- facettage en nid d'abeille de l'embout
- visserie, quatre vis par flanc
- gravure GEEKVAPE sur l'armature
- marquage en trois traits sur le revetement dorsal
- couleurs et matieres, dont la transparence du cylindre
- artefacts d'usure
