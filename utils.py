"""
Cree par Theophile PICHARD, sous licence libre MIT.

Ce script a pour l'objectif d'aider au gestionnaire de mise a jour.
"""

import os
import sys
import logger

def createPath(path):
    """Sert a creer le chemin complet sur l'ordinateur.
    Exemple:
    path = /dir/other/file.txt
    => cree le chemin complet, dossiers et fichiers
    """
    #on regarde si le fichier n'existe pas deja
    if os.path.exists(path):
        return
    # on essaie d'abord de creer les dossier
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except: pass
    else: pass
    # si tout va bien, on cree le fichier
    with open(path, "w"): pass
