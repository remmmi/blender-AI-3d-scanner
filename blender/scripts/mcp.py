#!/usr/bin/env python3
"""Client minimal du serveur socket BlenderMCP (port 9876).

Sert de secours et d'outil de diagnostic quand le serveur MCP cote Claude Code
n'est pas charge, et de brique commune aux skills du projet.

Usage:
  mcp.py ping                       teste la connexion
  mcp.py info                       resume de la scene
  mcp.py obj NOM                    detail d'un objet
  mcp.py exec FICHIER.py            execute un script python dans Blender
  mcp.py evalstdin                  execute le python lu sur stdin
  mcp.py cmd TYPE [JSON_PARAMS]     commande brute
  mcp.py shot SORTIE.png [TAILLE]   capture du viewport
"""

import json
import socket
import sys

HOST = "localhost"
PORT = 9876
TIMEOUT = 600


def call(cmd_type, params=None):
    sock = socket.create_connection((HOST, PORT), timeout=TIMEOUT)
    sock.settimeout(TIMEOUT)
    try:
        sock.sendall(json.dumps({"type": cmd_type, "params": params or {}}).encode())
        buf = b""
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            buf += chunk
            try:
                return json.loads(buf.decode())
            except json.JSONDecodeError:
                continue
    finally:
        sock.close()
    raise RuntimeError("reponse incomplete du serveur Blender")


def main(argv):
    if not argv:
        print(__doc__)
        return 2

    verb = argv[0]

    try:
        if verb == "ping":
            call("get_scene_info")
            print("OK serveur Blender joignable sur %s:%d" % (HOST, PORT))
            return 0
        if verb == "info":
            res = call("get_scene_info")
        elif verb == "obj":
            res = call("get_object_info", {"name": argv[1]})
        elif verb == "exec":
            with open(argv[1], "r", encoding="utf-8") as fh:
                res = call("execute_code", {"code": fh.read()})
        elif verb == "evalstdin":
            res = call("execute_code", {"code": sys.stdin.read()})
        elif verb == "cmd":
            params = json.loads(argv[2]) if len(argv) > 2 else {}
            res = call(argv[1], params)
        elif verb == "shot":
            out = argv[1]
            size = int(argv[2]) if len(argv) > 2 else 1200
            res = call("get_viewport_screenshot", {"max_size": size, "filepath": out})
        else:
            print("verbe inconnu: %s" % verb)
            return 2
    except (OSError, socket.timeout) as err:
        print("ECHEC connexion Blender: %s" % err)
        print("Lancer Blender: blender/scripts/blender_start.sh")
        return 1

    print(json.dumps(res, indent=1, ensure_ascii=False))
    return 0 if res.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
