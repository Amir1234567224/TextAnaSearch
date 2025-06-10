from collections import Counter

class FrequencyAnalyzer:
    """
    Classe chargée de l'analyse de fréquence des mots.
    - Calculer la fréquence des mots pour un texte unique ou un ensemble de textes.
    - Trier les mots par fréquence décroissante.
    - Afficher les N mots les plus fréquents.
    """

    def _init_(self):
        # Fréquences par document : {chemin_fichier: Counter({mot: count, ...}), ...}
        self.freq_per_doc: dict[str, Counter] = {}
        # Fréquence agrégée sur tous les documents : Counter({mot: count, ...})
        self.corpus_freq: Counter = Counter()

    def compute_frequency_per_document(self, docs_tokens: dict[str, list[str]]) -> None:
        """
        Pour chaque document, calcule la fréquence des mots.
        Remplit self.freq_per_doc.
        """
        self.freq_per_doc = {}
        for filepath, tokens in docs_tokens.items():
            counter = Counter(tokens)
            self.freq_per_doc[filepath] = counter

    def compute_corpus_frequency(self) -> None:
        """
        Agrège toutes les fréquences par document pour obtenir une fréquence globale.
        Nécessite d'avoir appelé compute_frequency_per_document au préalable.
        """
        self.corpus_freq = Counter()
        for counter in self.freq_per_doc.values():
            self.corpus_freq.update(counter)

    def get_top_n_in_document(self, filepath: str, n: int) -> list[tuple[str, int]]:
        """
        Retourne les n mots les plus fréquents dans un document donné.
        Doit avoir appelé compute_frequency_per_document avant.
        """
        if filepath not in self.freq_per_doc:
            raise KeyError(f"Document '{filepath}' non analysé.")
        return self.freq_per_doc[filepath].most_common(n)

    def get_top_n_in_corpus(self, n: int) -> list[tuple[str, int]]:
        """
        Retourne les n mots les plus fréquents dans l'ensemble du corpus.
        Doit avoir appelé compute_corpus_frequency avant.
        """
        return self.corpus_freq.most_common(n)

    def display_top_n(self, freq_list: list[tuple[str, int]]) -> None:
        """
        Affiche à la console une liste de tuples (mot, fréquence).
        """
        print(f"{'Mot':<20} {'Fréquence':>10}")
        print("-" * 32)
        for mot, count in freq_list:
            print(f"{mot:<20} {count:>10}")