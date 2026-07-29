---
name: blender-session
description: Ouvrir, verifier, sauvegarder et fermer la session Blender, et executer du code dans Blender par le MCP. TRIGGER des que je dois toucher a Blender pour la premiere fois d'un tour, que le MCP ne repond plus, que je veux sauvegarder la scene, vider la scene, ou que je vois une erreur de connexion port 9876. A lire avant toute autre skill blender-*.
---

# Session Blender

Socle de toutes les autres skills `blender-*`. Rien ne part sans une session verifiee.

## Etat de la chaine

```
Claude  --MCP stdio-->  blender-mcp (uvx)  --socket 9876-->  addon dans Blender
```

Deux voies pour parler a Blender, equivalentes :
- outils MCP `mcp__blender__*` si le serveur MCP est charge dans la session ;
- secours direct : `python3 blender/scripts/mcp.py ...` (toujours disponible).

## Verification d'entree

```bash
python3 blender/scripts/mcp.py ping
```

- OK : continuer.
- Echec : `./blender/scripts/blender_start.sh` puis re-ping.
- Toujours echec : lire `blender/blender.log`.

Blender tourne par defaut sur un display virtuel : aucune fenetre a l'ecran de
l'utilisateur. `blender_start.sh --visible` ouvre une vraie fenetre si
l'utilisateur veut regarder.

## Garde-fous, non negociables

1. **Jamais de reinitialisation de fichier depuis le MCP.**
   `bpy.ops.wm.read_factory_settings`, `wm.read_homefile`, `wm.open_mainfile`
   detruisent le contexte et coupent le serveur socket. Pour vider la scene :

   ```python
   import bpy
   for ob in list(bpy.data.objects):
       bpy.data.objects.remove(ob, do_unlink=True)
   ```

2. **Petits scripts idempotents.** Une longue passe qui casse au milieu laisse
   une scene hybride, plus difficile a diagnostiquer qu'a reconstruire. Un script
   par element, relancable sans doublon (supprimer l'objet homonyme avant de le
   recreer).

3. **Sauvegarder apres chaque element termine.**

   ```python
   import bpy
   bpy.ops.wm.save_as_mainfile(filepath='/home/m/projet/blender/blender/scene.blend')
   ```

4. **Toujours verifier apres coup.** `mcp.py info` ou `mcp.py obj NOM` — le
   retour de `execute_code` ne prouve que l'absence d'exception, pas le resultat.

## Executer du code

Script long : ecrire un fichier dans `blender/scripts/`, puis

```bash
python3 blender/scripts/mcp.py exec blender/scripts/mon_script.py
```

Le `print()` du script remonte dans la reponse — s'en servir pour renvoyer des
mesures (nombre de faces, dimensions, bounding box) plutot que de supposer.

Fragment court :

```bash
echo 'import bpy; print([o.name for o in bpy.data.objects])' | python3 blender/scripts/mcp.py evalstdin
```

## Version

Blender 3.4.1. Consequences a retenir :
- moteur EEVEE = `'BLENDER_EEVEE'` (et non `BLENDER_EEVEE_NEXT`, qui est 4.2+) ;
- noms d'entrees du Principled BSDF de la generation 3.x : `Base Color`,
  `Metallic`, `Roughness`, `Specular`, `Transmission`, `IOR`, `Alpha` ;
- lissage par angle via `mesh.use_auto_smooth` (supprime en 4.1+).

En cas de doute sur une API, tester le fragment avant de l'integrer.

## Fin de session

Sauvegarder, puis `./blender/scripts/blender_stop.sh`. Le script ne sauvegarde
rien tout seul.

## Journal

Toute difficulte technique resolue va dans `JOURNAL.md`, tout enseignement
reutilisable dans `LESSONS.md`.
