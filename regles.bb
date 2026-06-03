# ============================================================
#  BounceBox — Fichier de règles (DSL)
#  Modifiez ce fichier pour changer le comportement du jeu
#  sans toucher au code Python.
# ============================================================

# ── Variables de configuration ───────────────────────────
# Nombre de points nécessaires pour gagner la partie
POINTS_VICTOIRE = 5

# Nombre de boules grises placées au départ
NB_BOULES_GRISES = 9

# Nombre de boules bleues placées au départ
NB_BOULES_BLEUES = 3

# ── Règles de collision ───────────────────────────────────
# Format : JOUEUR frappe BOULE -> ACTION
# JOUEUR  : ROUGE | BLEU
# BOULE   : ROUGE | BLEUE | GRISE
# ACTION  : POINT            (marque un point, retire la boule)
#           COLORIE <COULEUR> (change la couleur de la boule)

ROUGE frappe ROUGE -> POINT
ROUGE frappe GRISE -> COLORIE ROUGE
ROUGE frappe BLEUE -> COLORIE GRISE

BLEU  frappe BLEUE -> POINT
BLEU  frappe GRISE -> COLORIE BLEUE
BLEU  frappe ROUGE -> COLORIE GRISE
