---
name: blender-vues
description: Produire les images de controle du modele - vues anatomiques normalisees ventrale dorsale laterale craniale caudale, vue reproduisant l'angle d'une photo, orbite multi-angles, capture du viewport. TRIGGER a l'etape P13 verification, a l'etape P14 auto-critique avant d'appeler le subagent critique, et chaque fois que je veux voir ou montrer l'etat du modele.
---

# Vues de controle

Prerequis : `blender-session` verifiee, `blender-eclairage` posee au moins une fois.

## Vues normalisees

```bash
python3 blender/scripts/mcp.py exec blender/scripts/vues_controle.py
```

Sortie dans `blender/renders/controle_vue_<direction>.png`, carre 1200 px,
camera orthographique cadree automatiquement sur la boite englobante des objets
rendus. La collection `outils` est exclue.

Parametres en tete de `blender/scripts/vues_controle.py` : `VUES`, `PREFIXE`,
`RESOLUTION`, `ORTHOGRAPHIQUE`, `MARGE`. Editer le fichier puis relancer.

Nommer le prefixe par iteration : `PREFIXE = "iter03"`. Les rendus des iterations
precedentes se conservent, la progression devient lisible.

## Choix des vues

- **Verification de forme et de proportions** : orthographique, toujours. La
  perspective fausse les rapports de longueur et rend la comparaison a la
  description anatomique impossible.
- **Comparaison a une photo** : perspective, focale approchant celle de la photo,
  angle reproduisant la prise de vue. C'est la seule facon de trancher un
  desaccord entre le modele et une photo.

Focale a retenir a defaut d'information : 50 mm pour une photo d'objet a distance
moyenne, 26 a 28 mm pour une photo de telephone tenu pres de l'objet. Une photo
de telephone en gros plan deforme fortement : la face la plus proche parait
surdimensionnee. Ne jamais corriger la geometrie du modele pour epouser cette
deformation — c'est le point 13 de la checklist.

## Reproduire l'angle d'une photo

En orbite, deux angles suffisent a decrire une prise de vue :

- **azimut** : rotation autour de l'axe craniocaudal, 0 degre en face ventrale,
  positif vers le lateral droit ;
- **elevation** : hauteur au-dessus du plan horizontal, positive en vue plongeante.

```python
import math, mathutils, bpy
azimut, elevation, recul = math.radians(35), math.radians(20), 0.9
axe = mathutils.Vector((
    math.sin(azimut) * math.cos(elevation),
   -math.cos(azimut) * math.cos(elevation),
    math.sin(elevation),
))
cam = bpy.data.objects["camera_controle"]
cam.data.type = 'PERSP'
cam.data.lens = 50.0
cam.location = centre + axe * recul
cam.rotation_mode = 'QUATERNION'
cam.rotation_quaternion = axe.to_track_quat('Z', 'Y')
```

Consigner azimut, elevation et focale retenus pour chaque photo dans la planche
correspondante : ils doivent etre rejoues a l'identique a chaque iteration, sinon
les comparaisons ne sont plus comparables.

## Capture rapide du viewport

Beaucoup plus rapide qu'un rendu, sans eclairage fidele. Bon pour verifier qu'un
element est bien la et bien place, jamais pour juger une forme ou une matiere.

```bash
python3 blender/scripts/mcp.py shot /home/m/projet/blender/blender/renders/apercu.png 1200
```

## Passe argile

Pour juger la forme seule, sans matiere : voir `blender-eclairage`, section
argile. A produire systematiquement pour P14 en plus des vues matierees — la
critique sur la forme et la critique sur l'aspect ne se font pas sur la meme
image.

## Preparer l'auto-critique P14

Livrer au subagent critique :

1. deux a quatre rendus dont les angles approchent ceux des photos ;
2. les photos correspondantes de `photos/work/` ;
3. la description anatomique en vigueur ;
4. la consigne que **la photo est la source de verite**.

Un rendu dont l'angle ne correspond a aucune photo ne sert a rien pour la
critique : le critique compare, il ne devine pas.

## Verifier avant de conclure

Toujours ouvrir le fichier rendu avant d'affirmer qu'il est bon. Un rendu noir,
vide, ou cadre a cote se produit sans lever d'erreur.
