"""Pipeau, elements 8 et 9 : reservoir et embout.

Deux corps de revolution d'axe craniocaudal, construits par profil revolu.
Diametre maximal du reservoir 26 mm, diametre du bord cranial de l'embout 15 mm,
cotes fournies par l'utilisateur.
"""

import importlib
import math
import os
import sys

import bmesh
import bpy

DOSSIER = "/home/m/projet/blender/objets/pipeau/blender/scripts"
if DOSSIER not in sys.path:
    sys.path.insert(0, DOSSIER)
import _geom
importlib.reload(_geom)

MM = _geom.MM
SEGMENTS = 64

Z_BASE = 90.0     # face craniale du corps
AXE_Y = 25.75      # l'axe de revolution passe par le milieu ventro-dorsal du corps,
                  # non par l'origine du monde qui est au ras de la face ventrale

# Profils releves au pixel sur la planche p01, silhouette ligne par ligne.
# Echelle etablie par deux calibrations concordantes a 1 pour cent pres : largeur
# de la face laterale du corps (55 mm) et diametre de l'embout (15 mm).
# Listes de (rayon, z) en millimetres, du caudal vers le cranial.
PROFILS = {
    # bague de base, point le plus large de tout l'ensemble
    "embase": [(13.5, 90.0), (15.0, 90.8), (15.0, 93.8), (14.6, 94.5)],
    "bague_caudale": [(14.6, 94.5), (14.4, 95.5), (14.4, 100.8), (13.2, 102.0)],
    # verre renfle en tonneau
    "cylindre_transparent": [(13.0, 102.0), (13.8, 105.0), (14.3, 108.0),
                             (13.9, 111.0), (13.2, 114.0)],
    # chapeau : evasement, gorge portant la lumiere d'air, puis bandeau
    "bague_craniale": [(13.2, 114.0), (13.4, 114.8), (12.2, 117.5), (11.0, 119.5),
                       (11.0, 122.0), (11.8, 122.8), (11.8, 126.0), (11.5, 126.5)],
    "collerette": [(11.5, 126.5), (11.0, 127.5), (8.6, 130.0), (7.6, 131.0)],
    # chaine ouverte, du canal interne vers la base : une revolution sur profil
    # ferme ne produit aucune face
    "embout": [(3.6, 133.0), (3.6, 140.0), (6.8, 140.0), (7.5, 138.6),
               (7.5, 132.0), (7.4, 131.0)],
}

# Lumiere d'entree d'air : craniale, dans la gorge du chapeau, et non caudale
# comme la premiere passe le supposait. Nettement visible sur la planche p04.
LUMIERE = dict(z=120.7, hauteur=2.4, largeur=12.0, profondeur=2.5, rayon=11.0)


def revolution(nom, profil, ferme=False):
    old = bpy.data.objects.get(nom)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)

    bm = bmesh.new()
    verts = [bm.verts.new((r * MM, 0.0, z * MM)) for (r, z) in profil]
    for a, b in zip(verts, verts[1:]):
        bm.edges.new((a, b))
    if ferme:
        bm.edges.new((verts[-1], verts[0]))
    mesh = bpy.data.meshes.new(nom)
    bm.to_mesh(mesh)
    bm.free()

    ob = bpy.data.objects.new(nom, mesh)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = (0.0, AXE_Y * MM, 0.0)

    m = ob.modifiers.new("revolution", "SCREW")
    m.axis = "Z"
    m.angle = 2.0 * math.pi
    m.steps = SEGMENTS
    m.render_steps = SEGMENTS
    m.use_merge_vertices = True
    # Le seuil par defaut vaut 0.01 m, soit 10 mm : a l'echelle de l'objet il
    # fusionne des pieces entieres. L'embout, de 3.6 mm de rayon interne,
    # disparaissait completement.
    m.merge_threshold = 1e-5
    m.use_normal_calculate = True

    for f in mesh.polygons:
        f.use_smooth = True
    mesh.use_auto_smooth = True
    mesh.auto_smooth_angle = math.radians(30.0)
    return ob


def outil(ob):
    ob.display_type = "WIRE"
    ob.hide_render = True
    _geom.ranger(ob, "outils")
    return ob


def lumiere_air(cible):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= LUMIERE["profondeur"] * 2.0 * MM
        v.co.y *= LUMIERE["largeur"] * MM
        v.co.z *= LUMIERE["hauteur"] * MM
    mesh = bpy.data.meshes.new("outil_lumiere")
    bm.to_mesh(mesh)
    bm.free()
    ob = bpy.data.objects.new("outil_lumiere", mesh)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = (LUMIERE["rayon"] * MM, AXE_Y * MM, LUMIERE["z"] * MM)
    outil(ob)

    for c in bpy.data.objects:
        for m in list(c.modifiers):
            if m.name == "lumiere_air":
                c.modifiers.remove(m)
    m = cible.modifiers.new("lumiere_air", "BOOLEAN")
    m.operation = "DIFFERENCE"
    m.object = ob
    m.solver = "EXACT"
    return ob


def main():
    reservoir = _geom.collection("reservoir")
    for nom in ("embase", "bague_caudale", "cylindre_transparent",
                "bague_craniale", "collerette"):
        ob = revolution(nom, PROFILS[nom])
        _geom.ranger(ob, "reservoir")

    lumiere_air(bpy.data.objects["bague_craniale"])

    embout = revolution("embout", PROFILS["embout"])
    _geom.ranger(embout, "embout")

    for nom in ("embase", "bague_caudale", "cylindre_transparent",
                "bague_craniale", "collerette", "embout"):
        ob = bpy.data.objects[nom]
        print("%-22s z %.1f a %.1f mm" % (
            nom,
            min(z for (_, z) in PROFILS[nom]),
            max(z for (_, z) in PROFILS[nom])))

    print("hauteur totale visee: 140 mm")


main()
