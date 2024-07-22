from enum import Enum

class Couleur(Enum):
    BLEU = 0
    ROUGE = 1

class Joueur:
    def __init__(self, id, couleur : Couleur):
        self.couleur = couleur
        self.id = id