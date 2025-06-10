import os
import sys
from text_processor import TextProcessor
from frequency_analyzer import FrequencyAnalyzer
from simple_indexer import SimpleIndexer
from document_retriever import DocumentRetriever

class CLIManager:
    """
    Interface en ligne de commande pour :
    - Charger des fichiers / dossiers.
    - Lancer l'analyse de fréquence (par document et globale).
    - Afficher les N mots les plus fréquents.
    - Rechercher un mot dans les documents (lignes où il apparaît).
    - Rechercher plusieurs mots-clés et classer les documents par pertinence.
    - Sauvegarder les résultats d'analyse dans un fichier texte.
    """

    def __init__(self):
        # Remarquez qu'on doit utiliser __init__ (deux underscores) pour que Python appelle bien le constructeur.
        self.text_processor = TextProcessor()
        self.freq_analyzer = FrequencyAnalyzer()
        self.indexer = SimpleIndexer()
        self.retriever = None  # Sera instancié après construction de l'index
        self.loaded = False

    def _print_menu(self) -> None:
        print("\n--- TextAnaSearch CLI ---")
        print("1. Charger un ou plusieurs fichiers/dossiers")
        print("2. Analyser la fréquence des mots")
        print("3. Afficher les N mots les plus fréquents (corpus ou par document)")
        print("4. Rechercher la présence d'un mot (affiche fichiers + lignes)")
        print("5. Rechercher des documents contenant des mots-clés et classer")
        print("6. Sauvegarder les fréquences dans un fichier")
        print("7. Quitter")
        print("----------------------------")

    def _input_paths(self) -> list[str]:
        """
        Invite l'utilisateur à entrer une liste de chemins séparés par des virgules.
        Ex : /chemin/fichier1.txt, /autre/folder
        """
        raw = input("Entrez les chemins des fichiers ou dossiers (séparés par une virgule) : ").strip()
        chemins = [ch.strip() for ch in raw.split(',') if ch.strip()]
        return chemins

    def _save_frequencies(self) -> None:
        """
        Sauvegarde les fréquences globales dans un fichier texte.
        """
        if not self.freq_analyzer.corpus_freq:
            print("Aucune fréquence calculée. Lancez d'abord l'analyse de fréquence.")
            return
        filepath = input("Entrez le chemin de sauvegarde (ex: resultats_freq.txt) : ").strip()
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("MOT,FRÉQUENCE\n")
                for mot, count in self.freq_analyzer.get_top_n_in_corpus(len(self.freq_analyzer.corpus_freq)):
                    f.write(f"{mot},{count}\n")
            print(f"Fréquences sauvegardées avec succès dans '{filepath}'.")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")

    def _handle_load(self) -> None:
        """
        Traitement de l'option 1 : chargement des documents.
        """
        chemins = self._input_paths()
        try:
            self.text_processor.process_documents(chemins)
            # Construit l'index à partir des lignes chargées
            docs_lines = self.text_processor.get_lines()
            self.indexer.build_index(docs_lines)
            # Analyse de fréquence
            docs_tokens = self.text_processor.get_tokens()
            self.freq_analyzer.compute_frequency_per_document(docs_tokens)
            self.freq_analyzer.compute_corpus_frequency()
            # Instanciation du retriever
            self.retriever = DocumentRetriever(
                index=self.indexer.get_index(),
                freq_per_doc=self.freq_analyzer.freq_per_doc
            )
            self.loaded = True
            print("Documents chargés et prétraités avec succès.")
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")

    def _handle_frequency_display(self) -> None:
        """
        Option 3 : afficher les N mots les plus fréquents.
        L'utilisateur choisit corpus ou document spécifique.
        """
        if not self.loaded:
            print("Aucun document chargé. Choisissez l'option 1 d'abord.")
            return

        choix = input("Afficher la fréquence pour (1) Corpus global ou (2) Document individuel ? [1/2] : ").strip()
        if choix == '1':
            try:
                n = int(input("Combien de mots les plus fréquents (N) ? ").strip())
            except ValueError:
                print("Veuillez entrer un entier valide.")
                return
            top_n = self.freq_analyzer.get_top_n_in_corpus(n)
            print(f"\nTop {n} mots dans le corpus global :")
            self.freq_analyzer.display_top_n(top_n)
        elif choix == '2':
            docs = list(self.freq_analyzer.freq_per_doc.keys())
            print("Documents disponibles :")
            for i, doc in enumerate(docs, start=1):
                print(f"{i}. {doc}")
            try:
                idx = int(input("Sélectionnez le numéro du document : ").strip())
                if not (1 <= idx <= len(docs)):
                    raise IndexError
                filepath = docs[idx - 1]
                n = int(input("Combien de mots les plus fréquents (N) ? ").strip())
            except (ValueError, IndexError):
                print("Choix invalide.")
                return
            top_n = self.freq_analyzer.get_top_n_in_document(filepath, n)
            print(f"\nTop {n} mots dans le document '{filepath}' :")
            self.freq_analyzer.display_top_n(top_n)
        else:
            print("Choix invalide.")

    def _handle_search_word(self) -> None:
        """
        Option 4 : recherche d'un mot simple dans l'index.
        Affiche pour chaque document le(s) numéro(s) de ligne où il apparaît,
        puis affiche la ligne complète à titre de contexte.
        """
        if not self.loaded:
            print("Aucun document chargé. Choisissez l'option 1 d'abord.")
            return
        mot = input("Entrez le mot à rechercher : ").strip().lower()
        occurrences = self.indexer.search_word(mot)
        if not occurrences:
            print(f"Aucune occurrence de '{mot}' trouvée dans les documents.")
            return
        for filepath, lignes_idx in occurrences.items():
            print(f"\n-- Document : {filepath} --")
            lines = self.text_processor.get_lines()[filepath]
            for num in lignes_idx:
                # Protection si le numéro de ligne est hors-limite
                if 1 <= num <= len(lines):
                    print(f"  Ligne {num} : {lines[num - 1]}")
                else:
                    print(f"  Ligne {num} : (numéro de ligne invalide)")
        print("Recherche terminée.")

    def _handle_retrieve_documents(self) -> None:
        """
        Option 5 : recherche de documents contenant un jeu de mots-clés.
        L'utilisateur entre les mots-clés séparés par des espaces.
        Affiche la liste de fichiers classés par pertinence.
        """
        if not self.loaded:
            print("Aucun document chargé. Choisissez l'option 1 d'abord.")
            return
        raw = input("Entrez les mots-clés séparés par des espaces : ").strip()
        keywords = [w.strip() for w in raw.split() if w.strip()]
        if not keywords:
            print("Aucun mot-clé valide entré.")
            return

        mode = input("Mode de recherche : (1) OR (au moins un mot) / (2) AND (tous les mots) ? [1/2] : ").strip()
        if mode == '1':
            résultats = self.retriever.retrieve(keywords)
        elif mode == '2':
            résultats = self.retriever.boolean_and_retrieve(keywords)
        else:
            print("Choix invalide, retour au menu.")
            return

        if not résultats:
            print("Aucun document trouvé pour ces mots-clés.")
            return

        print("\nDocuments trouvés (chemin – score) :")
        for filepath, score in résultats:
            print(f"  {filepath}  – Score : {score}")
        print("Recherche de documents terminée.")

    def run(self) -> None:
        """
        Boucle principale du CLI : affiche le menu et traite le choix de l'utilisateur.
        """
        while True:
            self._print_menu()
            choix = input("Votre choix : ").strip()
            if choix == '1':
                self._handle_load()
            elif choix == '2':
                # Option 2 : forcer recalcul des fréquences (même logique que dans _handle_load)
                if not self.loaded:
                    print("Aucun document chargé. Choisissez l'option 1 d'abord.")
                else:
                    # On recalcule au cas où les documents auraient changé
                    docs_tokens = self.text_processor.get_tokens()
                    self.freq_analyzer.compute_frequency_per_document(docs_tokens)
                    self.freq_analyzer.compute_corpus_frequency()
                    # Mise à jour du retriever
                    self.retriever = DocumentRetriever(
                        index=self.indexer.get_index(),
                        freq_per_doc=self.freq_analyzer.freq_per_doc
                    )
                    print("Analyse de fréquence effectuée avec succès.")
            elif choix == '3':
                self._handle_frequency_display()
            elif choix == '4':
                self._handle_search_word()
            elif choix == '5':
                self._handle_retrieve_documents()
            elif choix == '6':
                self._save_frequencies()
            elif choix == '7':
                print("Fermeture de TextAnaSearch. Au revoir !")
                sys.exit(0)
            else:
                print("Choix invalide, veuillez sélectionner une option valide.")

if __name__ == "__main__":
    """
    Point d'entrée si on exécute directement ce fichier.
    """
    cli = CLIManager()
    cli.run()
