---
name: blender-eclairage
description: Eclairer la scene Blender pour un rendu de controle fidele - eclairage neutre trois points, fond uni, ou environnement HDRI PolyHaven, et reglages du moteur de rendu EEVEE ou Cycles. TRIGGER avant tout rendu de controle ou de livraison, quand un rendu sort trop sombre, crame, plat, ou quand les reflets ne correspondent pas aux photos.
---

# Eclairage et moteur de rendu

Prerequis : `blender-session` verifiee.

## Deux regimes, ne pas les confondre

| Regime | But | Eclairage |
|---|---|---|
| **controle** (P13, P14) | comparer la forme aux photos | neutre, sans ombre dure, fond uni |
| **restitution** (P17) | rendre l'objet credible | environnement HDRI, reflets riches |

Le regime de controle prime pendant toute la boucle d'iteration. Un eclairage
flatteur masque les defauts de forme — c'est exactement ce qu'il ne faut pas.

## Eclairage neutre de controle

```bash
python3 blender/scripts/mcp.py exec blender/scripts/eclairage_controle.py
```

Pose trois sources larges a faible contraste plus un fond gris emissif, et regle
le moteur. Tout est dimensionne sur la boite englobante des objets rendus : le
script fonctionne aussi bien sur un objet de 40 mm que de 2 m, sans reglage.

A relancer apres tout changement de taille du modele. A relancer aussi apres une
passe HDRI, qui remplace le fond.

Parametre principal en tete du script : `EXPOSITION`. Le laisser a 1.0 sauf si le
rendu sort visiblement trop clair ou trop sombre — un objet tres sombre ou tres
clair decale la lecture.

### Calibration, verifiee

La puissance d'une source suit le carre de sa distance a l'objet. Reference
etablie par mesure sur cette machine, a deux echelles separees d'un facteur 5 :

```
puissance de la source cle, en watts = 9 x (distance en metres)^2
remplissage = 0,38 x cle          contre = 0,50 x cle
distance des sources = 3 x la plus grande dimension de l'objet
taille de source = 0,7 x distance (cle et contre), 1,0 x distance (remplissage)
```

Consequence utile : ne jamais recopier une puissance vue ailleurs sans la
rapporter a la distance. Une valeur juste a 2 m est surexposee d'un facteur 45 a
30 cm.

## Moteur

Regle par `eclairage_controle.py`. Detail, si un ajustement est necessaire :

```python
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'      # Blender 3.4 ; en 4.2+ : BLENDER_EEVEE_NEXT
sc.eevee.taa_render_samples = 64
sc.eevee.use_gtao = True                # occlusion ambiante : revele les creux
sc.eevee.gtao_distance = 0.2
sc.eevee.use_ssr = True                 # reflets
sc.view_settings.view_transform = 'Filmic'
sc.render.film_transparent = False
```

EEVEE fonctionne sous ecran virtuel, verifie sur cette machine. Rapide, suffisant
pour tous les rendus de controle.

Passer a Cycles seulement pour la livraison finale, ou si transparence ou
refraction doivent etre credibles :

```python
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 128
sc.cycles.use_denoising = True
```

Cycles en CPU est lent : reduire la resolution pendant les essais.

## Occlusion ambiante seule, pour lire la forme

Pour juger une courbure ou un relief sans etre gene par la matiere, rendre en
argile : materiau gris uniforme temporaire sur tout, occlusion ambiante forte.
C'est la vue la plus severe pour la forme, donc la plus utile en P14.

```python
argile = bpy.data.materials.get("argile") or bpy.data.materials.new("argile")
argile.use_nodes = True
b = argile.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.55, 0.55, 0.55, 1.0)
b.inputs["Roughness"].default_value = 0.65
b.inputs["Specular"].default_value = 0.2
sc.view_layers[0].material_override = argile   # Cycles uniquement
```

En EEVEE, `material_override` n'existe pas : affecter le materiau argile a chaque
objet et retablir ensuite, ou basculer en Cycles pour cette passe.

## Environnement HDRI, pour la restitution

Requiert PolyHaven actif et le reseau.

```bash
echo 'import bpy; bpy.context.scene.blendermcp_use_polyhaven = True' \
  | python3 blender/scripts/mcp.py evalstdin
python3 blender/scripts/mcp.py cmd download_polyhaven_asset \
  '{"asset_id":"studio_small_09","asset_type":"hdris","resolution":"2k"}'
```

Environnements neutres utiles : `studio_small_09` (studio blanc propre),
`studio_small_03` (lumiere douce), `photo_studio_loft_hall` (studio photo),
`kloppenheim_06_puresky` (exterieur couvert, tres neutre).

Ne jamais utiliser un HDRI colore ou contraste pendant la boucle d'iteration : il
teinte les materiaux et fausse la comparaison avec les photos.

## Reproduire l'eclairage d'une photo

Si la critique de P14 porte sur un ecart d'ombres et non de forme, s'aligner sur
la photo plutot que sur le neutre : reperer la direction de l'ombre portee dans
la photo, orienter la source cle en consequence, ajuster la durete par la taille
de la source. Consigner ce reglage dans `JOURNAL.md` : il devra etre rejoue a
chaque iteration pour que les comparaisons restent valides.
