# blender-AI-3d-scanner

Scanner 3D par référence photographique

Reconstruction d'un objet réel en modèle 3D Blender à partir de photographies,
via une description anatomique textuelle servant de contrat de spécification.

Ce n'est pas de la photogrammétrie automatique : c'est une reconstruction
raisonnée, donc contrôlable, éditable et discutable point par point.

## Documents

| Fichier | Contenu |
|---|---|
| `CLAUDE.md` | méthode, langage imposé, pipeline en 18 étapes, conventions |
| `SETUP.md` | installation de la chaîne Blender, commandes, diagnostic |
| `SKILLS_INDEX.md` | index sémantique des skills Blender du projet |
| `JOURNAL.md` | journal technique interne |
| `LESSONS.md` | capitalisation |

## Démarrage

```bash
./blender/scripts/blender_start.sh     # Blender + serveur, sans fenêtre
python3 blender/scripts/mcp.py ping    # vérifier la chaîne
```

Ajouter `--visible` pour ouvrir une fenêtre Blender à l'écran.

## Où va quoi

```
photos/source/          photos d'origine, jamais modifiées
photos/work/            versions redimensionnées, seules exploitées
descriptions/           descriptions anatomiques, incertitudes, dimensions
blender/scripts/        scripts de construction et outils
blender/renders/        rendus de contrôle
blender/exports/        fichiers exportés
livraison/              paquet final
```

## État

Chaîne Blender installée et vérifiée. Premier objet en cours : `objets/pipeau`,
une cigarette électronique. Description anatomique validée, volume du corps
construit, itération en cours sur la section transversale.

## Licence

MIT, voir `LICENSE`.
