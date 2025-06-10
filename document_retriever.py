from collections import Counter

class DocumentRetriever:
    """
    Classe chargée de la recherche de documents sur base d'une requête de mots-clés.
    - Utilise l'index inversé (de SimpleIndexer) pour localiser les documents concernés.
    - Calcule un score de pertinence basique (nombre de mots-clés trouvés) et trie les résultats.
    """

    def __init__(self, index: dict[str, dict[str, list[int]]], freq_per_doc: dict[str, Counter]):
        """
        :param index: index inversé (mot -> {fichier: [n°_lignes]})
        :param freq_per_doc: fréquences par document (chemin_fichier -> Counter(mot:count))
        """
        self.index = index
        self.freq_per_doc = freq_per_doc

    def retrieve(self, keywords: list[str]) -> list[tuple[str, int]]:
        """
        À partir d'une liste de mots-clés, retrouve les documents contenant au moins un de ces mots.
        Calcule un score de pertinence = somme des occurrences de chaque mot-clé dans le document
        (i.e. on summe les fréquences issues de freq_per_doc).
        Retourne une liste triée de tuples (chemin_fichier, score) par ordre décroissant de score.
        """
        if not keywords:
            return []

        # Pour chaque mot-clé, récupérer les documents où il apparaît
        docs_with_keyword: dict[str, int] = {}
        for kw in keywords:
            mot = kw.lower()
            if mot in self.index:
                # Pour chaque doc contenant ce mot, augmenter le score
                for filepath, _ in self.index[mot].items():
                    freq = self.freq_per_doc.get(filepath, Counter()).get(mot, 0)
                    docs_with_keyword.setdefault(filepath, 0)
                    docs_with_keyword[filepath] += freq

        # Transformer en liste triée par score décroissant
        résultats = sorted(docs_with_keyword.items(), key=lambda pair: pair[1], reverse=True)
        return résultats

    def boolean_and_retrieve(self, keywords: list[str]) -> list[tuple[str, int]]:
        """
        Variante booléenne « AND » : ne renvoie que les documents contenant tous les mots-clés.
        Calcule le score de la même manière (somme des fréquences).
        """
        if not keywords:
            return []

        # D'abord, pour chaque mot, récupérer l'ensemble des documents
        sets_of_docs = []
        for kw in keywords:
            mot = kw.lower()
            docs_for_mot = set(self.index.get(mot, {}).keys())
            sets_of_docs.append(docs_for_mot)

        # Intersection des ensembles
        docs_intersection = set.intersection(*sets_of_docs) if sets_of_docs else set()

        # Pour ces documents, calculer le score identique
        résultats = []
        for filepath in docs_intersection:
            score = 0
            for kw in keywords:
                mot = kw.lower()
                score += self.freq_per_doc.get(filepath, Counter()).get(mot, 0)
            résultats.append((filepath, score))

        # Tri décroissant
        résultats.sort(key=lambda pair: pair[1], reverse=True)
        return résultats
