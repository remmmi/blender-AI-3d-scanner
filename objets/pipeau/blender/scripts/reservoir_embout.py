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

# profils : listes de (rayon, z), du caudal vers le cranial
PROFILS = {
    "embase": [(9.0, 90.0), (11.5, 90.5), (12.0, 94.0), (12.0, 95.5)],
    "bague_caudale": [(12.0, 95.5), (13.0, 96.2), (13.0, 101.5), (12.4, 102.2)],
    "cylindre_transparent": [(12.4, 102.2), (12.9, 111.0), (12.4, 119.5)],
    "bague_craniale": [(12.4, 119.5), (13.0, 120.2), (13.0, 126.5), (11.5, 127.5)],
    "collerette": [(11.5, 127.5), (11.0, 128.0), (9.0, 129.5)],
    "embout": [(6.2, 129.5), (6.4, 131.0), (7.5, 138.5), (7.5, 140.0), (3.6, 140.0), (3.6, 133.0)],
}

# lumiere d'entree d'air, unilaterale, portee par le flanc droit
LUMIERE = dict(z=98.8, hauteur=2.2, largeur=9.0, profondeur=2.0)


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
    ob.location = (12.6 * MM, AXE_Y * MM, LUMIERE["z"] * MM)
    outil(ob)

    for m in list(cible.modifiers):
        if m.name == "lumiere_air":
            cible.modifiers.remove(m)
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

    lumiere_air(bpy.data.objects["bague_caudale"])

    embout = revolution("embout", PROFILS["embout"], ferme=True)
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
