"""Pipeau : face craniale, plaque support et piece silicone.

Sur la face craniale, une plaque d'aluminium recoit l'assise du reservoir. Une
piece de silicone rouge l'entoure sur environ 1 mm de large, et se poursuit vers
le ventral : c'est elle qui forme la facette inclinee descendant vers le caudal
et le ventral pour rejoindre la face ventrale.

Releve par l'utilisateur sur l'objet.
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

# --- parametres -------------------------------------------------------------

Z_FACE = _geom.HAUTEUR          # plan de la face craniale, 90 mm
SILICONE_EPAISSEUR = 0.5        # epaisseur apparente de la piece silicone
BORDURE = 1.0                   # largeur de silicone visible autour de la plaque
JEU = 0.02                      # decalage evitant la concurrence d'affichage

# chanfrein cranio-ventral, mêmes cotes que dans ventral_caudal.py
CHANFREIN_Z_BAS = 80.0
CHANFREIN_Y_HAUT = 9.887

PLAQUE_CONGE = 3.0


def prisme_section(nom, z0, z1):
    """Prisme droit ayant pour base la section transversale du corps."""
    old = bpy.data.objects.get(nom)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    pts = _geom.section_fermee()
    bm = bmesh.new()
    verts = [bm.verts.new((x * MM, y * MM, z0 * MM)) for (x, y) in pts]
    bm.faces.new(verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    ret = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    hauts = [e for e in ret["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=hauts, vec=(0.0, 0.0, (z1 - z0) * MM))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(nom)
    bm.to_mesh(mesh)
    bm.free()
    ob = bpy.data.objects.new(nom, mesh)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def bloc(nom, centre, dims, conge=0.0):
    old = bpy.data.objects.get(nom)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= dims[0] * MM
        v.co.y *= dims[1] * MM
        v.co.z *= dims[2] * MM
    mesh = bpy.data.meshes.new(nom)
    bm.to_mesh(mesh)
    bm.free()
    ob = bpy.data.objects.new(nom, mesh)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = tuple(c * MM for c in centre)
    if conge > 0.0:
        m = ob.modifiers.new("conge", "BEVEL")
        m.width = conge * MM
        m.segments = 4
        m.limit_method = "ANGLE"
        m.angle_limit = math.radians(35.0)
    return ob


def outil(ob):
    ob.display_type = "WIRE"
    ob.hide_render = True
    _geom.ranger(ob, "outils")
    return ob


def soustraire(cible, nom_mod, outil_ob):
    for m in list(cible.modifiers):
        if m.name == nom_mod:
            cible.modifiers.remove(m)
    m = cible.modifiers.new(nom_mod, "BOOLEAN")
    m.operation = "DIFFERENCE"
    m.object = outil_ob
    m.solver = "EXACT"
    return m


def outil_chanfrein(nom):
    """Demi-espace retirant le coin cranio-ventral, identique a ventral_caudal."""
    dy = CHANFREIN_Y_HAUT
    dz = Z_FACE - CHANFREIN_Z_BAS
    longueur = math.hypot(dy, dz)
    ny, nz = -dz / longueur, dy / longueur
    cote = 60.0
    ob = bloc(nom,
              (0.0,
               dy / 2.0 + ny * cote / 2.0,
               CHANFREIN_Z_BAS + dz / 2.0 + nz * cote / 2.0),
              (cote, cote, cote))
    ob.rotation_euler = (math.asin(-ny), 0.0, 0.0)
    return outil(ob)


def main():
    # --- peau de silicone : elle couvre la face craniale et la facette
    silicone = prisme_section("silicone_cranial",
                              Z_FACE - SILICONE_EPAISSEUR, Z_FACE + JEU)
    soustraire(silicone, "chanfrein", outil_chanfrein("outil_chanfrein_silicone"))
    _geom.ranger(silicone, "corps")

    # peau portee par la facette inclinee elle-meme
    dy, dz = CHANFREIN_Y_HAUT, Z_FACE - CHANFREIN_Z_BAS
    longueur = math.hypot(dy, dz)
    ny, nz = -dz / longueur, dy / longueur
    peau = bloc("silicone_biseau",
                (0.0,
                 dy / 2.0 + ny * SILICONE_EPAISSEUR / 2.0,
                 CHANFREIN_Z_BAS + dz / 2.0 + nz * SILICONE_EPAISSEUR / 2.0),
                (30.0, 30.0, SILICONE_EPAISSEUR))
    peau.rotation_euler = (math.asin(-ny), 0.0, 0.0)
    # on ne garde que la part qui epouse le corps
    corps = bpy.data.objects.get("corps_volume")
    for m in list(peau.modifiers):
        peau.modifiers.remove(m)
    m = peau.modifiers.new("epouse_corps", "BOOLEAN")
    m.operation = "INTERSECT"
    m.object = corps
    m.solver = "EXACT"
    _geom.ranger(peau, "corps")

    # --- plaque d'aluminium recevant l'assise du reservoir
    y_min = CHANFREIN_Y_HAUT + BORDURE
    y_max = _geom.SOMMET - BORDURE
    plaque = bloc("plaque_alu",
                  (0.0, (y_min + y_max) / 2.0, Z_FACE - 1.0 + JEU * 2.0),
                  (2.0 * _geom.DEMI_MAX - 2.0 * BORDURE,
                   y_max - y_min, 2.0),
                  conge=PLAQUE_CONGE)
    _geom.ranger(plaque, "corps")

    print("plaque alu: %.1f x %.1f mm, silicone visible sur %.1f mm de pourtour"
          % (2.0 * _geom.DEMI_MAX - 2.0 * BORDURE, y_max - y_min, BORDURE))


main()
