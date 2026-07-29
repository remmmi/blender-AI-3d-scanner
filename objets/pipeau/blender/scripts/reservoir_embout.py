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

# Profils revises en P15. Mon premier releve, fait par seuillage de la silhouette
# sur la planche p01, concluait que la bague de base etait le point le plus large.
# C'etait faux : le verre est transparent, le seuillage manquait ses bords reels
# et sous-estimait son diametre. L'utilisateur a tranche, le verre renfle est le
# point le plus large et la bague de base est en retrait du corps.
#
# Etagement revise :
#   embase          90.0 a  98.3   diametre 26.2
#   verre           98.3 a 118.7   renflement convexe, 27.4 au maximum
#   bague d'air    118.7 a 125.5   24.1, porte la lumiere d'entree d'air
#   capuchon       125.5 a 131.9   22.7, cylindre droit a sommet chanfreine
#   embout         131.9 a 140.0   14.4
#
# L'objet est un empilement de cylindres droits a epaulements francs, non une
# suite de dômes. Listes de (rayon, z) en millimetres, du caudal vers le cranial.
PROFILS = {
    "embase": [(11.8, 90.0), (13.1, 90.9), (13.1, 96.9), (12.8, 98.3)],
    "cylindre_transparent": [(12.8, 98.3), (13.4, 102.5), (13.7, 108.5),
                             (13.4, 114.5), (12.8, 118.7)],
    "bague_air": [(12.8, 118.7), (12.05, 119.6), (12.05, 124.6), (11.35, 125.5)],
    "capuchon": [(11.35, 125.5), (11.35, 130.2), (10.2, 131.2), (8.4, 131.9)],
    "collerette": [(8.4, 131.9), (7.6, 132.2), (7.2, 132.6)],
    # chaine ouverte, du canal interne vers la base : une revolution sur profil
    # ferme ne produit aucune face
    "embout": [(3.5, 133.5), (3.5, 140.0), (6.5, 140.0), (7.2, 138.4),
               (7.2, 132.6), (7.1, 131.9)],
}

# Lumiere d'entree d'air : craniale, dans la gorge du chapeau, et non caudale
# comme la premiere passe le supposait. Nettement visible sur la planche p04.
# Orientee vers le dorsal dans l'etat d'assemblage photographie.
LUMIERE = dict(z=122.1, hauteur=3.0, largeur=14.0, profondeur=3.0, rayon=12.05)


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

    # Sans epaisseur, la piece est une nappe ouverte : toute decoupe booleenne y
    # echoue silencieusement. C'est ce qui avait fait disparaitre la lumiere d'air.
    ep = ob.modifiers.new("paroi", "SOLIDIFY")
    ep.thickness = 0.8 * MM
    ep.offset = -1.0

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
        v.co.x *= LUMIERE["largeur"] * MM
        v.co.y *= LUMIERE["profondeur"] * 2.0 * MM
        v.co.z *= LUMIERE["hauteur"] * MM
    mesh = bpy.data.meshes.new("outil_lumiere")
    bm.to_mesh(mesh)
    bm.free()
    ob = bpy.data.objects.new("outil_lumiere", mesh)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = (0.0, (AXE_Y + LUMIERE["rayon"]) * MM, LUMIERE["z"] * MM)
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
    for nom in ("embase", "cylindre_transparent", "bague_air",
                "capuchon", "collerette"):
        ob = revolution(nom, PROFILS[nom])
        _geom.ranger(ob, "reservoir")

    lumiere_air(bpy.data.objects["bague_air"])

    embout = revolution("embout", PROFILS["embout"])
    _geom.ranger(embout, "embout")

    for nom in ("embase", "cylindre_transparent", "bague_air",
                "capuchon", "collerette", "embout"):
        ob = bpy.data.objects[nom]
        print("%-22s z %.1f a %.1f mm" % (
            nom,
            min(z for (_, z) in PROFILS[nom]),
            max(z for (_, z) in PROFILS[nom])))

    print("hauteur totale visee: 140 mm")


main()
