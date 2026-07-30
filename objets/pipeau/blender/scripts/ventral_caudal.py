"""Pipeau, elements 2, 3 et 7 : panneau ventral, boutons, volet caudal.

Ces trois elements reposent sur des faces planes du corps, la face ventrale
(Y = 0) et la face caudale (Z = 0). Ils se construisent donc par volumes
prismatiques simples, sans passer par la machinerie de nappe.
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

# --- panneau ventral --------------------------------------------------------

PANNEAU_LARGEUR = 18.0
PANNEAU_HAUTEUR = 68.0
PANNEAU_Z = 11.0            # bord caudal du panneau
PANNEAU_ENFONCEMENT = 0.3
PANNEAU_CONGE = 2.0

# --- boutons ----------------------------------------------------------------

# Positions et cotes revisees en P15 sur la planche p02. Le bouton de mise a feu
# etait 15 mm trop caudal, et le bouton de reglage etait plus etroit que lui alors
# que l'objet a le rapport inverse.
BOUTON_FEU = dict(largeur=11.0, hauteur=13.5, z=69.3, saillie=2.0, conge=2.2)
BOUTON_REGLAGE = dict(largeur=14.4, hauteur=6.5, z=17.0, saillie=1.0, conge=1.8)

# --- chanfrein cranio-ventral -----------------------------------------------
# Releve en P15 sur les planches p02 et p03. La face craniale ne rejoint pas la
# face ventrale par une arete : une facette inclinee part de la face craniale a
# l'aplomb de l'arete dorsale du biseau et descend jusqu'a mourir sur la face
# ventrale, juste au dessus du bord cranial de l'ecran.

CHANFREIN_Z_BAS = 80.0      # ou la facette rejoint la face ventrale
CHANFREIN_Y_HAUT = 9.887    # arete dorsale du biseau, sur la face craniale

# --- volet caudal -----------------------------------------------------------

VOLET_LARGEUR = 16.0        # medio-lateral
VOLET_PROFONDEUR = 25.0     # ventro-dorsal
VOLET_Y = 12.0              # bord ventral du volet
VOLET_ENFONCEMENT = 0.6
VOLET_CONGE = 2.5
RAINURES = 8
RAINURE_LARGEUR = 0.9
RAINURE_PROFONDEUR = 0.5
RAINURE_ETENDUE = 11.0      # longueur d'une rainure en medio-lateral


def bloc(nom, cx, cy, cz, dx, dy, dz, conge=0.0, segments=4):
    """Pave droit centre, avec congé optionnel."""
    old = bpy.data.objects.get(nom)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= dx * MM
        v.co.y *= dy * MM
        v.co.z *= dz * MM
    mesh = bpy.data.meshes.new(nom)
    bm.to_mesh(mesh)
    bm.free()
    ob = bpy.data.objects.new(nom, mesh)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = (cx * MM, cy * MM, cz * MM)
    if conge > 0.0:
        m = ob.modifiers.new("conge", "BEVEL")
        m.width = conge * MM
        m.segments = segments
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


def main():
    corps = bpy.data.objects.get("corps_volume")
    if corps is None:
        raise RuntimeError("corps_volume absent")

    # --- chanfrein cranio-ventral, a couper avant tout le reste
    dy = CHANFREIN_Y_HAUT
    dz = _geom.HAUTEUR - CHANFREIN_Z_BAS
    longueur = math.hypot(dy, dz)
    # normale du plan, dirigee vers la matiere a retirer : ventral et cranial
    ny, nz = -dz / longueur, dy / longueur
    cote = 60.0
    milieu_y = dy / 2.0
    milieu_z = CHANFREIN_Z_BAS + dz / 2.0
    biseau = bloc("outil_chanfrein_cranial", 0.0,
                  milieu_y + ny * cote / 2.0,
                  milieu_z + nz * cote / 2.0,
                  cote, cote, cote)
    biseau.rotation_euler = (math.asin(-ny), 0.0, 0.0)
    outil(biseau)
    soustraire(corps, "chanfrein_cranial", biseau)

    # --- logement du panneau ventral
    z_centre = PANNEAU_Z + PANNEAU_HAUTEUR / 2.0
    creux = bloc("outil_creux_panneau", 0.0, PANNEAU_ENFONCEMENT, z_centre,
                 PANNEAU_LARGEUR, 2 * PANNEAU_ENFONCEMENT,
                 PANNEAU_HAUTEUR, conge=PANNEAU_CONGE, segments=3)
    outil(creux)
    soustraire(corps, "creux_panneau", creux)

    # --- panneau noir, affleurant le bord rouge
    # legerement en avant du plan de la face : strictement coplanaire, il perdrait
    # l'arbitrage d'affichage contre la face rouge
    panneau = bloc("panneau_ventral", 0.0, PANNEAU_ENFONCEMENT / 2.0 - 0.03, z_centre,
                   PANNEAU_LARGEUR - 0.05, PANNEAU_ENFONCEMENT,
                   PANNEAU_HAUTEUR - 0.05, conge=PANNEAU_CONGE * 0.9, segments=3)
    _geom.ranger(panneau, "corps")

    # --- boutons, en saillie ventrale
    for nom, p in (("bouton_feu", BOUTON_FEU), ("bouton_reglage", BOUTON_REGLAGE)):
        # le bloc est centre sur la face ventrale : la moitie ventrale forme la
        # saillie, la moitie dorsale s'enfonce dans le corps
        ob = bloc(nom, 0.0, 0.0, p["z"],
                  p["largeur"], p["saillie"] * 2.0, p["hauteur"],
                  conge=p["conge"], segments=4)
        _geom.ranger(ob, "corps")

    # --- logement du volet caudal
    y_centre = VOLET_Y + VOLET_PROFONDEUR / 2.0
    creux_volet = bloc("outil_creux_volet", 0.0, y_centre, VOLET_ENFONCEMENT,
                       VOLET_LARGEUR, VOLET_PROFONDEUR, 2 * VOLET_ENFONCEMENT,
                       conge=VOLET_CONGE, segments=3)
    outil(creux_volet)
    soustraire(corps, "creux_volet", creux_volet)

    volet = bloc("volet_caudal", 0.0, y_centre, VOLET_ENFONCEMENT / 2.0,
                 VOLET_LARGEUR - 0.05, VOLET_PROFONDEUR - 0.05, VOLET_ENFONCEMENT,
                 conge=VOLET_CONGE * 0.9, segments=3)
    _geom.ranger(volet, "corps")

    # --- rainures du volet, creusees dans le volet lui-meme
    pas = VOLET_PROFONDEUR * 0.55 / max(RAINURES - 1, 1)
    y0 = y_centre - pas * (RAINURES - 1) / 2.0
    for k in range(RAINURES):
        r = bloc("outil_rainure_%d" % k, 0.0, y0 + k * pas,
                 -RAINURE_PROFONDEUR / 2.0 + VOLET_ENFONCEMENT / 2.0,
                 RAINURE_ETENDUE, RAINURE_LARGEUR, RAINURE_PROFONDEUR * 2.0)
        outil(r)
        soustraire(volet, "rainure_%d" % k, r)

    print("panneau ventral: %.1f x %.1f mm, z de %.1f a %.1f"
          % (PANNEAU_LARGEUR, PANNEAU_HAUTEUR, PANNEAU_Z, PANNEAU_Z + PANNEAU_HAUTEUR))
    print("volet caudal: %.1f x %.1f mm, %d rainures"
          % (VOLET_LARGEUR, VOLET_PROFONDEUR, RAINURES))


main()
