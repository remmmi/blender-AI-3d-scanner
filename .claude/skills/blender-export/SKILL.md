---
name: blender-export
description: Sortir le modele hors de Blender - export GLB ou GLTF, OBJ, STL pour impression 3D, FBX, et generation d'une visionneuse HTML autonome pour tourner autour du modele dans un navigateur. TRIGGER a l'etape P17 livraison, ou quand l'utilisateur demande un fichier, un format, une impression 3D, ou de voir le modele hors de Blender.
---

# Export et livraison

Prerequis : `blender-session` verifiee, modele valide en P13 ou P16.

## Choisir le format

| Besoin | Format | Remarque |
|---|---|---|
| voir, partager, web | GLB | matieres et couleurs incluses, un seul fichier |
| impression 3D | STL | geometrie seule, exige un volume ferme |
| edition dans un autre logiciel | OBJ ou FBX | OBJ plus simple, FBX si animation |
| retour dans Blender | .blend | le fichier de travail lui-meme |

Ne pas livrer plusieurs formats par defaut : demander lequel sert a quoi.

## Preparation avant export

1. Appliquer les modificateurs necessaires — beaucoup de formats les ignorent.
2. Supprimer ou exclure la collection `outils` et les cameras et sources de
   lumiere si le destinataire n'en veut pas.
3. Verifier l'echelle : 1 unite Blender = 1 m. Un STL destine a l'impression est
   generalement attendu en millimetres, donc a l'echelle 1000.
4. Recentrer l'objet sur l'origine si le destinataire l'attend centre.

```python
import bpy
for ob in bpy.context.scene.objects:
    if ob.type == 'MESH':
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        for m in list(ob.modifiers):
            bpy.ops.object.modifier_apply(modifier=m.name)
```

Appliquer les modificateurs **sur une copie du fichier**, jamais sur le fichier de
travail : la geometrie redevient non editable et les iterations ulterieures sont
perdues.

## Exports

```python
import bpy
BASE = "/home/m/projet/blender/blender/exports/"

bpy.ops.export_scene.gltf(
    filepath=BASE + "modele.glb",
    export_format='GLB',
    use_selection=False,
    export_apply=True,          # applique les modificateurs a l'export
)

bpy.ops.export_mesh.stl(
    filepath=BASE + "modele.stl",
    use_selection=True,
    global_scale=1000.0,        # metres vers millimetres
    ascii=False,
)

bpy.ops.export_scene.obj(filepath=BASE + "modele.obj", use_materials=True)
bpy.ops.export_scene.fbx(filepath=BASE + "modele.fbx", path_mode='COPY', embed_textures=True)
```

`export_scene.obj` est l'operateur de Blender 3.x ; en 4.x il devient
`wm.obj_export`.

## Verifier l'export

Un export qui ne leve pas d'erreur peut etre vide.

```bash
ls -l blender/exports/
python3 - <<'EOF'
import struct
with open('/home/m/projet/blender/blender/exports/modele.glb','rb') as f:
    magic, version, length = struct.unpack('<4sII', f.read(12))
print(magic, version, length, 'octets')
EOF
```

Pour un STL destine a l'impression, verifier que le volume est ferme : chaque
arete doit appartenir a exactement deux faces.

```python
import bpy, bmesh
ob = bpy.context.object
bm = bmesh.new(); bm.from_mesh(ob.data)
ouvertes = [e for e in bm.edges if len(e.link_faces) != 2]
print("aretes non fermees:", len(ouvertes))
bm.free()
```

Un modele non ferme n'est pas imprimable : le signaler a l'utilisateur en termes
de forme — « la paroi ventrale n'a pas d'epaisseur, l'objet est une coque ouverte »
— et proposer de poser une epaisseur.

## Visionneuse HTML autonome

Un fichier HTML unique, ouvrable par double clic, permettant a l'utilisateur de
tourner autour du modele sans installer quoi que ce soit. Utile en livraison
pour quelqu'un qui ne connait pas Blender.

Construction : exporter en GLB, encoder le GLB en base64 dans le HTML, charger
Three.js et OrbitControls. Le fichier devient volumineux — au-dela d'une
vingtaine de megaoctets, livrer plutot le GLB et le HTML separement dans le meme
dossier.

Alternative sans dependance : livrer le GLB seul et indiquer a l'utilisateur
qu'il s'ouvre par glisser-deposer sur https://gltf-viewer.donmccurdy.com — a ne
proposer que si l'utilisateur accepte de deposer le fichier sur un service
externe.

## Documentation de livraison

Accompagner tout export de `livraison/OBJET.md` : identification, dimensions
reelles, matieres par zone, points restes incertains, et ce que le modele ne
represente pas. C'est ce document, pas le fichier 3D, qui permet a quelqu'un de
reprendre le travail.
