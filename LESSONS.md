# Lessons learned

Capitalisation continue (P18). Une lecon = un fait verifie + ce qu'on en fait.

## Blender et MCP

- **Le mode arriere-plan ne sert pas le MCP.** `blender --background` n'a pas de
  boucle d'evenements ; l'addon refuse d'ouvrir le port. Un display virtuel
  (`xvfb-run`) suffit et fait tourner Blender sans fenetre.
- **EEVEE rend correctement sous ecran virtuel.** Pas besoin de Cycles ni de
  fenetre visible pour les rendus de controle.
- **Un seul Blender a la fois.** Le port 9876 n'accepte qu'un serveur. Une
  deuxieme instance leve une trace Python a l'activation de l'addon. Diagnostic :
  `ss -lptn 'sport = :9876'`.
- **Blender enregistre ses preferences automatiquement, meme apres un echec.**
  Une activation d'addon qui echoue peut donc desactiver durablement un addon
  precedemment active. Verifier avec
  `bpy.context.preferences.addons.keys()` plutot que se fier a l'installation.
- **Ne jamais reinitialiser le fichier depuis le MCP.** `wm.read_homefile` et
  `wm.read_factory_settings` coupent le serveur. Vider la scene objet par objet.
- **`execute_code` ne prouve rien.** Absence d'exception n'est pas resultat
  correct. Terminer chaque script par un `print` de mesures et relire la scene.
- **Les seuils par defaut de Blender sont en metres, donc enormes a l'echelle
  d'un objet de poche.** Le `merge_threshold` du modificateur SCREW vaut 0.01 m,
  soit 10 mm : il a fait disparaitre entierement une piece de 3.6 mm de rayon,
  sans lever d'erreur, en rendant simplement zero face. Verifier le nombre de
  faces de l'objet evalue apres tout modificateur, jamais seulement l'absence
  d'exception.
- **Une revolution sur profil ferme ne produit rien.** SCREW attend une chaine
  d'aretes ouverte.
- **Deux surfaces strictement coplanaires perdent l'arbitrage d'affichage.**
  Decaler la piece rapportee de quelques centiemes de millimetre suffit.
- **Une grille reguliere decoupee produit des bords en escalier.** Toute piece
  dont le bord est oblique par rapport a la grille sort crenelee. La parade n'est
  pas de raffiner la grille mais de la faire epouser les bords : echantillonner
  entre les deux limites de la piece plutot que decouper dans un quadrillage.
- **SOLIDIFY : batir toujours depuis la face exterieure et epaissir vers
  l'interieur.** Construite en sens inverse, la piece produit un solide retourne.
  Une decoupe booleenne avec un tel solide ne leve aucune erreur : elle vide
  entierement l'objet cible.
- **Ne jamais ecrire de valeur physique de memoire.** Les puissances d'eclairage
  posees d'intuition etaient fausses d'un facteur proche de 50. Une source suit
  le carre de sa distance : toute valeur trouvee ailleurs doit etre rapportee a
  la distance avant reemploi. Mesurer, puis ecrire.

## Interaction avec l'utilisateur

- **L'utilisateur ne debogue pas Blender.** Toute manipulation d'interface qu'on
  lui demande est un point de rupture. Preferer systematiquement une voie
  programmatique, meme plus longue a mettre en place.
- **Quand il signale une anomalie, chercher d'abord ce que j'ai fait.** Le
  conflit de port du 29 juillet venait de mes propres instances de test, pas de
  son installation.
- **Une preuve visible vaut mieux qu'une affirmation.** Deplacer un objet sous
  ses yeux a etabli que la chaine fonctionnait, la ou trois messages n'y
  suffisaient pas.

## Strategie

- **Verifier bout en bout avant d'annoncer.** Le rendu EEVEE sous display virtuel
  n'allait pas de soi ; il a ete teste, pas suppose.
- **Prevoir une voie de secours independante.** `mcp.py` parle au port sans le
  serveur MCP : le travail n'est pas suspendu a un redemarrage de session.
- **Les scripts de construction doivent etre relancables.** Supprimer l'objet
  homonyme en tete de script evite les doublons a chaque iteration.
