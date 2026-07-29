---
name: blender-materiaux
description: Donner a une surface sa couleur, sa matiere et sa finition dans Blender - metal, plastique, bois, verre, ceramique, textile, mat ou satine ou brillant, transparent ou translucide, plus les textures PBR PolyHaven et les inscriptions et marquages. TRIGGER quand je traite les points 7 a 11 de la checklist (couleurs, matieres, textures, transparence, inscriptions) ou quand la critique porte sur l'aspect de surface plutot que sur la forme.
---

# Matieres et finitions

Prerequis : `blender-session` verifiee.

## Principe

Une matiere par zone decrite comme homogene. Ne pas mutualiser deux zones dont
l'utilisateur a distingue la finition, meme si la couleur est identique : c'est
la finition qui porte le realisme.

Nom du materiau = zone anatomique + matiere : `corps_plastique_satine`,
`bord_libre_metal_brosse`.

## Materiau de base

```python
import bpy

def materiau(nom, couleur, rugosite=0.5, metal=0.0, alpha=1.0):
    mat = bpy.data.materials.get(nom) or bpy.data.materials.new(nom)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*couleur, 1.0)
    bsdf.inputs["Roughness"].default_value = rugosite
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Alpha"].default_value = alpha
    if alpha < 1.0:
        mat.blend_method = 'BLEND'
    return mat

ob = bpy.data.objects["corps"]
ob.data.materials.clear()
ob.data.materials.append(materiau("corps_plastique_satine", (0.15, 0.16, 0.18), 0.35))
```

Noms d'entrees valables en Blender 3.x. En 4.x, `Transmission` devient
`Transmission Weight` et `Specular` devient `Specular IOR Level`.

## Bareme de reglage

Traduction des descripteurs verbaux en valeurs. Point de depart, a ajuster au vu
des rendus de controle.

| Finition decrite | Rugosite | Metallique |
|---|---|---|
| poli miroir | 0.02 - 0.08 | selon matiere |
| brillant, verni | 0.10 - 0.20 | 0 |
| satine | 0.30 - 0.45 | 0 |
| mat | 0.60 - 0.80 | 0 |
| granuleux, sable, moulure grainee | 0.85 - 1.0 | 0 |

| Matiere | Metallique | Rugosite | Remarques |
|---|---|---|---|
| acier brosse | 1.0 | 0.35 | rugosite anisotrope si le brossage est visible |
| aluminium anodise | 1.0 | 0.45 | couleur legerement teintee |
| chrome | 1.0 | 0.05 | |
| plastique ABS | 0.0 | 0.35 | |
| plastique mat | 0.0 | 0.70 | |
| caoutchouc | 0.0 | 0.90 | couleur tres sombre, jamais noir pur |
| bois verni | 0.0 | 0.25 | texture indispensable |
| ceramique emaillee | 0.0 | 0.10 | |
| verre | 0.0 | 0.02 | voir transparence |
| textile | 0.0 | 0.85 | texture indispensable |

Aucune couleur reelle n'est un noir pur ni un blanc pur. Plancher a 0.02,
plafond a 0.90 en valeur lineaire.

## Transparence et translucidite

```python
bsdf.inputs["Transmission"].default_value = 1.0   # verre
bsdf.inputs["IOR"].default_value = 1.45           # verre 1.45-1.52, eau 1.33, plastique 1.49
bsdf.inputs["Roughness"].default_value = 0.02     # depoli: monter vers 0.3
mat.use_screen_refraction = True                  # requis en EEVEE
bpy.context.scene.eevee.use_ssr = True
bpy.context.scene.eevee.use_ssr_refraction = True
```

Le verre exige une epaisseur reelle : une surface sans epaisseur ne refracte pas
correctement. Poser un SOLIDIFY si l'element est modelise en simple paroi.

## Degrades et limites de zone

- **Limite nette** entre deux couleurs : separer en deux materiaux et affecter
  par groupe de faces, ou poser un masque par texture.
- **Degrade progressif** : melanger deux BSDF via un noeud de degrade oriente sur
  l'axe anatomique concerne.

Toujours demander a l'utilisateur si une limite est nette ou floue — la reponse
change la construction et n'est presque jamais lisible sur photo.

## Textures PBR PolyHaven

Utile pour bois, beton, tissu, metal grene, cuir. Requiert l'integration
PolyHaven active dans l'addon et un acces reseau.

```bash
echo 'import bpy; print(bpy.context.scene.blendermcp_use_polyhaven)' \
  | python3 blender/scripts/mcp.py evalstdin
```

Si desactive, l'activer :

```bash
echo 'import bpy; bpy.context.scene.blendermcp_use_polyhaven = True' \
  | python3 blender/scripts/mcp.py evalstdin
```

Puis, par le socket :

```bash
python3 blender/scripts/mcp.py cmd download_polyhaven_asset \
  '{"asset_id":"wood_table_001","asset_type":"textures","resolution":"2k"}'
python3 blender/scripts/mcp.py cmd set_texture \
  '{"object_name":"corps","texture_id":"wood_table_001"}'
```

Regler ensuite l'echelle du mapping pour que le motif corresponde a l'echelle
reelle de l'objet — une texture de bois calibree pour une table est grotesque sur
un objet de 40 mm.

## Inscriptions, marquages, gravures

Par ordre de cout croissant :

1. **Serigraphie ou impression a plat** : image en texture, mixee sur la couleur
   de base par un masque alpha. Aucune geometrie.
2. **Gravure ou relief peu profond** : carte de relief (bump) a partir de la meme
   image. Aucune geometrie, mais le relief accroche la lumiere.
3. **Relief franc, lettres en saillie** : geometrie reelle par booleen. A reserver
   aux cas ou le relief se lit nettement sur les photos.

Le texte exact doit venir de l'utilisateur, jamais d'une lecture incertaine sur
photo. Si illisible : question ouverte.

## Artefacts d'usure

Point 12 de la checklist. Rayures, eclats, salissures se traitent par variation
locale de rugosite plutot que par variation de couleur : une rayure sur surface
brillante est d'abord une zone plus rugueuse. Ne les poser qu'apres validation de
la forme, jamais avant.

## Rapport a l'utilisateur

Decrire en termes de matiere et de finition perçues, pas de valeurs numeriques :
« face ventrale en plastique satine gris ardoise, bord lateral plus brillant ».
