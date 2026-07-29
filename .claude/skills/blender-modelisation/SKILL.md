---
name: blender-modelisation
description: Construire et modifier la geometrie d'un objet dans Blender - primitives, profil revolu, extrusion le long d'un trace, epaisseur de paroi, congés, symetrie sagittale, decoupe booleenne, lissage. TRIGGER quand je dois creer une forme, ajouter un element, corriger une courbure, une proportion, un rayon de conge, une epaisseur, une arete, ou dupliquer par symetrie. Coeur de l'etape P12 et des iterations P15.
---

# Modelisation

Prerequis : `blender-session` verifiee.

## Choix de la methode de construction

Le descripteur de forme de la description anatomique dicte la methode.

| Descripteur anatomique | Construction |
|---|---|
| cylindrique, tronconique, discoide, ovoide de revolution | profil 2D revolu (modificateur SCREW) |
| prismatique, en gouttiere, section constante | profil 2D extrude le long d'un axe ou d'une courbe |
| fusiforme, lenticulaire, renflement progressif | primitive + mise a l'echelle progressive, ou lattice |
| symetrique bilateral | demi-objet + modificateur MIRROR sur le plan sagittal |
| radial d'ordre n | secteur + modificateur ARRAY en rotation |
| echancre, foramen, incisure | soustraction booleenne |
| eminence, tubercule, crete | ajout booleen ou extrusion locale |
| paroi mince, coque | modificateur SOLIDIFY |
| arete adoucie, rayon de conge | modificateur BEVEL |

Regle : **preferer les modificateurs a la geometrie figee**. Un modificateur reste
reglable a l'iteration suivante ; une geometrie appliquee doit etre refaite.
N'appliquer (`object.modifier_apply`) que si une operation ulterieure l'exige.

## Convention d'orientation

Rappel, non negociable (voir CLAUDE.md §3) :

| Axe anatomique | Axe Blender |
|---|---|
| medio-lateral | X, positif vers la droite de l'objet |
| ventro-dorsal | Y, positif vers le dorsal |
| craniocaudal | Z, positif vers le cranial |

Plan sagittal median = X = 0. Toute piece paire se construit du cote X positif
puis se reflete.

## Patrons

### Symetrie sagittale

```python
import bpy
ob = bpy.data.objects["mon_element"]
m = ob.modifiers.new("sagittal", 'MIRROR')
m.use_axis = (True, False, False)   # miroir sur X
m.use_clip = True                    # empeche les sommets de traverser le plan
m.merge_threshold = 0.0005
```

### Profil revolu

Construire le profil dans le plan XZ (rayon en X, hauteur en Z), puis :

```python
m = ob.modifiers.new("revolution", 'SCREW')
m.axis = 'Z'
m.angle = 6.283185307      # 2 pi
m.steps = 64
m.use_merge_vertices = True
m.merge_threshold = 1e-5   # le defaut vaut 0.01 m, soit 10 mm
```

Deux pieges, tous deux silencieux, tous deux constates :

- le profil doit etre une **chaine d'aretes ouverte**. Ferme, la revolution ne
  produit aucune face ;
- le **seuil de fusion par defaut vaut 10 mm**. Sur un objet de poche il fusionne
  des pieces entieres. Toujours le baisser.

Verifier apres coup le nombre de faces de l'objet evalue :

```python
d = bpy.context.evaluated_depsgraph_get()
ev = ob.evaluated_get(d)
me = ev.to_mesh()
print(ob.name, "faces:", len(me.polygons))
ev.to_mesh_clear()
```

Un modificateur qui ne produit rien ne leve aucune erreur.

### Paroi et congés

```python
s = ob.modifiers.new("paroi", 'SOLIDIFY')
s.thickness = 0.002        # metres, soit 2 mm
s.offset = -1              # matiere vers l'interieur

b = ob.modifiers.new("conges", 'BEVEL')
b.width = 0.0015
b.segments = 3
b.limit_method = 'ANGLE'
b.angle_limit = 0.5236     # 30 degres
```

### Decoupe booleenne

```python
mod = cible.modifiers.new("echancrure", 'BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = outil
mod.solver = 'EXACT'
outil.display_type = 'WIRE'      # l'outil reste visible mais ne se rend pas
outil.hide_render = True
```

L'outil booleen doit rester dans la scene tant que le modificateur n'est pas
applique. Le nommer `outil_<cible>_<fonction>` et le ranger dans une collection
`outils`.

### Lissage

```python
for f in ob.data.polygons:
    f.use_smooth = True
ob.data.use_auto_smooth = True     # Blender 3.x
ob.data.auto_smooth_angle = 0.5236 # arete vive au-dela de 30 degres
```

Une arete decrite comme vive doit le rester : le lissage global est un piege
frequent qui arrondit tout et fait perdre la fidelite.

### Pieces rapportees affleurantes

Une piece posee exactement au niveau de la surface qui la porte entre en
concurrence d'affichage avec elle et disparait par intermittence. La decaler de
quelques centiemes de millimetre vers l'exterieur suffit, et reste invisible.

## Discipline de construction

1. **Un element = un script = un objet nomme.** Le nom vient de la description
   anatomique, pas de Blender : `corps`, `col`, `bord_libre`, `apophyse_dorsale`.
2. **Script relancable.** Commencer par supprimer l'objet homonyme :

   ```python
   old = bpy.data.objects.get(NOM)
   if old:
       bpy.data.objects.remove(old, do_unlink=True)
   ```

3. **Mesurer, ne pas supposer.** Terminer chaque script par un print des
   dimensions reelles :

   ```python
   print(NOM, "dimensions m:", tuple(round(v, 4) for v in ob.dimensions))
   ```

   Puis confronter a `descriptions/DIMENSIONS.md`.
4. **Collections.** Une collection par sous-ensemble anatomique, plus une
   collection `outils` pour les objets de construction non rendus.
5. **Sauvegarder** apres chaque element valide.

## Densite de maillage

Suffisante pour tenir la courbure decrite, pas davantage. Un objet lisse et
convexe n'a pas besoin de subdivision fine si un lissage par angle suffit. Une
densite excessive rend les corrections d'iteration penibles.

Si une subdivision est necessaire, la poser en modificateur `SUBSURF` avec
`levels = 2`, `render_levels = 3`, et laisser la cage grossiere editable.

## Rapport a l'utilisateur

Ne jamais parler de sommets, modificateurs, booleens, subdivision. Rendre compte
en termes de forme : « la face ventrale est desormais convexe sur toute sa
hauteur, le bord lateral est adouci sur environ 1,5 mm ».
