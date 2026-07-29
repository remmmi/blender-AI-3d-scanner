"""Pipeau, element 1 : volume du corps.

Section transversale constante, definie dans _geom.py, extrudee sur 90 mm en
craniocaudal. Repere : X medio-lateral, Y ventro-dorsal (0 = face ventrale),
Z craniocaudal (0 = face caudale). Unites de scene en metres.

Script relancable : supprime l'objet homonyme avant de reconstruire.
"""

import importlib
import math
import sys

import bmesh
import bpy

DOSSIER = "/home/m/projet/blender/objets/pipeau/blender/scripts"
if DOSSIER not in sys.path:
    sys.path.insert(0, DOSSIER)
import _geom
importlib.reload(_geom)

MM = _geom.MM
NOM = "corps_volume"
CONGE_EXTREMITES = 1.0


def construire():
    old = bpy.data.objects.get(NOM)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)

    pts = _geom.section_fermee()

    bm = bmesh.new()
    verts = [bm.verts.new((x * MM, y * MM, 0.0)) for (x, y) in pts]
    bm.faces.new(verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

    ret = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    deplaces = [e for e in ret["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=deplaces, vec=(0.0, 0.0, _geom.HAUTEUR * MM))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

    mesh = bpy.data.meshes.new(NOM)
    bm.to_mesh(mesh)
    bm.free()

    ob = bpy.data.objects.new(NOM, mesh)
    bpy.context.scene.collection.objects.link(ob)

    m = ob.modifiers.new("conges_extremites", "BEVEL")
    m.width = CONGE_EXTREMITES * MM
    m.segments = 4
    m.limit_method = "ANGLE"
    m.angle_limit = math.radians(40.0)

    for f in mesh.polygons:
        f.use_smooth = True
    mesh.use_auto_smooth = True
    mesh.auto_smooth_angle = math.radians(25.0)

    print("section: %d points" % len(pts))
    print("corps nu, dimensions mm:", tuple(round(v / MM, 2) for v in ob.dimensions))
    return ob


construire()
