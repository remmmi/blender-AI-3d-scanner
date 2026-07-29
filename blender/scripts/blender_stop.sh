#!/usr/bin/env bash
# Arrete Blender proprement. La scene N'EST PAS sauvegardee automatiquement :
# sauvegarder avant via le MCP (bpy.ops.wm.save_as_mainfile).
set -u

PROJET="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PIDFILE="$PROJET/blender/blender.pid"

if [ -f "$PIDFILE" ]; then
  PID="$(cat "$PIDFILE")"
  kill "$PID" 2>/dev/null && echo "Blender arrete (pid $PID)"
  rm -f "$PIDFILE"
fi

pkill -f "xvfb-run -a blender" 2>/dev/null
pkill -x blender 2>/dev/null
exit 0
