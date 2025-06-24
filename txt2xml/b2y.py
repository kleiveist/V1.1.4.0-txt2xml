import os
import subprocess
import shutil

def update_by2_archive(archive_filepath, by_content_filepath):
    """
    Aktualisiert das .by2-Archiv, indem der interne Eintrag by_content.xml
    durch die neu erzeugte by_content.xml ersetzt wird.
    
    Falls das Archiv nicht im Zielverzeichnis existiert, wird versucht,
    es aus dem Modulordner (txt2xml) zu kopieren.

    Parameter:
      archive_filepath: Zielpfad des Archivs (z.B. im Output-Ordner)
      by_content_filepath: Pfad zur neu erzeugten by_content.xml im Output-Ordner

    Rückgabe:
      True, wenn die Aktualisierung erfolgreich war.
    """
    # Prüfe, ob die by_content.xml existiert
    if not os.path.exists(by_content_filepath):
        raise FileNotFoundError(f"Die Datei '{by_content_filepath}' wurde nicht gefunden.")
    
    # Falls das Archiv nicht existiert, kopiere es aus dem Modulordner (txt2xml)
    if not os.path.exists(archive_filepath):
        module_folder = os.path.dirname(os.path.abspath(__file__))
        # Suche nach einer .by2-Datei im Modulordner
        by2_files = [f for f in os.listdir(module_folder) if f.lower().endswith('.by2')]
        if not by2_files:
            raise FileNotFoundError(f"Keine .by2-Datei im Modulordner '{module_folder}' gefunden, um sie zu kopieren.")
        # Wähle die erste gefundene .by2-Datei und kopiere sie in den Zielordner
        source_archive = os.path.join(module_folder, by2_files[0])
        shutil.copy(source_archive, archive_filepath)
        print(f"Die .by2-Datei '{os.path.basename(source_archive)}' wurde nach '{archive_filepath}' kopiert.")

    # Der Dateiname, wie er im Archiv enthalten ist, wird angenommen: "by_content.xml"
    by_content_filename = os.path.basename(by_content_filepath)
    # Das Arbeitsverzeichnis ist das Verzeichnis, in dem sich die by_content.xml befindet.
    work_dir = os.path.dirname(by_content_filepath)

    # Pfad zu 7z.exe – bitte gegebenenfalls anpassen!
    seven_zip_path = r"C:\Program Files\7-Zip\7z.exe"
    if not os.path.exists(seven_zip_path):
        raise FileNotFoundError(f"7-Zip wurde nicht unter '{seven_zip_path}' gefunden.")

    # Führe den 7-Zip-Befehl aus, um im Archiv den Eintrag by_content.xml zu ersetzen.
    result = subprocess.run(
        [seven_zip_path, "u", archive_filepath, by_content_filename],
        cwd=work_dir,
        capture_output=True,
        text=True
    )
    print("7z stdout:", result.stdout)
    print("7z stderr:", result.stderr)

    if result.returncode != 0:
        raise Exception(f"Fehler beim Aktualisieren des Archivs:\n{result.stderr}")
    
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python b2y.py <pfad_zur_by2_datei> <pfad_zur_by_content.xml>")
        sys.exit(1)
    
    archive_path = sys.argv[1]
    by_content_path = sys.argv[2]
    
    try:
        update_by2_archive(archive_path, by_content_path)
        print("Archiv erfolgreich aktualisiert.")
    except Exception as e:
        print(f"Fehler: {e}")
        sys.exit(1)
