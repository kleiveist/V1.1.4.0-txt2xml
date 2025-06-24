# Datei: file_util.py

import os
import datetime
import configparser

def create_output_folder(base_name):
    """
    Erstellt einen Ausgabeverzeichnis basierend auf einer Einstellung in der settings.ini.

    Liest in der INI-Datei (im selben Verzeichnis wie das Skript) den Wert
    unter [Settings] -> output_data ein.

    - Ist output_data auf einen "true"-Wert gesetzt (z.B. "true", "1", "yes", "on"),
      wird ein Ordner im Format "jjmmtt" bzw. "jjmmtt_01", "jjmmtt_02", ... erstellt.
    - Ist output_data auf einen "false"-Wert gesetzt (z.B. "false", "0", "no", "off"),
      wird der Ordnername aus dem Parameter base_name (also dem Namen der .txt-Datei)
      übernommen. Existiert dieser Ordner bereits, wird eine Zählervariante (z.B. base_name_01)
      erzeugt.

    Rückgabe:
      Pfad zum erstellten Ordner.
    """
    # INI-Datei einlesen
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), "settings.ini")
    config.read(config_path)
    
    # Default: Datum-Ordner, falls keine Einstellung vorhanden ist
    output_data = True  
    if "Settings" in config and "output_data" in config["Settings"]:
        val = config["Settings"]["output_data"].strip().lower()
        output_data = val in ["true", "1", "yes", "on"]
    
    # Bestimme das Basisverzeichnis
    if output_data:
        # Datum-basiertes Format: jjmmtt
        folder_base = datetime.datetime.now().strftime("%y%m%d")
    else:
        # Name der .txt-Datei verwenden (ohne Erweiterung, da base_name üblicherweise so übergeben wird)
        folder_base = base_name
    
    folder_name = folder_base
    if os.path.exists(folder_name):
        for i in range(1, 100):
            folder_candidate = f"{folder_base}_{i:02d}"
            if not os.path.exists(folder_candidate):
                folder_name = folder_candidate
                break
    os.makedirs(folder_name, exist_ok=True)
    return folder_name
