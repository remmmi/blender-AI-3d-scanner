"""Pipeau, briques geometriques partagees.

Definit une fois pour toutes la section transversale du corps, et fournit un
constructeur de nappe : une surface epousant le flanc du corps, restreinte a une
region decrite dans les coordonnees (su, z).

Coordonnees de travail, en millimetres :
  su  distance curviligne le long de la section, mesuree depuis le milieu de la
      face ventrale. Symetrique : su vaut la meme chose a droite et a gauche.
      0 au milieu ventral, maximum au sommet dorsal.
  z   hauteur craniocaudale, 0 a la face caudale.

Toutes les fonctions rendent des millimetres. La conversion en metres se fait a
la construction du maillage.
"""

import math

import bmesh
import bpy

MM = 0.001

# --- cotes de la section ----------------------------------------------------

# Les cotes de l'utilisateur portent sur l'objet fini, renflement de la piece
# creme et saillie des boutons compris. Le corps nu est donc plus fin :
#   medio-lateral   27 = 24 (corps nu) + 1.5 d'armature de chaque cote
#   ventro-dorsal   55 = 51.5 (corps nu) + 1.5 d'armature + 2 de bouton
DEMI_VENTRALE = 10.5
LARGEUR_BISEAU = 10.0
GAIN_X_BISEAU = 1.5
DEMI_MAX = 12.0
FLANC_FIN = 43.0        # dome dorsal de 8.5 mm : l'objet pose sur le dos tient a plat
SOMMET = 51.5
RAYON_VENTRAL = 1.0
RAYON_DORSAL = 2.0
EXPOSANT_OGIVE = 3.0
PAS_OGIVE = 24
PAS_CONGE = 6

HAUTEUR = 90.0


def _bezier(p0, p1, p2, n):
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
    """Section pour X >= 0, du milieu ventral au sommet dorsal."""
    gain_y = math.sqrt(LARGEUR_BISEAU ** 2 - GAIN_X_BISEAU ** 2)
    dir_biseau = (GAIN_X_BISEAU / LARGEUR_BISEAU, gain_y / LARGEUR_BISEAU)

    coin_ventral = (DEMI_VENTRALE, 0.0)
    coin_dorsal = (DEMI_MAX, gain_y)

    dev_v = math.acos(dir_biseau[0])
    ret_v = RAYON_VENTRAL * math.tan(dev_v / 2.0)
    dev_d = math.acos(dir_biseau[1])
    ret_d = RAYON_DORSAL * math.tan(dev_d / 2.0)

    pts = [(0.0, 0.0), (coin_ventral[0] - ret_v, 0.0)]
    pts += _bezier(
        (coin_ventral[0] - ret_v, 0.0),
        coin_ventral,
        (coin_ventral[0] + ret_v * dir_biseau[0], ret_v * dir_biseau[1]),
        PAS_CONGE,
    )
    pts.append((coin_ventral[0] + ret_v * dir_biseau[0], ret_v * dir_biseau[1]))
    pts.append((coin_dorsal[0] - ret_d * dir_biseau[0], coin_dorsal[1] - ret_d * dir_biseau[1]))
    pts += _bezier(
        (coin_dorsal[0] - ret_d * dir_biseau[0], coin_dorsal[1] - ret_d * dir_biseau[1]),
        coin_dorsal,
        (DEMI_MAX, coin_dorsal[1] + ret_d),
        PAS_CONGE,
    )
    pts.append((DEMI_MAX, coin_dorsal[1] + ret_d))
    pts.append((DEMI_MAX, FLANC_FIN))

    a, b = DEMI_MAX, SOMMET - FLANC_FIN
    n = EXPOSANT_OGIVE
    for i in range(1, PAS_OGIVE + 1):
        t = i / float(PAS_OGIVE)
        pts.append((a * (1.0 - t ** n) ** (1.0 / n), FLANC_FIN + b * t))
    return pts


def section_fermee():
    demi = profil_demi()
    gauche = [(-x, y) for (x, y) in reversed(demi[1:-1])]
    return demi + gauche


def _abscisses(demi):
    """Distance curviligne cumulee le long de la demi-section."""
    s = [0.0]
    for i in range(1, len(demi)):
        dx = demi[i][0] - demi[i - 1][0]
        dy = demi[i][1] - demi[i - 1][1]
        s.append(s[-1] + math.hypot(dx, dy))
    return s


def _normales(demi):
    """Normale exterieure en chaque point de la demi-section."""
    n = []
    for i in range(len(demi)):
        j0 = max(i - 1, 0)
        j1 = min(i + 1, len(demi) - 1)
        tx = demi[j1][0] - demi[j0][0]
        ty = demi[j1][1] - demi[j0][1]
        norme = math.hypot(tx, ty) or 1.0
        # rotation de -90 degres : pointe vers l'exterieur pour ce sens de parcours
        n.append((ty / norme, -tx / norme))
    # le point du sommet dorsal doit pointer vers le dorsal
    n[-1] = (0.0, 1.0)
    n[0] = (0.0, -1.0)
    return n


def reechantillonner(demi, pas=0.4):
    """Redistribue les points a pas curviligne constant.

    Indispensable : les portions rectilignes de la section ne sont decrites que
    par deux points. Sans cette etape, aucune limite de region ne peut tomber au
    milieu d'un flanc plan, et les nappes sortent tronquees ou vides.
    """
    s = _abscisses(demi)
    total = s[-1]
    n = max(int(round(total / pas)), 2)
    sortie = []
    j = 0
    for i in range(n + 1):
        cible = total * i / float(n)
        while j < len(s) - 2 and s[j + 1] < cible:
            j += 1
        portee = s[j + 1] - s[j]
        t = 0.0 if portee <= 0 else (cible - s[j]) / portee
        sortie.append((
            demi[j][0] + t * (demi[j + 1][0] - demi[j][0]),
            demi[j][1] + t * (demi[j + 1][1] - demi[j][1]),
        ))
    return sortie


PAS_CURVILIGNE = 0.4

DEMI = reechantillonner(profil_demi(), PAS_CURVILIGNE)
ABSCISSES = _abscisses(DEMI)
NORMALES = _normales(DEMI)
SU_MAX = ABSCISSES[-1]


def reperes():
    """Abscisses curvilignes des limites remarquables de la section."""
    gain_y = math.sqrt(LARGEUR_BISEAU ** 2 - GAIN_X_BISEAU ** 2)
    su_ventrale = su_de_y(0.0, DEMI_VENTRALE)
    su_biseau = su_de_y(gain_y, DEMI_MAX)
    su_flanc = su_de_y(FLANC_FIN, DEMI_MAX)
    return {
        "ventrale": su_ventrale,
        "biseau": su_biseau,
        "flanc": su_flanc,
        "sommet": SU_MAX,
    }


def su_de_y(y, x):
    """Abscisse curviligne du point de la demi-section le plus proche de (x, y)."""
    meilleur, dmin = 0.0, None
    for i, (px, py) in enumerate(DEMI):
        d = math.hypot(px - x, py - y)
        if dmin is None or d < dmin:
            dmin, meilleur = d, ABSCISSES[i]
    return meilleur


def x_de_su(su):
    """Abscisse medio-laterale du point de la section a l'abscisse curviligne su."""
    for i in range(len(ABSCISSES) - 1):
        if ABSCISSES[i] <= su <= ABSCISSES[i + 1]:
            portee = ABSCISSES[i + 1] - ABSCISSES[i]
            t = 0.0 if portee <= 0 else (su - ABSCISSES[i]) / portee
            return DEMI[i][0] + t * (DEMI[i + 1][0] - DEMI[i][0])
    return DEMI[-1][0] if su > ABSCISSES[-1] else DEMI[0][0]


def y_de_su(su):
    """Position ventro-dorsale du point de la section a l'abscisse curviligne su."""
    for i in range(len(ABSCISSES) - 1):
        if ABSCISSES[i] <= su <= ABSCISSES[i + 1]:
            portee = ABSCISSES[i + 1] - ABSCISSES[i]
            t = 0.0 if portee <= 0 else (su - ABSCISSES[i]) / portee
            return DEMI[i][1] + t * (DEMI[i + 1][1] - DEMI[i][1])
    return DEMI[-1][1] if su > ABSCISSES[-1] else DEMI[0][1]


def nappe(nom, region, decalage=0.0, epaisseur=1.5, vers_exterieur=True,
          pas_z=0.5, lisse=True, cotes=(1, -1)):
    """Construit une nappe epousant le flanc, restreinte a region(su, z).

    region  fonction (su, z) -> bool, su etant l'abscisse symetrique
    decalage  deport radial de la surface de reference, en millimetres. Peut etre
              un nombre, ou une fonction (su, z) -> millimetres, ce qui permet de
              donner a une piece rapportee un profil en travers.
    epaisseur  epaisseur donnee par le modificateur SOLIDIFY
    """
    old = bpy.data.objects.get(nom)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)

    nz = int(round(HAUTEUR / pas_z)) + 1
    zs = [i * HAUTEUR / (nz - 1) for i in range(nz)]

    # demi-section a droite puis symetrique a gauche, avec su commun
    bm = bmesh.new()
    total = 0

    for cote in cotes:
        variable = callable(decalage)
        grille = {}
        for i, (x, y) in enumerate(DEMI):
            su = ABSCISSES[i]
            nx, ny = NORMALES[i]
            for j, z in enumerate(zs):
                d = decalage(su, z) if variable else decalage
                grille[(i, j)] = ((x + nx * d) * cote, y + ny * d, z, su)

        for i in range(len(DEMI) - 1):
            for j in range(nz - 1):
                su_c = 0.5 * (ABSCISSES[i] + ABSCISSES[i + 1])
                z_c = 0.5 * (zs[j] + zs[j + 1])
                if not region(su_c, z_c):
                    continue
                quad = [grille[(i, j)], grille[(i + 1, j)],
                        grille[(i + 1, j + 1)], grille[(i, j + 1)]]
                if cote < 0:
                    quad = list(reversed(quad))
                vs = [bm.verts.new((p[0] * MM, p[1] * MM, p[2] * MM)) for p in quad]
                bm.faces.new(vs)
                total += 1

    if total == 0:
        bm.free()
        print("ATTENTION: nappe %s vide" % nom)
        return None

    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

    mesh = bpy.data.meshes.new(nom)
    bm.to_mesh(mesh)
    bm.free()

    ob = bpy.data.objects.new(nom, mesh)
    bpy.context.scene.collection.objects.link(ob)

    m = ob.modifiers.new("epaisseur", "SOLIDIFY")
    m.thickness = epaisseur * MM
    m.offset = 1.0 if vers_exterieur else -1.0

    if lisse:
        for f in mesh.polygons:
            f.use_smooth = True
        mesh.use_auto_smooth = True
        mesh.auto_smooth_angle = math.radians(25.0)

    print("nappe %-18s %5d faces" % (nom, total))
    return ob


def collection(nom):
    col = bpy.data.collections.get(nom)
    if col is None:
        col = bpy.data.collections.new(nom)
        bpy.context.scene.collection.children.link(col)
    return col


def ranger(ob, nom_collection):
    col = collection(nom_collection)
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)
