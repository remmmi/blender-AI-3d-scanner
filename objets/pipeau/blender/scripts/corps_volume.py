"""Pipeau, element 1 : volume du corps.

Section transversale constante, extrudee sur 90 mm en craniocaudal.
Repere : X medio-lateral, Y ventro-dorsal (0 = face ventrale), Z craniocaudal
(0 = face caudale). Unites de scene en metres.

Script relancable : supprime l'objet homonyme avant de reconstruire.
"""

import math

import bpy
import bmesh

NOM = "corps_volume"
MM = 0.001

# --- cotes de la section, en millimetres ------------------------------------

DEMI_VENTRALE = 10.5      # demi-largeur de la face ventrale plane
LARGEUR_BISEAU = 10.0     # largeur mesuree sur la facette
GAIN_X_BISEAU = 3.0       # ce que le biseau gagne en medio-lateral
DEMI_MAX = 13.5           # demi-largeur maximale de la section
FLANC_FIN = 34.5          # limite ventro-dorsale de la portion plane du flanc
SOMMET = 53.0             # sommet dorsal, hors saillie des boutons
RAYON_VENTRAL = 1.0       # arete ventrale du biseau, rayon tres serre
RAYON_DORSAL = 2.0        # arete dorsale du biseau, rayon leger
EXPOSANT_OGIVE = 3.0      # ogive aplatie, retenue par l'utilisateur en P13
PAS_OGIVE = 24            # segments sur le quart d'ogive
PAS_CONGE = 6             # segments par arete arrondie

HAUTEUR = 90.0
CONGE_EXTREMITES = 1.0    # congé des aretes craniale et caudale


def bezier(p0, p1, p2, n):
    """Arc quadratique approximant un conge entre deux segments."""
    pts = []
    for i in range(1, n):
        t = i / float(n)
        u = 1.0 - t
        pts.append((
            u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
        ))
    return pts


def profil_demi():
    """Points de la section pour X >= 0, du plan sagittal ventral vers le sommet."""
    gain_y = math.sqrt(LARGEUR_BISEAU ** 2 - GAIN_X_BISEAU ** 2)
    dir_biseau = (GAIN_X_BISEAU / LARGEUR_BISEAU, gain_y / LARGEUR_BISEAU)

    coin_ventral = (DEMI_VENTRALE, 0.0)
    coin_dorsal = (DEMI_MAX, gain_y)

    # longueurs de retrait de part et d'autre de chaque coin
    dev_v = math.acos(dir_biseau[0])                 # deviation au coin ventral
    ret_v = RAYON_VENTRAL * math.tan(dev_v / 2.0)
    dev_d = math.acos(dir_biseau[1])                 # deviation au coin dorsal
    ret_d = RAYON_DORSAL * math.tan(dev_d / 2.0)

    pts = [(0.0, 0.0), (coin_ventral[0] - ret_v, 0.0)]
    pts += bezier(
        (coin_ventral[0] - ret_v, 0.0),
        coin_ventral,
        (coin_ventral[0] + ret_v * dir_biseau[0], ret_v * dir_biseau[1]),
        PAS_CONGE,
    )
    pts.append((coin_ventral[0] + ret_v * dir_biseau[0], ret_v * dir_biseau[1]))
    pts.append((coin_dorsal[0] - ret_d * dir_biseau[0], coin_dorsal[1] - ret_d * dir_biseau[1]))
    pts += bezier(
        (coin_dorsal[0] - ret_d * dir_biseau[0], coin_dorsal[1] - ret_d * dir_biseau[1]),
        coin_dorsal,
        (DEMI_MAX, coin_dorsal[1] + ret_d),
        PAS_CONGE,
    )
    pts.append((DEMI_MAX, coin_dorsal[1] + ret_d))
    pts.append((DEMI_MAX, FLANC_FIN))

    # ogive : superellipse tangente verticale au depart, sommet sur X = 0
    a, b = DEMI_MAX, SOMMET - FLANC_FIN
    n = EXPOSANT_OGIVE
    for i in range(1, PAS_OGIVE + 1):
        t = i / float(PAS_OGIVE)
        y = b * t
        x = a * (1.0 - t ** n) ** (1.0 / n)
        pts.append((x, FLANC_FIN + y))
    return pts


def section_fermee():
    demi = profil_demi()
    gauche = [(-x, y) for (x, y) in reversed(demi[1:-1])]
    return demi + gauche


def construire():
    old = bpy.data.objects.get(NOM)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)

    pts = section_fermee()

    bm = bmesh.new()
    verts = [bm.verts.new((x * MM, y * MM, 0.0)) for (x, y) in pts]
    bm.faces.new(verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

    ret = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    deplaces = [e for e in ret["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=deplaces, vec=(0.0, 0.0, HAUTEUR * MM))
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
    m.harden_normals = False

    for f in mesh.polygons:
        f.use_smooth = True
    mesh.use_auto_smooth = True
    mesh.auto_smooth_angle = math.radians(25.0)

    print("section: %d points" % len(pts))
    print("dimensions mm:", tuple(round(v / MM, 2) for v in ob.dimensions))
    return ob


construire()
