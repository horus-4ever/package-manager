"""
Cree par Theophile PICHARD, sous licence libre MIT.

Ce script a pour l'objectif de creer un logger.
"""

import datetime
import os
import sys

class Log:
    
    ERROR = "[ERROR]"
    WARNING = "[WARNING]"
    INFO = "[INFO]"

    def __init__(self, stream):
        """Creer un nouvel objet de type Log. Sert a manipuler un fichier de log facilement."""
        self.stream = stream

    def info(self, *args):
        """Creer un message d'information."""
        self(*args, status = Log.INFO)

    def warning(self, *args):
        """Creer un message d'avertissement"""
        self(*args, status = Log.WARNING)

    def error(self, *args):
        """Creer un message d'erreur"""
        self(*args, status = Log.ERROR)

    def blank(self):
        """Creer une nouvelle ligne"""
        print(file = self.stream, flush = True)

    def __call__(self, *args, status = INFO):
        """Fonction appelee quand on appelle l'objet.
        Prend un nombre indefini d'arguments, ainsi qu'un status (INFO, ERROR, WARNING).
        [TIME] [STATUS] [MESSAGE]
        Exemple :
        Log("file doesn't exist", status = Log.ERROR)
        => [TIME] [ERROR] file doesn't exist
        """
        # met la date au bon format
        now = datetime.datetime.now()
        time = f"[{now.date()} {now.hour}:{now.minute}:{now.second}]"
        # l'ajoute au fichier de log
        print(time, status, *args, file = self.stream, flush = True)