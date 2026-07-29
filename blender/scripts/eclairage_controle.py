"""Eclairage neutre de controle, cadre automatiquement sur la taille de l'objet.

Execute dans Blender via:
    python3 blender/scripts/mcp.py exec blender/scripts/eclairage_controle.py

Trois sources larges a faible contraste plus un fond gris emissif. Aucune ombre
portee dure : le but est de lire la forme, pas de flatter l'objet.

Calibration verifiee a deux echelles (objet de 0,1 m et de 0,5 m) : la puissance
d'une source suit le carre de sa distance a l'objet. Puissance de la source cle
= 9 W par metre carre de distance.
"""

import bpy
import mathutils

# --- parametres -------------------------------------------------------------

EXPOSITION = 1.0          # >1 eclaircit, <1 assombrit
FOND = 0.18               # gris du fond, valeur lineaire
FOND_INTENSITE = 1.6
COLLECTIONS_EXCLUES = {"outils"}

# nom, direction (normalisee ensuite), part de puissance, taille relative
SOURCES = [
    ("cle", (0.66, -0.66, 0.66), 1.00, 0.70),
    ("remplissage", (-0.70, -0.50, 0.30), 0.38, 1.00),
    ("contre", (0.00, 0.85, 0.55), 0.50, 0.70),
]


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


def fond():
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (FOND, FOND, FOND, 1.0)
    bg.inputs["Strength"].default_value = FOND_INTENSITE


def moteur():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = 64
    sc.eevee.use_gtao = True
    sc.eevee.gtao_distance = 0.2
    sc.eevee.use_ssr = True
    sc.eevee.use_ssr_refraction = True
    sc.view_settings.view_transform = "Filmic"
    sc.render.film_transparent = False


def main():
    objets = objets_rendus()
    if not objets:
        print("ERREUR: aucun objet a eclairer")
        return

    mini, maxi = boite_englobante(objets)
    centre = (mini + maxi) / 2.0
    taille = max(maxi - mini)
    distance = max(taille * 3.0, 0.05)

    fond()
    moteur()

    for nom, direction, part, taille_rel in SOURCES:
        old = bpy.data.objects.get(nom)
        if old:
            bpy.data.objects.remove(old, do_unlink=True)
        data = bpy.data.lights.new(nom, "AREA")
        data.energy = 9.0 * distance * distance * part * EXPOSITION
        data.size = distance * taille_rel
        ob = bpy.data.objects.new(nom, data)
        bpy.context.scene.collection.objects.link(ob)
        axe = mathutils.Vector(direction).normalized()
        ob.location = centre + axe * distance
        ob.rotation_mode = "QUATERNION"
        ob.rotation_quaternion = axe.to_track_quat("Z", "Y")
        print("source %-12s distance %.3f m  puissance %.2f W  taille %.3f m"
              % (nom, distance, data.energy, data.size))

    print("objet: taille %.4f m, centre %s"
          % (taille, tuple(round(v, 4) for v in centre)))


main()
