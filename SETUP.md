# Installation et exploitation de la chaine Blender

Etat au 29 juillet 2026. Tout ce qui suit a ete installe et verifie sur cette
machine.

## Ce qui est en place

| Element | Etat |
|---|---|
| Blender | 3.4.1, `/usr/bin/blender` |
| Addon BlenderMCP | installe dans `~/.config/blender/3.4/scripts/addons/blender_mcp_addon.py`, active dans les preferences |
| Serveur MCP | `blender-mcp` installe par `uv tool install`, declare dans `.mcp.json` |
| Port de dialogue | 9876, ouvert automatiquement au lancement de Blender |
| Ecran virtuel | `xvfb-run`, permet de faire tourner Blender sans fenetre |
| Rendu EEVEE sans fenetre | verifie |

## Chaine de dialogue

```
Claude  --MCP stdio-->  blender-mcp  --socket 9876-->  addon dans Blender
```

Deux voies equivalentes pour piloter Blender :

- les outils `mcp__blender__*`, disponibles apres redemarrage de Claude Code et
  approbation du serveur declare dans `.mcp.json` ;
- `python3 blender/scripts/mcp.py ...`, qui parle au meme port sans passer par le
  serveur MCP. Toujours disponible, sert de secours et de diagnostic.

## Commandes

```bash
./blender/scripts/blender_start.sh            # ecran virtuel, aucune fenetre
./blender/scripts/blender_start.sh --visible  # fenetre a l'ecran
./blender/scripts/blender_stop.sh             # arret, sans sauvegarde
python3 blender/scripts/mcp.py ping           # la chaine repond-elle
python3 blender/scripts/mcp.py info           # contenu de la scene
```

`blender_start.sh` refuse de lancer une seconde instance si le port 9876 est deja
tenu : il se raccroche a l'instance existante.

## Regle fondamentale : une seule instance

Le port 9876 ne peut etre tenu que par un seul Blender. Une deuxieme instance
echoue a demarrer son serveur, et l'erreur remonte sous forme de trace Python.

C'est la cause du probleme rencontre le 29 juillet 2026 : une instance de test
tenait le port, l'activation manuelle de l'addon dans une seconde fenetre
echouait donc systematiquement. Aggravant : Blender enregistre automatiquement
les preferences, y compris apres un echec, ce qui a **desactive** l'addon dans le
fichier de preferences. Il a fallu le reactiver.

Consequence pratique : ne jamais activer ou desactiver l'addon a la main dans les
preferences. Il est deja actif et demarre son serveur tout seul.

## Reactiver l'addon si necessaire

A executer uniquement quand aucun Blender ne tourne.

```bash
./blender/scripts/blender_stop.sh
blender --background --python-expr "
import bpy, addon_utils
addon_utils.enable('blender_mcp_addon', default_set=True, persistent=True)
bpy.ops.wm.save_userpref()
print([k for k in bpy.context.preferences.addons.keys() if 'mcp' in k])
"
```

## Diagnostic

| Symptome | Cause probable | Action |
|---|---|---|
| `Connection refused` sur 9876 | aucun Blender lance | `blender_start.sh` |
| Blender tourne mais port ferme | addon desactive dans les preferences | procedure de reactivation ci-dessus |
| Trace Python en cochant l'addon | port deja tenu par une autre instance | fermer l'autre instance ; ne pas cocher a la main |
| Onglet `BlenderMCP` absent du panneau `N` | addon non charge dans cette fenetre | relancer par `blender_start.sh` |
| Le MCP se tait en pleine session | un operateur de reinitialisation de fichier a ete appele | relancer Blender ; ne jamais appeler `wm.read_homefile` ni `wm.read_factory_settings` |

## Integrations facultatives de l'addon

Desactivees par defaut, activables par scene :

- **PolyHaven** — bibliotheque libre d'environnements lumineux et de textures PBR.
  Utile pour les matieres et la livraison. Reseau requis.
- **Hyper3D Rodin, Hunyuan3D, Sketchfab** — generation ou telechargement de
  modeles 3D. Sans emploi ici : le projet reconstruit l'objet, il ne le
  telecharge pas.

## Verification complete

```bash
./blender/scripts/blender_start.sh
python3 blender/scripts/mcp.py ping
python3 blender/scripts/mcp.py exec blender/scripts/vues_controle.py
ls -l blender/renders/
```

Quatre images doivent apparaitre dans `blender/renders/`.
