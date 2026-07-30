"""Pipeau, element asymetrique : slider du flanc droit.

Piece claire allongee a stries transversales fines, logee dans la bordure de
peinture rouge qui court entre l'arete du biseau ventro-lateral et la piece
d'armature creme. Relevee sur la planche p03, confirmee par l'utilisateur.

Elle n'existe que sur le flanc droit : c'est la seule rupture de symetrie
bilaterale du corps.
"""

import importlib
import sys

import bpy

DOSSIER = "/home/m/projet/blender/objets/pipeau/blender/scripts"
if DOSSIER not in sys.path:
    sys.path.insert(0, DOSSIER)
import _geom
importlib.reload(_geom)

# La bordure rouge est definie dans armature_skai.py. On la recopie plutot que
# d'importer ce module, dont le chargement relancerait toute sa construction.
BORDURE_ROUGE = 6.0

MM = _geom.MM

# --- parametres, releves sur p03 --------------------------------------------

Z_CENTRE = 48.0            # position craniocaudale du milieu du slider
HAUTEUR = 16.0             # etendue craniocaudale
LARGEUR = 4.0              # etendue curviligne
SAILLIE = 0.9              # au dessus de la bordure rouge
LOGEMENT = 0.5             # profondeur de la gorge qui le recoit

STRIES = 11
STRIE_LARGEUR = 0.45
STRIE_PROFONDEUR = 0.25

SU_CENTRE = _geom.reperes()["biseau"] + BORDURE_ROUGE / 2.0
SU_MIN = SU_CENTRE - LARGEUR / 2.0
SU_MAX = SU_CENTRE + LARGEUR / 2.0
Z_MIN = Z_CENTRE - HAUTEUR / 2.0
Z_MAX = Z_CENTRE + HAUTEUR / 2.0


def region_slider(su, z):
    return SU_MIN <= su <= SU_MAX and Z_MIN <= z <= Z_MAX


def region_logement(su, z):
    marge = 0.4
    return (SU_MIN - marge <= su <= SU_MAX + marge
            and Z_MIN - marge <= z <= Z_MAX + marge)


def region_stries(su, z):
    if not region_slider(su, z):
        return False
    pas = (HAUTEUR - 2.0) / float(STRIES)
    rang = (z - (Z_MIN + 1.0)) / pas
    if rang < 0.0 or rang > STRIES:
        return False
    return (rang - int(rang)) * pas <= STRIE_LARGEUR


def main():
    corps = bpy.data.objects.get("corps_volume")
    if corps is None:
        raise RuntimeError("corps_volume absent")

    # gorge recevant le slider, creusee dans le corps
    outil = _geom.nappe(
        "outil_logement_slider", region_logement,
        decalage=-LOGEMENT, epaisseur=LOGEMENT + 3.0,
        vers_exterieur=True, lisse=False, pas_z=0.2, cotes=(1,),
    )
    outil.display_type = "WIRE"
    outil.hide_render = True
    _geom.ranger(outil, "outils")

    for m in list(corps.modifiers):
        if m.name == "logement_slider":
            corps.modifiers.remove(m)
    m = corps.modifiers.new("logement_slider", "BOOLEAN")
    m.operation = "DIFFERENCE"
    m.object = outil
    m.solver = "EXACT"

    # le slider lui-meme, en saillie sur la bordure rouge
    slider = _geom.nappe(
        "slider", region_slider,
        decalage=-LOGEMENT, epaisseur=LOGEMENT + SAILLIE,
        vers_exterieur=True, pas_z=0.1, cotes=(1,),
    )
    _geom.ranger(slider, "corps")

    # stries transversales, creusees en relief negatif sur sa face libre
    stries = _geom.nappe(
        "stries_slider", region_stries,
        decalage=SAILLIE - STRIE_PROFONDEUR, epaisseur=STRIE_PROFONDEUR,
        vers_exterieur=False, pas_z=0.1, cotes=(1,),
    )
    if stries:
        _geom.ranger(stries, "corps")

    print("slider: su %.2f a %.2f, z %.1f a %.1f, flanc droit seul"
          % (SU_MIN, SU_MAX, Z_MIN, Z_MAX))


main()
