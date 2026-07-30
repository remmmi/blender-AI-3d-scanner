"""Pipeau, elements 4 a 6 : armature creme, panneau de skai, surpiqures.

L'armature est une piece unique et continue enveloppant le corps :
  - sur chaque flanc, une bande longitudinale longeant le bord ventral ;
  - deux ceintures qui, depuis les extremites de cette bande, montent vers le
    dorsal en obliquant, puis ceinturent la moitie dorsale.

Le skai occupe tout ce que l'armature laisse libre entre les deux ceintures, du
bord dorsal de la bande longitudinale jusqu'au sommet dorsal, en passant d'un
flanc a l'autre. Il est en depression sous le pourtour rouge.

Positions des coudes du chevron relevees sur la planche p01 : 24 et 78 mm au
dessus de la face caudale.
"""

import importlib
import math
import os
import sys

import bpy

DOSSIER = os.path.dirname(os.path.abspath(
    "/home/m/projet/blender/objets/pipeau/blender/scripts/armature_skai.py"))
if DOSSIER not in sys.path:
    sys.path.insert(0, DOSSIER)
import _geom
importlib.reload(_geom)

MM = _geom.MM

# --- parametres -------------------------------------------------------------

# Valeurs revisees en P15 apres confrontation aux planches p01, p03 et p04.
# La premiere passe donnait une piece creme de 8.5 mm, soit moins de la moitie de
# sa largeur reelle, et faisait mourir le creme sur l'arete craniale alors que
# l'objet interpose toujours une bande de peinture rouge d'environ 6 mm.
COUDE_CAUDAL = 18.0        # hauteur du coude caudal du chevron
COUDE_CRANIAL = 72.0       # hauteur du coude cranial
BANDE_LARGEUR = 18.0       # largeur de la bande longitudinale, en curviligne
# La piece creme ne demarre pas sur l'arete du biseau : une bordure de peinture
# rouge court entre les deux, et c'est elle qui porte le slider du flanc droit.
BORDURE_ROUGE = 6.0
CEINTURE_DEMI = 5.45       # demi-largeur des ceintures
CEINTURE_CAUDALE_DORSALE = 9.0    # hauteur de la ceinture caudale au sommet dorsal
CEINTURE_CRANIALE_DORSALE = 80.0  # hauteur de la ceinture craniale au sommet dorsal

SAILLIE_ARMATURE = 1.5     # renflement de la piece creme au dessus du pourtour
DEPRESSION_SKAI = 0.5      # enfoncement de la surface du skai
PROFONDEUR_ENTAILLE = 1.0  # profondeur de la decoupe recevant le skai

# Pas de calcul de la nappe. Les bords obliques des ceintures sont quantifies par
# ce pas : a 0.5 mm ils sortaient en marches de 1.2 mm, nettement visibles.
PAS_Z = 0.2

SURPIQURE_LARGEUR = 0.6
SURPIQURE_PROFONDEUR = 0.35

REP = _geom.reperes()
SU_BANDE_DEBUT = REP["biseau"] + BORDURE_ROUGE
SU_BANDE_FIN = SU_BANDE_DEBUT + BANDE_LARGEUR
SU_MILIEU_BANDE = 0.5 * (SU_BANDE_DEBUT + SU_BANDE_FIN)
SU_SOMMET = REP["sommet"]


def _hauteur_ceinture(su, z_bande, z_dorsal):
    """Ligne moyenne d'une ceinture : elle part du bout de la bande et oblique."""
    if su <= SU_MILIEU_BANDE:
        return z_bande
    t = (su - SU_MILIEU_BANDE) / max(SU_SOMMET - SU_MILIEU_BANDE, 1e-6)
    return z_bande + (z_dorsal - z_bande) * t


def _dans_ceinture(su, z, z_bande, z_dorsal):
    return abs(z - _hauteur_ceinture(su, z_bande, z_dorsal)) <= CEINTURE_DEMI


def region_armature(su, z):
    if SU_BANDE_DEBUT <= su <= SU_BANDE_FIN and COUDE_CAUDAL <= z <= COUDE_CRANIAL:
        return True
    if su < SU_BANDE_DEBUT:
        return False
    if su < REP["biseau"]:
        return False
    if _dans_ceinture(su, z, COUDE_CAUDAL, CEINTURE_CAUDALE_DORSALE):
        return True
    if _dans_ceinture(su, z, COUDE_CRANIAL, CEINTURE_CRANIALE_DORSALE):
        return True
    return False


def region_skai(su, z):
    if su <= SU_BANDE_FIN:
        return False
    bas = _hauteur_ceinture(su, COUDE_CAUDAL, CEINTURE_CAUDALE_DORSALE) + CEINTURE_DEMI
    haut = _hauteur_ceinture(su, COUDE_CRANIAL, CEINTURE_CRANIALE_DORSALE) - CEINTURE_DEMI
    return bas <= z <= haut


SURPIQURE_X = 7.5          # position medio-laterale des deux surpiqures


def region_surpiqure(su, z):
    """Deux lignes longitudinales encadrant le revetement, sur le dos."""
    if not region_skai(su, z):
        return False
    return abs(abs(_geom.x_de_su(su)) - SURPIQURE_X) <= SURPIQURE_LARGEUR / 2.0


def corps():
    ob = bpy.data.objects.get("corps_volume")
    if ob is None:
        raise RuntimeError("corps_volume absent : lancer corps_volume.py d'abord")
    return ob


def entailler_skai():
    """Creuse le logement du skai dans le corps."""
    outil = _geom.nappe(
        "outil_entaille_skai", region_skai,
        decalage=-PROFONDEUR_ENTAILLE,
        epaisseur=PROFONDEUR_ENTAILLE + 3.0,
        vers_exterieur=True, lisse=False, pas_z=PAS_Z,
    )
    outil.display_type = "WIRE"
    outil.hide_render = True
    _geom.ranger(outil, "outils")

    c = corps()
    for m in list(c.modifiers):
        if m.name == "entaille_skai":
            c.modifiers.remove(m)
    m = c.modifiers.new("entaille_skai", "BOOLEAN")
    m.operation = "DIFFERENCE"
    m.object = outil
    m.solver = "EXACT"
    return outil


def main():
    armature = _geom.nappe(
        "armature", region_armature,
        decalage=0.0, epaisseur=SAILLIE_ARMATURE, vers_exterieur=True,
        pas_z=PAS_Z,
    )
    b = armature.modifiers.new("renflement", "BEVEL")
    b.width = 0.9 * MM
    b.segments = 3
    b.limit_method = "ANGLE"
    b.angle_limit = math.radians(35.0)
    _geom.ranger(armature, "corps")

    outil = entailler_skai()

    skai = _geom.nappe(
        "skai", region_skai,
        decalage=-DEPRESSION_SKAI, epaisseur=0.5, vers_exterieur=False,
        pas_z=PAS_Z,
    )
    _geom.ranger(skai, "corps")

    surpiqure = _geom.nappe(
        "surpiqures", region_surpiqure,
        decalage=-DEPRESSION_SKAI + SURPIQURE_PROFONDEUR,
        epaisseur=SURPIQURE_PROFONDEUR, vers_exterieur=False,
        pas_z=PAS_Z,
    )
    if surpiqure:
        _geom.ranger(surpiqure, "corps")

    _geom.ranger(corps(), "corps")

    print("reperes curvilignes:", {k: round(v, 2) for k, v in REP.items()})
    print("bande longitudinale: su %.2f a %.2f" % (SU_BANDE_DEBUT, SU_BANDE_FIN))
    print("outil booleen:", outil.name)


main()
