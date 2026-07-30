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
# Cotes relevees sur la planche p01, la plus perpendiculaire au flanc.
# La piece creme demarre au ras de l'arete du biseau : la bordure rouge que la
# passe precedente avait interposee n'existe pas. Ce que la planche p03 montrait
# comme une bande rouge est la facette du biseau, vue moins de face.
# Les deux bords de la piece sont des SECTIONS PLANES du corps : un plan incline
# donne une droite oblique sur le flanc plat, epouse la courbure sur le dome, et
# ne casse jamais au passage de l'un a l'autre. La piece n'a ainsi que huit
# angles au total, quatre internes et quatre externes, la ou la bande
# longitudinale rencontre les deux ceintures.
COUDE_CAUDAL = 17.9        # ligne moyenne de la ceinture caudale, a l'arete du biseau
COUDE_CRANIAL = 69.8       # ligne moyenne de la ceinture craniale, a l'arete du biseau
PENTE = 0.2658             # variation craniocaudale par millimetre ventro-dorsal,
                           # montante pour la ceinture craniale, descendante pour
                           # la caudale : le chevron s'ouvre vers le dorsal
BANDE_LARGEUR = 18.0       # largeur de la bande longitudinale, en curviligne
BORDURE_ROUGE = 0.0
CEINTURE_DEMI = 4.0        # demi-largeur des ceintures, soit 8 mm au total

SAILLIE_ARMATURE = 1.5     # hauteur du plan de la piece creme au dessus du pourtour

# Profil en travers de la piece, cote par l'utilisateur. Largeur totale 8 mm.
# Du bord tourne vers le skai vers le bord tourne vers l'extremite :
#   1 mm de chanfrein arrondi, 4 mm de plan, 3 mm de biseau plan.
# Le bord vif du biseau est adouci sur 0.5 mm.
PROFIL_CHANFREIN = 1.0     # cote skai, arrondi
PROFIL_PLAN = 4.0
PROFIL_BISEAU = 3.0        # cote extremite, plan
PROFIL_ARETE = 0.5
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
SU_FLANC = REP["flanc"]
SU_SOMMET = REP["sommet"]


Y_BISEAU = _geom.y_de_su(REP["biseau"])


def _hauteur_ceinture(su, z_biseau, sens):
    """Ligne moyenne d'une ceinture, definie comme une section plane du corps."""
    return z_biseau + sens * PENTE * (_geom.y_de_su(su) - Y_BISEAU)


def _dans_ceinture(su, z, z_biseau, sens):
    return abs(z - _hauteur_ceinture(su, z_biseau, sens)) <= CEINTURE_DEMI


def region_armature(su, z):
    if su < REP["biseau"]:
        return False
    # la ceinture caudale descend vers le dorsal, la craniale monte : le chevron
    # s'ouvre vers le dorsal
    bas = _hauteur_ceinture(su, COUDE_CAUDAL, -1.0)
    haut = _hauteur_ceinture(su, COUDE_CRANIAL, +1.0)
    if SU_BANDE_DEBUT <= su <= SU_BANDE_FIN and bas <= z <= haut:
        return True
    return abs(z - bas) <= CEINTURE_DEMI or abs(z - haut) <= CEINTURE_DEMI


def region_skai(su, z):
    if su <= SU_BANDE_FIN:
        return False
    bas = _hauteur_ceinture(su, COUDE_CAUDAL, -1.0) + CEINTURE_DEMI
    haut = _hauteur_ceinture(su, COUDE_CRANIAL, +1.0) - CEINTURE_DEMI
    return bas <= z <= haut


SURPIQURE_X = 7.5          # position medio-laterale des deux surpiqures


def region_surpiqure(su, z):
    """Deux lignes longitudinales encadrant le revetement, sur le dos."""
    if not region_skai(su, z):
        return False
    return abs(abs(_geom.x_de_su(su)) - SURPIQURE_X) <= SURPIQURE_LARGEUR / 2.0


def _rampe_biseau(d):
    """Biseau plan de 3 mm, arete adoucie sur les 0.5 derniers millimetres."""
    if d <= 0.0:
        return 0.0
    if d >= PROFIL_BISEAU:
        return 1.0
    v = d / PROFIL_BISEAU
    if d < PROFIL_ARETE:
        # adoucissement de l'arete vive du biseau
        u = d / PROFIL_ARETE
        v *= u * u * (3.0 - 2.0 * u)
    return v


def _rampe_chanfrein(d):
    """Conge arrondi de 1 mm, cote skai."""
    if d <= 0.0:
        return 0.0
    if d >= PROFIL_CHANFREIN:
        return 1.0
    u = d / PROFIL_CHANFREIN
    return u * u * (3.0 - 2.0 * u)


def hauteur_armature(su, z):
    """Profil en travers de la piece creme, en millimetres au dessus du pourtour."""
    if not region_armature(su, z):
        return 0.0
    bas = _hauteur_ceinture(su, COUDE_CAUDAL, -1.0)
    haut = _hauteur_ceinture(su, COUDE_CRANIAL, +1.0)

    # bords tournes vers les extremites : biseau plan de 3 mm
    facteur = min(_rampe_biseau((haut + CEINTURE_DEMI) - z),
                  _rampe_biseau(z - (bas - CEINTURE_DEMI)))

    # bords tournes vers le skai : chanfrein arrondi de 1 mm
    if su > SU_BANDE_FIN:
        facteur = min(facteur,
                      _rampe_chanfrein((haut - CEINTURE_DEMI) - z)
                      if z < haut else 1.0,
                      _rampe_chanfrein(z - (bas + CEINTURE_DEMI))
                      if z > bas else 1.0)
    else:
        facteur = min(facteur, _rampe_chanfrein(SU_BANDE_FIN - su))

    return SAILLIE_ARMATURE * facteur


def corps():
    ob = bpy.data.objects.get("corps_volume")
    if ob is None:
        raise RuntimeError("corps_volume absent : lancer corps_volume.py d'abord")
    return ob


def _bornes_skai():
    bas = lambda su: _hauteur_ceinture(su, COUDE_CAUDAL, -1.0) + CEINTURE_DEMI
    haut = lambda su: _hauteur_ceinture(su, COUDE_CRANIAL, +1.0) - CEINTURE_DEMI
    return bas, haut


def entailler_skai():
    """Creuse le logement du skai dans le corps."""
    # L'outil est bati depuis sa face exterieure et epaissi vers l'interieur,
    # meme convention que les pieces visibles. Construit en sens inverse, il
    # produisait un solide retourne qui vidait entierement le corps.
    bas, haut = _bornes_skai()
    outil = _geom.bande(
        "outil_entaille_skai", SU_BANDE_FIN, SU_SOMMET, bas, haut,
        lambda su, z: 3.0,
        epaisseur=PROFONDEUR_ENTAILLE + 3.0, pas_su=0.25, divisions=64,
        lisse=False,
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
    # Trois nappes dont la grille epouse les bords, au lieu d'une nappe decoupee
    # dans une grille horizontale : les bords obliques sortaient en escalier.
    marge = CEINTURE_DEMI
    bas = lambda su: _hauteur_ceinture(su, COUDE_CAUDAL, -1.0)
    haut = lambda su: _hauteur_ceinture(su, COUDE_CRANIAL, +1.0)

    morceaux = [
        ("armature_bande", SU_BANDE_DEBUT, SU_BANDE_FIN,
         lambda su: bas(su) - marge, lambda su: haut(su) + marge, 48),
        ("armature_ceinture_caudale", SU_BANDE_FIN, SU_SOMMET,
         lambda su: bas(su) - marge, lambda su: bas(su) + marge, 24),
        ("armature_ceinture_craniale", SU_BANDE_FIN, SU_SOMMET,
         lambda su: haut(su) - marge, lambda su: haut(su) + marge, 24),
    ]
    for nom, su0, su1, zb, zh, div in morceaux:
        ob = _geom.bande(nom, su0, su1, zb, zh, hauteur_armature,
                         epaisseur=2.5, pas_su=0.25, divisions=div)
        _geom.ranger(ob, "corps")

    outil = entailler_skai()

    bas_s, haut_s = _bornes_skai()
    skai = _geom.bande(
        "skai", SU_BANDE_FIN, SU_SOMMET, bas_s, haut_s,
        lambda su, z: -DEPRESSION_SKAI,
        epaisseur=0.5, pas_su=0.25, divisions=64,
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
