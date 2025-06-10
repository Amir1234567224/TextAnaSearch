import os
import re

class TextProcessor:
    """
    Classe chargée du chargement et du prétraitement des textes.
    - Lecture de fichiers individuels ou d'un dossier.
    - Nettoyage (minuscules, suppression de ponctuation) et tokenisation « tokens » (mots)..
    - Extraction des lignes originales pour permettre la recherche contextuelle.
    """

    def __init__(self):

        # Docs raw : {chemin_fichier: texte_brut}
        self.docs_raw = {}
        # Docs tokens : {chemin_fichier: [liste_de_mots]}
        self.docs_tokens = {}
        # Docs lines : {chemin_fichier: [liste_de_lignes_brutes]}
        self.docs_lines = {}

    def _is_text_file(self, filename: str) -> bool:
        """
        Détermine si un fichier est considéré comme .txt (extension en minuscules).
        """
        return filename.lower().endswith('.txt')

    def _read_file(self, filepath: str) -> str:
        """
        Lit l'intégralité d'un fichier texte en UTF-8, en ignorant les erreurs d'encodage de base.
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Impossible de lire le fichier {filepath} : {e}")

    def _read_lines(self, filepath: str) -> list[str]:
        """
        Lit toutes les lignes brutes d'un fichier texte (sans transformation).
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.readlines()
        except Exception as e:
            raise IOError(f"Impossible de lire les lignes du fichier {filepath} : {e}")

    def _clean_and_tokenize(self, text: str) -> list[str]:
        """
        Nettoie un texte :
        - Passage en minuscules.
        - Suppression de la ponctuation de base (tout caractère non alphanumérique ou espace).
        - Séparation en mots (split sur les espaces).
        Retourne la liste de mots nettoyés.
        """
        # Convertir en minuscules
        text = text.lower()
        # Supprimer toute ponctuation de base (garde lettres, chiffres et espaces)
        text = re.sub(r'[^\w\s]', '', text)
        # Découper sur les espaces
        tokens = text.split()
        # Filtrer les éventuels tokens vides
        return [tok for tok in tokens if tok]

    def process_documents(self, paths: list[str]) -> None:
        """
        Charge un ou plusieurs fichiers ou dossiers pointés dans paths (liste de chemins).
        - Si un élément de paths est un fichier .txt, on le lit.
        - Si c'est un dossier, on parcourt récursivement ce dossier et on lit tous les .txt qu'on y trouve.
        Remplit :
          self.docs_raw    : {chemin_fichier: texte_brut}
          self.docs_lines  : {chemin_fichier: [lignes_brutes]}
          self.docs_tokens : {chemin_fichier: [liste_de_mots_nettoyés]}
        """
        to_process = []
        for p in paths:
            if os.path.isdir(p):
                # Parcours récursif du dossier
                for root, _, files in os.walk(p):
                    for fname in files:
                        if self._is_text_file(fname):
                            to_process.append(os.path.join(root, fname))
            elif os.path.isfile(p) and self._is_text_file(p):
                to_process.append(p)
            else:
                raise FileNotFoundError(f"Le chemin '{p}' n'existe pas ou n'est pas un fichier .txt")

        for filepath in to_process:
            # Lecture du texte brut
            raw = self._read_file(filepath)
            self.docs_raw[filepath] = raw

            # Lecture des lignes brutes (pour recherche contextuelle)
            lignes = self._read_lines(filepath)
            self.docs_lines[filepath] = [l.strip('\n') for l in lignes]

            # Tokenisation de l'intégralité du texte
            tokens = self._clean_and_tokenize(raw)
            self.docs_tokens[filepath] = tokens

    def get_raw(self) -> dict[str, str]:
        """
        Retourne le dictionnaire des textes bruts chargés (chemin -> contenu).
        """
        return self.docs_raw

    def get_tokens(self) -> dict[str, list[str]]:
        """
        Retourne le dictionnaire des tokens par document (chemin -> liste de mots).
        """
        return self.docs_tokens

    def get_lines(self) -> dict[str, list[str]]:
        """
        Retourne le dictionnaire des lignes brutes par document (chemin -> liste de lignes).
        """
        return self.docs_lines