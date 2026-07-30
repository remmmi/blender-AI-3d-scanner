"""Pipeau : couleurs, matieres et finitions.

Une matiere par zone decrite comme homogene dans la description anatomique.
Les valeurs suivent le bareme de la skill blender-materiaux, ajuste a la lecture
des planches. Aucune couleur n'est un noir ou un blanc pur.

Script relancable : les materiaux existants sont reconfigures, non dupliques.
"""

import bpy

# --- definitions ------------------------------------------------------------
# nom : (couleur lineaire, rugosite, metallique, transmission)

# Revise en P15. Sur l'objet, peinture rouge, skai lateral et revetement dorsal
# ont la meme clarte : seule la finition les distingue. La premiere passe les
# separait par la teinte, ce qui est une erreur de nature. Les rouges etaient en
# outre desatures, canal vert environ treize fois trop haut.
MATIERES = {
    "rouge_peint":   ((0.420, 0.014, 0.012), 0.14, 0.0, 0.0),
    "creme":         ((0.870, 0.830, 0.735), 0.40, 0.0, 0.0),
    "skai_rouge":    ((0.420, 0.016, 0.016), 0.74, 0.0, 0.0),
    "fil_surpiqure": ((0.190, 0.012, 0.012), 0.85, 0.0, 0.0),
    "noir_panneau":  ((0.008, 0.008, 0.010), 0.70, 0.0, 0.0),
    "blanc_bouton":  ((0.830, 0.825, 0.805), 0.34, 0.0, 0.0),
    "acier":         ((0.760, 0.765, 0.780), 0.26, 1.0, 0.0),
    "verre":         ((0.960, 0.960, 0.960), 0.04, 0.0, 1.0),
    "embout_noir":   ((0.014, 0.014, 0.016), 0.05, 0.0, 0.0),
    "silicone_rouge":((0.330, 0.020, 0.018), 0.52, 0.0, 0.0),
    "alu_brut":      ((0.700, 0.702, 0.706), 0.38, 1.0, 0.0),
}

# --- affectation ------------------------------------------------------------

AFFECTATION = {
    "corps_volume": "rouge_peint",
    "armature_bande": "creme",
    "armature_ceinture_caudale": "creme",
    "armature_ceinture_craniale": "creme",
    "skai": "skai_rouge",
    "surpiqures": "fil_surpiqure",
    "panneau_ventral": "noir_panneau",
    "bouton_feu": "blanc_bouton",
    "bouton_reglage": "blanc_bouton",
    "volet_caudal": "creme",
    "cheminee": "acier",
    "silicone_cranial": "silicone_rouge",
    "silicone_biseau": "silicone_rouge",
    "plaque_alu": "alu_brut",
    "slider": "creme",
    "stries_slider": "creme",
    "embase": "acier",
    "bague_air": "acier",
    "capuchon": "acier",
    "collerette": "acier",
    "cylindre_transparent": "verre",
    "embout": "embout_noir",
}

GRAIN_SKAI = 0.0009      # amplitude du grain du skai, en metres
NID_ABEILLE = 420.0      # densite de la marbrure en nid d'abeille de l'embout


def materiau(nom):
    couleur, rugosite, metal, transmission = MATIERES[nom]
    mat = bpy.data.materials.get(nom) or bpy.data.materials.new(nom)
    mat.use_nodes = True
    arbre = mat.node_tree
    for n in list(arbre.nodes):
        if n.type not in {"BSDF_PRINCIPLED", "OUTPUT_MATERIAL"}:
            arbre.nodes.remove(n)
    bsdf = arbre.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*couleur, 1.0)
    bsdf.inputs["Roughness"].default_value = rugosite
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Transmission"].default_value = transmission
    if transmission > 0.0:
        bsdf.inputs["IOR"].default_value = 1.50
        mat.use_screen_refraction = True
        mat.blend_method = "HASHED"
        mat.show_transparent_back = False
    return mat, arbre, bsdf


def grain(mat, arbre, bsdf, echelle, force):
    """Relief fin, sans geometrie : le grain du skai."""
    bruit = arbre.nodes.new("ShaderNodeTexNoise")
    bruit.inputs["Scale"].default_value = echelle
    bruit.inputs["Detail"].default_value = 6.0
    relief = arbre.nodes.new("ShaderNodeBump")
    relief.inputs["Strength"].default_value = force
    relief.inputs["Distance"].default_value = GRAIN_SKAI
    arbre.links.new(bruit.outputs["Fac"], relief.inputs["Height"])
    arbre.links.new(relief.outputs["Normal"], bsdf.inputs["Normal"])


def nid_abeille(mat, arbre, bsdf):
    """Marbrure en nid d'abeille de l'embout.

    C'est un motif de COULEUR, non un relief : la surface est parfaitement lisse
    et brillante. La premiere passe la traitait en relief, ce qui donnait un
    facettage grossier absent de l'objet.
    """
    coord = arbre.nodes.new("ShaderNodeTexCoord")
    cellules = arbre.nodes.new("ShaderNodeTexVoronoi")
    cellules.feature = "F1"
    cellules.inputs["Scale"].default_value = NID_ABEILLE
    joints = arbre.nodes.new("ShaderNodeTexVoronoi")
    joints.feature = "DISTANCE_TO_EDGE"
    joints.inputs["Scale"].default_value = NID_ABEILLE
    rampe = arbre.nodes.new("ShaderNodeValToRGB")
    rampe.color_ramp.elements[0].position = 0.0
    rampe.color_ramp.elements[0].color = (0.055, 0.055, 0.060, 1.0)
    rampe.color_ramp.elements[1].position = 0.20
    rampe.color_ramp.elements[1].color = (0.010, 0.010, 0.012, 1.0)
    # la couleur de cellule de Voronoi est aleatoire et saturee : on la ramene en
    # niveaux de gris avant de la faire jouer, sinon la marbrure part en couleurs
    gris = arbre.nodes.new("ShaderNodeRGBToBW")
    tons = arbre.nodes.new("ShaderNodeValToRGB")
    tons.color_ramp.elements[0].position = 0.15
    tons.color_ramp.elements[0].color = (0.006, 0.006, 0.008, 1.0)
    tons.color_ramp.elements[1].position = 0.85
    tons.color_ramp.elements[1].color = (0.048, 0.046, 0.052, 1.0)
    melange = arbre.nodes.new("ShaderNodeMixRGB")
    melange.blend_type = "MULTIPLY"
    melange.inputs["Fac"].default_value = 0.55
    arbre.links.new(coord.outputs["Object"], cellules.inputs["Vector"])
    arbre.links.new(coord.outputs["Object"], joints.inputs["Vector"])
    arbre.links.new(cellules.outputs["Color"], gris.inputs["Color"])
    arbre.links.new(gris.outputs["Val"], tons.inputs["Fac"])
    arbre.links.new(joints.outputs["Distance"], rampe.inputs["Fac"])
    arbre.links.new(tons.outputs["Color"], melange.inputs["Color1"])
    arbre.links.new(rampe.outputs["Color"], melange.inputs["Color2"])
    arbre.links.new(melange.outputs["Color"], bsdf.inputs["Base Color"])


def main():
    construits = {}
    for nom in MATIERES:
        mat, arbre, bsdf = materiau(nom)
        if nom == "skai_rouge":
            grain(mat, arbre, bsdf, echelle=1400.0, force=0.75)
        if nom == "embout_noir":
            nid_abeille(mat, arbre, bsdf)
        if nom == "acier":
            grain(mat, arbre, bsdf, echelle=1600.0, force=0.06)
        if nom == "alu_brut":
            grain(mat, arbre, bsdf, echelle=2600.0, force=0.18)
        construits[nom] = mat

    manquants = []
    for objet, matiere in AFFECTATION.items():
        ob = bpy.data.objects.get(objet)
        if ob is None:
            manquants.append(objet)
            continue
        ob.data.materials.clear()
        ob.data.materials.append(construits[matiere])

    sc = bpy.context.scene
    sc.eevee.use_ssr = True
    sc.eevee.use_ssr_refraction = True

    print("%d matieres, %d objets habilles" % (len(construits), len(AFFECTATION) - len(manquants)))
    if manquants:
        print("objets absents:", ", ".join(manquants))


main()
