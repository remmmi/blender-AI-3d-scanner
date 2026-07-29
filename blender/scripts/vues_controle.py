"""Rendus des vues anatomiques normalisees.

Execute dans Blender via:
    python3 blender/scripts/mcp.py exec blender/scripts/vues_controle.py

Parametres lus dans les variables globales ci-dessous, a editer avant execution.
Convention d'orientation: X medio-lateral (positif = droite), Y ventro-dorsal
(positif = dorsal), Z craniocaudal (positif = cranial). Voir CLAUDE.md section 3.
"""

import math
import os

import bpy
import mathutils

# --- parametres -------------------------------------------------------------

SORTIE = None             # None = blender/renders du sous-projet actif
PREFIXE = "controle"
VUES = ["ventrale", "dorsale", "laterale_droite", "craniale"]
RESOLUTION = 1200
ORTHOGRAPHIQUE = True
FOCALE_MM = 50.0          # ignoree si ORTHOGRAPHIQUE
MARGE = 1.12              # 12 pour cent de vide autour de l'objet
COLLECTIONS_EXCLUES = {"outils"}

# --- direction d'observation par vue ----------------------------------------
# vecteur = position de la camera par rapport au centre de l'objet

DIRECTIONS = {
    "ventrale": (0.0, -1.0, 0.0),
    "dorsale": (0.0, 1.0, 0.0),
    "laterale_droite": (1.0, 0.0, 0.0),
    "laterale_gauche": (-1.0, 0.0, 0.0),
    "craniale": (0.0, 0.0, 1.0),
    "caudale": (0.0, 0.0, -1.0),
}


def racine_projet():
    """Dossier du sous-projet actif, lu dans objets/ACTIF."""
    racine = "/home/m/projet/blender"
    try:
        with open(os.path.join(racine, "objets", "ACTIF"), encoding="utf-8") as fh:
            nom = fh.read().strip()
        if nom:
            return os.path.join(racine, "objets", nom)
    except OSError:
        pass
    return racine


def objets_rendus():
    exclus = set()
    for nom in COLLECTIONS_EXCLUES:
        col = bpy.data.collections.get(nom)
        if col:
            exclus.update(o.name for o in col.objects)
    return [
        o for o in bpy.context.scene.objects
        if o.type in {"MESH", "CURVE", "SURFACE", "FONT"}
        and not o.hide_render
        and o.name not in exclus
    ]


def boite_englobante(objets):
    mini = mathutils.Vector((float("inf"),) * 3)
    maxi = mathutils.Vector((float("-inf"),) * 3)
    for ob in objets:
        for coin in ob.bound_box:
            p = ob.matrix_world @ mathutils.Vector(coin)
            mini = mathutils.Vector(map(min, mini, p))
            maxi = mathutils.Vector(map(max, maxi, p))
    return mini, maxi


def camera():
    ob = bpy.data.objects.get("camera_controle")
    if ob is None:
        data = bpy.data.cameras.new("camera_controle")
        ob = bpy.data.objects.new("camera_controle", data)
        bpy.context.scene.collection.objects.link(ob)
    ob.data.type = "ORTHO" if ORTHOGRAPHIQUE else "PERSP"
    if not ORTHOGRAPHIQUE:
        ob.data.lens = FOCALE_MM
    return ob


# Les vues d'axe craniocaudal sont degenerees pour to_track_quat : l'orientation
# de l'image y est fixee explicitement, dorsal vers le haut dans les deux cas.
EULERS_AXIAUX = {
    "craniale": (0.0, 0.0, 0.0),
    "caudale": (math.pi, 0.0, math.pi),
}


def cadrer(cam, centre, taille, direction, largeur_vue, hauteur_vue, vue=None):
    axe = mathutils.Vector(direction).normalized()
    recul = taille * 3.0
    cam.location = centre + axe * recul
    if vue in EULERS_AXIAUX:
        cam.rotation_mode = "XYZ"
        cam.rotation_euler = EULERS_AXIAUX[vue]
    else:
        cam.rotation_mode = "QUATERNION"
        cam.rotation_quaternion = axe.to_track_quat("Z", "Y")
    etendue = max(largeur_vue, hauteur_vue) * MARGE
    if ORTHOGRAPHIQUE:
        cam.data.ortho_scale = etendue
    else:
        cam.data.lens = FOCALE_MM
        cam.location = centre + axe * (etendue * FOCALE_MM / 36.0)
    cam.data.clip_start = max(recul * 0.01, 1e-4)
    cam.data.clip_end = recul * 4.0


def main():
    objets = objets_rendus()
    if not objets:
        print("ERREUR: aucun objet a rendre")
        return

    mini, maxi = boite_englobante(objets)
    centre = (mini + maxi) / 2.0
    dims = maxi - mini
    taille = max(dims)

    sc = bpy.context.scene
    cam = camera()
    sc.camera = cam
    sc.render.resolution_x = RESOLUTION
    sc.render.resolution_y = RESOLUTION
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"

    sortie = SORTIE or os.path.join(racine_projet(), "blender", "renders")
    os.makedirs(sortie, exist_ok=True)
    print("boite englobante m:", tuple(round(v, 4) for v in dims))
    print("centre m:", tuple(round(v, 4) for v in centre))

    # largeur et hauteur apparentes selon l'axe d'observation
    etendues = {
        "ventrale": (dims.x, dims.z),
        "dorsale": (dims.x, dims.z),
        "laterale_droite": (dims.y, dims.z),
        "laterale_gauche": (dims.y, dims.z),
        "craniale": (dims.x, dims.y),
        "caudale": (dims.x, dims.y),
    }

    for vue in VUES:
        if vue not in DIRECTIONS:
            print("vue inconnue ignoree:", vue)
            continue
        larg, haut = etendues[vue]
        cadrer(cam, centre, taille, DIRECTIONS[vue], larg, haut, vue)
        chemin = os.path.join(sortie, "%s_vue_%s.png" % (PREFIXE, vue))
        sc.render.filepath = chemin
        bpy.ops.render.render(write_still=True)
        print("rendu:", chemin)


main()
