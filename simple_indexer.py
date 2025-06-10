import re

class SimpleIndexer:
    """
    Classe chargée de construire un index inversé très basique :
    - mot -> {chemin_fichier: [lignes_contenant_le_mot], ...}
    - Permet de rechercher rapidement la présence d'un mot dans les documents,
      et de lister les documents + lignes où il apparaît.
    """

    def _init_(self):
        # Index inversé : {mot: {chemin_fichier: [n°_ligne1, n°_ligne2, ...], ...}, ...}
        self.index: dict[str, dict[str, list[int]]] = {}

    def build_index(self, docs_lines: dict[str, list[str]]) -> None:
        """
        Construit l'index à partir des lignes brutes de chaque document.
        - Pour chaque document (chemin_fichier), parcourt chaque ligne (numéro de ligne et texte).
        - Nettoie la ligne (minuscules, suppression ponctuation), tokenize, puis
          pour chaque mot trouvé, ajoute au dictionnaire l'entrée (fichier, numéro de ligne).
        """
        self.index = {}
        for filepath, lines in docs_lines.items():
            for idx, raw_line in enumerate(lines, start=1):
                # Nettoyage simple : minuscules + suppression ponctuation
                line = raw_line.lower()
                line_clean = re.sub(r'[^\w\s]', '', line)
                tokens = line_clean.split()
                for mot in tokens:
                    if mot not in self.index:
                        self.index[mot] = {}
                    if filepath not in self.index[mot]:
                        self.index[mot][filepath] = []
                    # On ajoute le n° de ligne où le mot apparaît
                    self.index[mot][filepath].append(idx)

    def search_word(self, word: str) -> dict[str, list[int]]:
        """
        Recherche un mot (en ignorant la casse) dans l'index.
        Retourne un dictionnaire {chemin_fichier: [n°_ligne1, n°_ligne2, ...], ...}.
        Si le mot n'existe pas dans l'index, retourne un dict vide.
        """
        mot = word.lower()
        return self.index.get(mot, {})

    def get_index(self) -> dict[str, dict[str, list[int]]]:
        """
        Retourne l'index inversé complet.
        """
        return self.index