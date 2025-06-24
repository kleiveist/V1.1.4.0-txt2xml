import sys
import os
import configparser

def find_settings_ini(start_dir):
    """
    Durchsucht start_dir und alle Unterverzeichnisse nach einer Datei namens "settings.ini".
    Gibt den vollständigen Pfad zurück, falls gefunden, sonst None.
    """
    for root, dirs, files in os.walk(start_dir):
        if "settings.ini" in files:
            return os.path.join(root, "settings.ini")
    return None

# Starte die Suche ab dem aktuellen Arbeitsverzeichnis
start_dir = os.path.abspath(os.getcwd())
ini_path = find_settings_ini(start_dir)
if ini_path:
    print(f"INI-Datei gefunden: {ini_path}")
else:
    print("INI-Datei nicht gefunden – Standardwerte werden verwendet.")

config = configparser.ConfigParser()
if ini_path:
    config.read(ini_path)

# Lese den Wert; fällt auf False zurück, falls die Einstellung nicht gefunden wird
wait_for_enter = config.getboolean("MODULS", "wait_for_enter", fallback=False)

def find_txt2xml_folder():
    """
    Sucht im aktuellen Verzeichnis und in dessen übergeordneten Verzeichnissen
    nach einem Ordner namens "txt2xml" und gibt dessen absoluten Pfad zurück.
    """
    current_dir = os.path.abspath(os.getcwd())
    while True:
        candidate = os.path.join(current_dir, "txt2xml")
        if os.path.isdir(candidate):
            return candidate
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            break
        current_dir = parent
    return None

txt2xml_folder = find_txt2xml_folder()
if txt2xml_folder:
    sys.path.insert(0, txt2xml_folder)
    print(f"Ordner 'txt2xml' gefunden: {txt2xml_folder}")
else:
    print("Ordner 'txt2xml' wurde nicht gefunden. Bitte stelle sicher, dass die Module vorhanden sind.")

import glob
import shutil
import xml.etree.ElementTree as ET

from parser import parse_txt_file
from xml_builder import build_xml
# Hier wurde der Import angepasst:
from _folder import create_output_folder

def process_txt_files():
    txt_files = [f for f in glob.glob("*.txt") if f.lower() not in ["log.txt", "error_log.txt", "_folder_structure.txt"]]
    if not txt_files:
        print("Keine .txt-Dateien gefunden!")
        return

    for txt_file in txt_files:
        print(f"Verarbeite {txt_file} ...")
        cards = parse_txt_file(txt_file)
        base_name = os.path.splitext(txt_file)[0]
        
        # Erzeuge die Haupt-XML-Datei (userLessonID "123456")
        xml_root = build_xml(cards, lesson_title=base_name, user_lesson_id="123456")
        ET.indent(xml_root, space="  ", level=0)
        
        output_folder = create_output_folder(base_name)
        output_xml = os.path.join(output_folder, base_name + ".xml")
        tree = ET.ElementTree(xml_root)
        tree.write(output_xml, encoding="utf-8", xml_declaration=False)
        
        shutil.move(txt_file, os.path.join(output_folder, txt_file))
        
        # Erzeuge die Archiv-Version (userLessonID "669686010")
        archive_user_id = "669686010"
        xml_archive_root = build_xml(cards, lesson_title=base_name, user_lesson_id=archive_user_id)
        ET.indent(xml_archive_root, space="  ", level=0)
        archive_xml_path = os.path.join(output_folder, "by_content.xml")
        tree_archive = ET.ElementTree(xml_archive_root)
        tree_archive.write(archive_xml_path, encoding="utf-8", xml_declaration=True)
        
        # Aktualisiere das vorhandene Archiv mittels b2y.py.
        from b2y import update_by2_archive

        # Hier wird der Archivname explizit angegeben:
        archive_path = os.path.join(output_folder, "lesson_669974947_import-lektion00.by2")
        by_content_path = os.path.join(output_folder, "by_content.xml")
        
        try:
            update_by2_archive(archive_path, by_content_path)
            print(f"Archiv '{os.path.basename(archive_path)}' wurde aktualisiert.")
        except Exception as e:
            print(f"Fehler beim Aktualisieren des Archivs: {e}")

        print(f"Erstellt: Ordner '{output_folder}' mit '{base_name}.xml' und 'by_content.xml'.")

def main():
    # Optional: Einen Eingabeordner als Kommandozeilenargument übergeben
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
        if os.path.isdir(input_dir):
            os.chdir(input_dir)
            print(f"Arbeitsverzeichnis geändert zu: {os.getcwd()}")
        else:
            print(f"Der angegebene Pfad '{input_dir}' ist kein gültiges Verzeichnis.")
            sys.exit(1)
    process_txt_files()

if __name__ == "__main__":
    main()
    if wait_for_enter:
        input("Drücken Sie Enter zum Beenden...")
