# Journal technique

Interne. Vocabulaire 3D libre. Une entree par etape franchie ou par difficulte
resolue.

---

## 2026-07-29 — P0 Initialisation

**Fait**

- Arborescence de travail creee (voir CLAUDE.md section 4).
- Blender 3.4.1 detecte, `uv` et `xvfb-run` disponibles.
- Addon BlenderMCP v1.2 installe en `~/.config/blender/3.4/scripts/addons/blender_mcp_addon.py`,
  active de facon persistante par `addon_utils.enable(..., persistent=True)` puis
  `wm.save_userpref()`. Aucune manipulation d'interface requise : cette version de
  l'addon demarre son serveur socket a l'enregistrement.
- `blender-mcp` installe par `uv tool install`. Declare dans `.mcp.json` (portee
  projet). Sera charge au prochain demarrage de Claude Code, apres approbation.
- Client de secours `blender/scripts/mcp.py` : parle directement au port 9876,
  independant du serveur MCP. Verbes : ping, info, obj, exec, evalstdin, cmd, shot.
- Scripts de cycle de vie `blender_start.sh` / `blender_stop.sh`.
- `blender/scripts/vues_controle.py` : rendus des vues anatomiques normalisees,
  camera orthographique cadree sur la boite englobante, exclusion de la
  collection `outils`.
- `blender/scripts/eclairage_controle.py` : eclairage neutre trois points plus
  fond gris, entierement dimensionne sur la taille de l'objet.
- Six skills projet dans `.claude/skills/`, index semantique dans `SKILLS_INDEX.md`.

**Verifie**

- Aller-retour socket : `get_scene_info` repond.
- `execute_code` : execution et remontee du `print`.
- Rendu EEVEE sous `xvfb-run` : image correcte, non noire. C'est le point qui
  n'allait pas de soi — EEVEE demande un contexte OpenGL, un display virtuel
  suffit.
- `vues_controle.py` : quatre vues produites, cadrage automatique correct.
- `eclairage_controle.py` : calibration verifiee a deux echelles separees d'un
  facteur 5. La puissance de la source cle suit 9 W par metre carre de distance.
  Les valeurs que j'avais d'abord ecrites de memoire etaient fausses d'un facteur
  proche de 50 — d'ou la mesure.
- Chaine complete P12 vers P13 sur un objet test de 12 cm : construction,
  eclairage, rendu des vues anatomiques, exposition correcte, forme lisible.
- Pilotage visible : renommage et deplacement d'un objet observes en direct par
  l'utilisateur dans sa fenetre.

**Ce qui a resiste**

1. `blender --background` refuse de servir le MCP. L'addon le detecte et le dit
   explicitement : sans boucle d'evenements, les commandes ne s'executeraient
   jamais. Un display, meme virtuel, est obligatoire.
2. Conflit de port. Deux instances de test tenaient 9876 ; l'utilisateur essayait
   en parallele d'activer l'addon a la main dans sa propre fenetre, ce qui levait
   une trace Python et laissait la case decochee. Diagnostic par
   `ss -lptn 'sport = :9876'`.
3. Effet de bord non anticipe : Blender enregistre automatiquement les
   preferences, y compris apres un echec d'activation. La tentative manquee a
   donc **retire** l'addon du fichier de preferences que j'avais ecrit. Constate
   par `bpy.context.preferences.addons.keys()`, corrige par une reactivation en
   arriere-plan, aucune instance ne tournant.

**Decide**

- Une seule instance de Blender a la fois, lancee par `blender_start.sh`.
- L'utilisateur ne touche jamais aux preferences de l'addon.
- Mode `--visible` disponible quand l'utilisateur veut voir travailler.
- Les rendus d'iteration sont prefixes par numero d'iteration et conserves.

**Reste ouvert**

- Serveur MCP `blender` non encore charge dans la session Claude Code : necessite
  un redemarrage. Le client de secours couvre entre-temps.
- Integration PolyHaven non testee (reseau, non necessaire avant P12).
- Objet a scanner non encore fourni : P1 en attente des photos.
