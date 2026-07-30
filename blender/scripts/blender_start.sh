#!/usr/bin/env bash
# Demarre Blender avec le serveur MCP actif sur le port 9876.
#
#   blender_start.sh            display virtuel (aucune fenetre a l'ecran)
#   blender_start.sh --visible  fenetre Blender sur l'ecran de l'utilisateur
#
# L'addon BlenderMCP demarre le serveur tout seul au chargement.
# Blender refuse de servir en mode --background : un display est obligatoire.
set -u

PROJET="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# On ouvre la scene du sous-projet actif, pas celle de la racine.
SCENE="$PROJET/blender/scene.blend"
if [ -f "$PROJET/objets/ACTIF" ]; then
  ACTIF="$(cat "$PROJET/objets/ACTIF")"
  [ -f "$PROJET/objets/$ACTIF/blender/scene.blend" ] &&
    SCENE="$PROJET/objets/$ACTIF/blender/scene.blend"
fi
LOG="$PROJET/blender/blender.log"
PIDFILE="$PROJET/blender/blender.pid"

# Un seul serveur peut tenir le port 9876. Si quelqu'un le tient deja - typiquement
# une fenetre Blender ouverte par l'utilisateur - on s'y raccroche au lieu de
# lancer une seconde instance qui echouerait a demarrer son serveur.
if python3 "$PROJET/blender/scripts/mcp.py" ping > /dev/null 2>&1; then
  echo "Serveur MCP deja actif sur 9876, instance existante reutilisee"
  exit 0
fi

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "Blender tourne deja (pid $(cat "$PIDFILE")) mais ne sert pas le port 9876"
  echo "Activer l'addon dans cette fenetre, ou l'arreter: blender/scripts/blender_stop.sh"
  exit 1
fi

if pgrep -x blender > /dev/null 2>&1; then
  echo "Une fenetre Blender est ouverte mais son serveur MCP n'est pas demarre."
  echo "Dans cette fenetre: Edit > Preferences > Add-ons > cocher BlenderMCP."
  exit 1
fi

ARGS=()
[ -f "$SCENE" ] && ARGS+=("$SCENE")

if [ "${1:-}" = "--visible" ]; then
  nohup blender "${ARGS[@]}" > "$LOG" 2>&1 &
else
  nohup xvfb-run -a blender "${ARGS[@]}" > "$LOG" 2>&1 &
fi
echo $! > "$PIDFILE"

for _ in $(seq 1 40); do
  if python3 "$PROJET/blender/scripts/mcp.py" ping > /dev/null 2>&1; then
    echo "Blender pret, serveur MCP sur 9876 (pid $(cat "$PIDFILE"))"
    exit 0
  fi
  sleep 1
done

echo "Blender n'a pas ouvert le port 9876 en 40 s. Voir $LOG"
exit 1
