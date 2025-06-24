import os
import subprocess
import shutil

def archive_by_content(output_folder, archive_user_id, base_name):
    """
    Kopiert die vorhandene .by2-Datei aus dem txt2xml-Ordner (also dem Modulordner)
    in den output_folder (z. B. "jjmmtt" oder "jjmmtt_01"). Anschließend wird mit 7-Zip
    in dem kopierten Archiv die enthaltene by_content.xml durch die von txt2xml.py
    erzeugte by_content.xml ersetzt und das Archiv gespeichert.

    Die Parameter archive_user_id und base_name werden nicht mehr zur Benennung des
    Archivs verwendet – stattdessen bleibt der Originalname der .by2-Datei erhalten.

    Rückgabe:
      Pfad zur aktualisierten .by2-Datei.
    """
    # Ermittle den Ordner, in dem sich dieses Modul (und damit auch die exportierte .by2-Datei)
    # befindet – dies entspricht dem txt2xml-Ordner.
    script_folder = os.path.dirname(os.path.abspath(__file__))
    
    # Suche im script_folder nach einer .by2-Datei (unabhängig von Groß-/Kleinschreibung)
    by2_files = [f for f in os.listdir(script_folder) if f.lower().endswith('.by2')]
    if not by2_files:
        raise FileNotFoundError("Keine .by2-Datei im txt2xml-Ordner gefunden.")
    
    # Verwende die erste gefundene .by2-Datei und behalte deren Originalnamen bei
    exported_by2_file = by2_files[0]
    final_archive_filepath = os.path.join(output_folder, exported_by2_file)
    
    # Kopiere die vorhandene .by2-Datei in den output_folder
    shutil.copy(os.path.join(script_folder, exported_by2_file), final_archive_filepath)
    print(f"Die .by2-Datei '{exported_by2_file}' wurde in den Ordner '{output_folder}' kopiert.")

    # Stelle sicher, dass die von txt2xml.py erzeugte by_content.xml existiert
    by_content_filename = "by_content.xml"
    abs_by_content_path = os.path.join(output_folder, by_content_filename)
    if not os.path.exists(abs_by_content_path):
        raise FileNotFoundError(f"Die Datei '{by_content_filename}' wurde nicht im Ordner {output_folder} gefunden.")

    # Pfad zu 7z.exe – bitte anpassen, falls notwendig!
    seven_zip_path = r"C:\Program Files\7-Zip\7z.exe"
    if not os.path.exists(seven_zip_path):
        raise FileNotFoundError(f"7-Zip wurde nicht unter '{seven_zip_path}' gefunden.")

    # Aktualisiere im kopierten Archiv den Eintrag by_content.xml
    result = subprocess.run(
         [seven_zip_path, "u", final_archive_filepath, by_content_filename],
         cwd=output_folder,
         capture_output=True,
         text=True
    )
    print("7z stdout:", result.stdout)
    print("7z stderr:", result.stderr)
    
    if result.returncode != 0:
         raise Exception(f"Fehler beim Aktualisieren des Archivs:\n{result.stderr}")
    
    return final_archive_filepath
