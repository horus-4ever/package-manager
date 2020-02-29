"""
Ce script a pour l'objectif de creer un gestionnaire de packages simple.
"""

__license__ = "GPL"

import utils
import sys
import os
import time
from logger import *

def to_int64(data):
    """Parce que aucune autre fonction n'existe en Python... Converti 4o en un entier 32bits"""
    somme = 0
    for char in data:
        somme <<= 8
        somme += char
    return somme

def from_int64(n):
    """Converti un entier 32bits en 4o"""
    result = [0 for _ in range(8)]
    counter = 7
    while n:
        result[counter] = (n & 0xFF)
        n >>= 8
        counter -= 1
    return bytes(result)


def findAllFiles(path):
    """Cherche tous les fichiers d'un dossier."""
    for p in os.listdir(path):
        if os.path.isdir(os.path.join(path, p)):
            yield from findAllFiles(os.path.join(path, p))
        else:
            yield os.path.join(path, p)


class _Header:

    SIZE = 28
    NORMAL_MAGIC_NUMBER = bytes([0x00, 0x6d, 0x61, 0x6a])
    
    def __init__(self):
        """Gestionnaire de header des packets .maj"""
        self.init()

    def init(self):
        """Initialize variables to None"""
        self.MAGIC_NUMBER = None
        self.FILE_SIZE = None
        self.INDEX_SIZE = None
        self.DATA_SIZE = None

    def read(self, stream):
        """Lis l'en-tete des fichiers .maj"""
        # supprime les lectures precedantes
        self.init()
        # lis et fait les tests
        try:
            self.MAGIC_NUMBER = stream.read(4)
            self.FILE_SIZE = to_int64(stream.read(8))
            self.INDEX_SIZE = to_int64(stream.read(8))
            self.DATA_SIZE = to_int64(stream.read(8))
        except:
            sys.stderr.write("Error while reading error\n")
            return False
        return self.validate()

    def create(self, index_size, data_size):
        """3eme etape de la creation de packet.
        Ajoute le header
        """
        self.MAGIC_NUMBER = _Header.NORMAL_MAGIC_NUMBER
        self.INDEX_SIZE = index_size
        self.DATA_SIZE = data_size
        self.FILE_SIZE = 28 + self.DATA_SIZE + self.INDEX_SIZE
        return True

    def get(self):
        """Retourne les donnees sous forme de bytes"""
        result = self.MAGIC_NUMBER + from_int64(self.FILE_SIZE) + from_int64(self.INDEX_SIZE) + from_int64(self.DATA_SIZE)
        return result

    def validate(self):
        """Valide les donnees."""
        return (self.MAGIC_NUMBER == _Header.NORMAL_MAGIC_NUMBER) and ( (self.FILE_SIZE - self.INDEX_SIZE - self.DATA_SIZE - _Header.SIZE) == 0 )

    def __repr__(self):
        """Representation litterale de l'objet."""
        return f"{self.MAGIC_NUMBER} {self.FILE_SIZE} {self.INDEX_SIZE} {self.DATA_SIZE}"


class _IndexTable:

    def __init__(self):
        """Gestionnaire de la table de donnees des packets .maj"""
        self.init()

    def init(self):
        """Met des valeurs par default aux attributs"""
        self.table = {}

    def read(self, stream, index_size):
        """Lis depuis le flux passe en parametre"""
        # on efface les anciennes données
        self.init()
        # on lit index_size octets de fichier et on verifie le tout :)
        while index_size:
        # et si aucune erreur, on met le tout dans la table
            pathlen = stream.read(8)
            pathlen = to_int64(pathlen)
            key = stream.read(pathlen)
            file_size = to_int64(stream.read(8))
            try:
                key = key.decode("utf-8")
            except:
                print("ERROR, can't decode key or file_size")
                return False
            # si aucune exception, alors on l'ajoute a la table
            self.table[key] = file_size
            index_size -= 16 + pathlen
        return True

    def create(self, directory):
        """2nde etape de la creation de packet.
        Ajoute la table d'index
        """
        self.init()
        #
        for file in findAllFiles(directory):
            file_size = os.path.getsize(os.path.join(directory, file))
            self.table[file] = file_size
        # si tout va bien...
        return True

    def get(self, directory):
        """Retourne les bytes de la table d'index"""
        result = []
        for path, n in self.table.items():
            path = os.path.join(*path.replace(directory, "").split(os.sep)[1:])
            lenpath = len(path.encode())
            result.append(from_int64(lenpath) + path.encode("utf-8") + from_int64(n))
        return b"".join(result)

    def getDataLength(self):
        """Donne la longueur du segment de donnees"""
        return sum(self.table.values())

    def __iter__(self):
        """On peut iterer : retourne le dictionnaire"""
        return self.table

    def __repr__(self):
        """Representation de la table"""
        return str(self.table)
        

class PackageManager:

    def __init__(self, log_filename = None):
        """PackageManager permet de gerer les packets de format .maj."""
        self.HEADER = _Header()
        self.INDEX_TABLE = _IndexTable()
        self.LOG = Log(log_filename)

    def read(self, packet):
        """Lis un packet .maj"""
        if self.HEADER.read(packet):
            self.LOG.info("Header has been read...")
        else:
            self.LOG.error("Could not read Header!")
            return False
        if self.INDEX_TABLE.read(packet, self.HEADER.INDEX_SIZE):
            self.LOG.info("Index table has been read...")
        else:
            self.LOG.error("Could not read Index table!")
            return False
        self.LOG.info("Packet read!")
        self.LOG.blank()
        return True

    def create(self, directory, outpath = "temp.maj"):
        """On cree un nouveau packet .maj"""
        # path must be absolute
        if not os.path.isabs(directory):
            raise Exception("Path must be absolute")
        if not os.path.exists(directory):
            self.LOG.error(f"Directory not found '{directory}'")
            return False
        # 1ere etape
        self.LOG.info("Create index table...")
        self.INDEX_TABLE.create(directory)
        index_table = self.INDEX_TABLE.get(directory)
        # 2eme etape
        self.LOG.info("Create header...")
        self.HEADER.create(len(index_table), self.INDEX_TABLE.getDataLength())
        header = self.HEADER.get()
        # construction finale
        self.LOG.info("Create packet...")
        # pour chaque fichier de l'INDEX_TABLE
        with open(outpath, "wb") as doc:
            # le header + la table d'index
            doc.write(header + index_table)
            # puis les donnees
            for path in self.INDEX_TABLE.table:
                # on ouvre chaque fichier
                with open(os.path.join(directory, path), "rb") as file:
                    # le boucle dure tant que l'on lit des donnees
                    while True:
                        datas = file.read(1024 * 32)
                        # si on n'a rien lu, on a atteint la fin du fichier et on brise la boucle
                        if not datas:
                            break
                        # sinon, on ecrit les donnees dans l'autre fichier
                        doc.write(datas)
                        del datas
                # un petit flush ;)
                doc.flush()
        self.LOG.info("Packet has been created!")
        self.LOG.blank()

    def install(self, filename, directory = ""):
        """Installe le packet dans le repertoire specifie"""
        try:
            os.mkdir(directory)
        except:
            self.LOG.warning(f"Destination directory already exists '{directory}'")

        with open(filename, "rb") as packet:
            if not self.read(packet):
                return False
            else:
                for path, size in self.INDEX_TABLE.table.items():
                    utils.createPath(os.path.join(directory, path))
                    # on lit et ecrit les donnees
                    with open(os.path.join(directory, path), "wb") as doc:
                        # on lis les donnees du packets
                        to_read = size // (1024 * 32)
                        remainder = size % (1024 * 32)
                        for _ in range(to_read):
                            datas = packet.read(1024 * 32)
                            doc.write(datas)
                        doc.write(packet.read(remainder))
                        # et flush
                        doc.flush()
        # sans erreurs ;)
        self.LOG.info("Packet installed successfully!")
        return True

if __name__ == "__main__":
    p = PackageManager()
    p.install("temp.maj", "FAKE")
