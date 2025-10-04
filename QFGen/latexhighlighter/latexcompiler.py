import os
import subprocess
import tempfile
import shutil
import time
from tqdm import tqdm

class CompilationError(Exception):
        """Exception levée en cas d'erreur de compilation."""
        pass

class LaTeXCompiler:
    """
    Classe permettant de gérer des documents LaTeX, incluant la lecture et la sauvegarde des documents,
    des manipulations de base, la compilation avec LuaLaTeX ou avec une double compilation pour les sommaires,
    et l'ouverture du fichier PDF résultant dans Microsoft Edge.
    """

    def __init__(self, document_paths):
        """
        Initialise l'instance avec une liste de chemins vers les documents LaTeX.
        """
        self.error_code=""
        self.documents = document_paths  # Liste des chemins des documents LaTeX
        self.data_compilation_times="latexcompiler_compilation_times.txt"
        self.compilation_times = self._load_compilation_times()


    def _load_compilation_times(self):
        """Charge les temps de compilation à partir du fichier."""
        if not os.path.exists(self.data_compilation_times):
            return []

        with open(self.data_compilation_times, 'r') as f:
            times = [float(line.strip()) for line in f.readlines()]
        
        return times
    def _save_compilation_time(self, duration):
        """Enregistre le temps de compilation dans le fichier."""
        self.compilation_times.append(duration)
        if len(self.compilation_times) > 20:
            self.compilation_times.pop(0)  # Garder seulement les 20 derniers temps

        with open(self.data_compilation_times, 'w') as f:
            for time in self.compilation_times:
                f.write(f"{time}\n")

    def _get_average_compilation_time(self):
        """Calcule le temps moyen de compilation à partir des 20 derniers enregistrements."""
        if not self.compilation_times:
            return 100  # Valeur par défaut si aucune donnée
        return sum(self.compilation_times) / len(self.compilation_times)
    
    def backup_documents(self, backup_dir):
        """
        Copie et sauvegarde les documents dans un répertoire spécifié.
        """
        os.makedirs(backup_dir, exist_ok=True)
        for doc in self.documents:
            shutil.copy(doc, os.path.join(backup_dir, os.path.basename(doc)))

    def manipulate_document(self, document_path, manipulation_func):
        """
        Applique une fonction de manipulation sur le contenu d'un document LaTeX.
        """
        try:
            with open(document_path, 'r', encoding='utf-8') as file:
                content = file.read()

            content = manipulation_func(content)

            with open(document_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except Exception as e:
            self.error_code="Erreur lors de la manipulation du document : {}".format(e)
            return False
        return True
    def destroy_auxiliary_files(self,pdf_path):
        print("""
            A implémenter : 
                permet de supprimer les fichiers auxiliaires pour améliorer l'expérience de compilation automatique
            """)
        
    def compile_latex_errors(self, document_path, output_directory=None, double_compile=False):
        """
        Compile le document LaTeX en utilisant LuaLaTeX ou une double compilation si nécessaire.
        Affiche une barre de progression pendant la compilation.
        """
        compiler = "lualatex"#"pdflatex"  # ou "lualatex"
        if output_directory:
            pdf_output_path = os.path.join(output_directory, os.path.splitext(os.path.basename(document_path))[0] + ".pdf")
            compile_command = [compiler, "-output-directory=" + output_directory, document_path]
        else:
            pdf_output_path = os.path.splitext(document_path)[0] + ".pdf"
            compile_command = [compiler, document_path]

        average_time = self._get_average_compilation_time()

        try:
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tempf:
                with tqdm(total=average_time, desc="Compilation en cours", unit="s") as pbar:
                    start_time = time.time()
                    process = subprocess.Popen(compile_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            tempf.write(output)
                            tempf.flush()
                            elapsed_time = time.time() - start_time
                            pbar.update(min(elapsed_time - pbar.n, pbar.total - pbar.n))  # Mise à jour de la barre de progression

                    # Vérifie le code de retour du processus pour les erreurs
                    if process.returncode != 0:
                        raise CompilationError("Erreur de compilation : {}".format(process.returncode))

                    if double_compile:
                        tempf.seek(0)
                        tempf.truncate()
                        start_time = time.time()
                        process = subprocess.Popen(compile_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                        while True:
                            output = process.stdout.readline()
                            if output == '' and process.poll() is not None:
                                break
                            if output:
                                tempf.write(output)
                                tempf.flush()
                                elapsed_time = time.time() - start_time
                                pbar.update(min(elapsed_time - pbar.n, pbar.total - pbar.n))  # Mise à jour de la barre de progression

                        if process.returncode != 0:
                            raise CompilationError("Erreur de compilation : {}".format(process.returncode))

            total_duration = time.time() - start_time
            self._save_compilation_time(total_duration)
            self.last_duration = total_duration
            self.pdf_output_path = pdf_output_path
            return True, pdf_output_path
        except CompilationError as e:
            self.error_code = str(e)
            with open(tempf.name, 'r') as tempf:
                log_lines = tempf.readlines()[-20:]
                print("".join(log_lines))
            return False, None
        finally:
            # Supprimer le fichier temporaire
            if os.path.exists(tempf.name):
                os.remove(tempf.name)

    def compile_latex(self, document_path, output_directory=None, double_compile=False):
        """
        Compile le document LaTeX en utilisant LuaLaTeX ou une double compilation si nécessaire.
        Affiche une barre de progression pendant la compilation.
        """
        compiler = "pdflatex"  # ou "lualatex"
        if output_directory:
            pdf_output_path = os.path.join(output_directory, os.path.splitext(os.path.basename(document_path))[0] + ".pdf")
            compile_command = [compiler, "-output-directory=" + output_directory, document_path]
        else:
            pdf_output_path = os.path.splitext(document_path)[0] + ".pdf"
            compile_command = [compiler, document_path]

        average_time = self._get_average_compilation_time()

        try:
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tempf:
                with tqdm(total=average_time, desc="Compilation en cours", unit="s") as pbar:
                    start_time = time.time()
                    process = subprocess.Popen(compile_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            tempf.write(output)
                            tempf.flush()
                            elapsed_time = time.time() - start_time
                            pbar.update(min(elapsed_time - pbar.n, pbar.total - pbar.n))  # Mise à jour de la barre de progression

                    # Vérifie le code de retour du processus pour les erreurs
                    if process.returncode != 0:
                        raise subprocess.CalledProcessError(process.returncode, compile_command)

                    if double_compile:
                        tempf.seek(0)
                        tempf.truncate()
                        start_time = time.time()
                        process = subprocess.Popen(compile_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                        while True:
                            output = process.stdout.readline()
                            if output == '' and process.poll() is not None:
                                break
                            if output:
                                tempf.write(output)
                                tempf.flush()
                                elapsed_time = time.time() - start_time
                                pbar.update(min(elapsed_time - pbar.n, pbar.total - pbar.n))  # Mise à jour de la barre de progression

                        if process.returncode != 0:
                            raise subprocess.CalledProcessError(process.returncode, compile_command)

            total_duration = time.time() - start_time
            self._save_compilation_time(total_duration)
            self.last_duration=total_duration
            return True, pdf_output_path
        except subprocess.CalledProcessError as e:
            self.error_code = "Erreur de compilation : {}".format(e)
            with open(tempf.name, 'r') as tempf:
                log_lines = tempf.readlines()[-20:]
                print("".join(log_lines))
            return False, None
        finally:
            # Supprimer le fichier temporaire
            if os.path.exists(tempf.name):
                os.remove(tempf.name)
    def compile_latex_old(self, document_path, output_directory=None, double_compile=False):
        """
        Compile le document LaTeX en utilisant LuaLaTeX ou une double compilation si nécessaire.
        """
        compiler = "pdflatex"#"lualatex"
        if output_directory:
            pdf_output_path = os.path.join(output_directory, os.path.splitext(os.path.basename(document_path))[0] + ".pdf")
            compile_command = [compiler, "-output-directory=" + output_directory, document_path]
        else:
            pdf_output_path = os.path.splitext(document_path)[0] + ".pdf"
            compile_command = [compiler, document_path]
        
        try:
            subprocess.run(compile_command, check=True)
            if double_compile:  # Double compilation pour les documents nécessitant un sommaire
                subprocess.run(compile_command, check=True)
        except subprocess.CalledProcessError as e:
            self.error_code = "Erreur de compilation : {}".format(e)
            return False, None
        return True, pdf_output_path

    def open_pdf_in_edge(self, pdf_path):
        """
        Tente d'ouvrir le fichier PDF dans le navigateur par défaut pour les fichiers PDF.
        """
        try:
            if not os.path.exists(pdf_path):
                self.error_code = "Le fichier PDF n'existe pas."
                return False

            os.startfile(pdf_path)
        except Exception as e:
            self.error_code = "Erreur lors de l'ouverture du fichier PDF : {}".format(e)
            return False
        return True

    def compile_and_open(self, document_path, output_directory=None, double_compile=False):
        """
        Compile le fichier LaTeX et ouvre le PDF résultant.
        """
        success, pdf_path = self.compile_latex(document_path, output_directory, double_compile)
        if not success:
            print("Échec de la compilation :", self.error_code)
            return False

        if not self.open_pdf_in_edge(pdf_path):
            print("Échec de l'ouverture du PDF :", self.error_code)
            return False

        print(f"Compilation et ouverture réussies - durée : {self.last_duration}")
        return True
    
    def compile_and_return_pdf_path(self, document_path, output_directory=None, double_compile=False):
        """
        Compile le fichier LaTeX et retourne le chemin du PDF résultant.
        """
        success, pdf_path = self.compile_latex_errors(document_path, output_directory, double_compile=False)
        if not success:
            print("Échec de la compilation :", self.error_code)
            return None
        return pdf_path