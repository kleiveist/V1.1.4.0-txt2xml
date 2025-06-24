import os
from datetime import datetime as dt
import configparser
from _logger import log_message  # Importiere unsere Log-Funktion aus _logger.py

MAX_FOLDER_NAME_LENGTH = 260  # Maximale erlaubte Länge für den Ordnernamen

def parse_bool(value):
    """
    Wandelt einen String in einen Boolean um.
    Akzeptierte True-Werte: ["true", "1", "yes", "on"]
    Akzeptierte False-Werte: ["false", "0", "no", "off"]
    """
    if isinstance(value, bool):
        return value
    value = value.strip().lower()
    value_on = ["true", "1", "yes", "on"]
    value_off = ["false", "0", "no", "off"]
    if value in value_on:
        return True
    elif value in value_off:
        return False
    else:
        log_message(f"Ungültiger Boolean-Wert: '{value}'", level="warning")
        raise ValueError(f"Ungültiger Boolean-Wert: {value}")

def read_config():
    config = configparser.ConfigParser()
    # Absolute Pfadangabe basierend auf dem Ort von _folder.py:
    config_path = os.path.join(os.path.dirname(__file__), "settings.ini")
    config.read(config_path)
    
    settings = {}
    if "FOLDER" in config:
        cfg = config["FOLDER"]
        settings['folder_jjmmtt'] = parse_bool(cfg.get("folder_jjmmtt", "true"))
        settings['folder_data']   = parse_bool(cfg.get("folder_data", "true"))
        settings['folder_output'] = parse_bool(cfg.get("folder_output", "true"))
        settings['folder_name']   = cfg.get("folder_name", "")
    else:
        log_message("Section [FOLDER] nicht gefunden in settings.ini – es werden Default-Werte genutzt.", level="warning")
        settings['folder_jjmmtt'] = True
        settings['folder_data']   = True
        settings['folder_output'] = True
        settings['folder_name']   = ""
    return settings

def ensure_folder_name_length(folder_name, max_length=MAX_FOLDER_NAME_LENGTH):
    """
    Prüft, ob der Ordnername länger als max_length ist.
    Falls ja, wird eine Error-Log-Meldung ausgegeben und ein Fallback-Name (Datum) verwendet.
    """
    if len(folder_name) > max_length:
        log_message(f"Ordnername '{folder_name}' ist zu lang (Länge {len(folder_name)} > {max_length}). Verwende Fallback-Name.", level="error")
        folder_name = dt.now().strftime("%y%m%d")
    return folder_name

def create_unique_folder(base_name):
    """
    Erstellt einen Ordner mit dem übergebenen Basisnamen.
    Falls der Ordner bereits existiert, wird ein Zähler (_01, _02, …) angehängt.
    Falls der Ordnername zu lang ist, wird dieser geprüft und ggf. gekürzt.
    Loggt dabei wichtige Schritte.
    """
    folder_name = base_name
    folder_name = ensure_folder_name_length(folder_name)  # Überprüfe die Länge
    
    counter = 1
    while os.path.exists(folder_name):
        log_message(f"Ordner '{folder_name}' existiert bereits. Erzeuge neuen Namen mit Zähler.", level="info")
        folder_name = f"{base_name}_{counter:02d}"
        folder_name = ensure_folder_name_length(folder_name)  # Auch hier prüfen
        counter += 1

    try:
        os.makedirs(folder_name)
        log_message(f"Ordner erstellt: '{folder_name}'", level="info")
    except Exception as e:
        log_message(f"Fehler beim Erstellen des Ordners '{folder_name}': {e}", level="error")
        raise

    return folder_name

def create_folder(custom_name=""):
    """
    Erstellt einen Ordner basierend auf den Einstellungen in der INI.

    Logik:
      - Falls folder_jjmmtt true ist, wird das Datum (jjmmtt) als Präfix verwendet.
      - Falls folder_data true ist und ein Custom-Name übergeben wurde, wird dieser als nächster Bestandteil genutzt.
      - Falls folder_output true ist und ein folder_name gesetzt ist, wird dieser als Zusatz angehängt.
    
    Falls keine der Bedingungen zutrifft, wird als Fallback das Datum genutzt.
    """
    settings = read_config()
    parts = []
    
    if settings['folder_jjmmtt']:
        parts.append(dt.now().strftime("%y%m%d"))
    
    if settings['folder_data'] and custom_name:
        parts.append(custom_name)
    
    if settings['folder_output'] and settings['folder_name']:
        parts.append(settings['folder_name'])
    
    # Fallback: Falls keine Komponente vorhanden ist, verwende das Datum
    if not parts:
        parts.append(dt.now().strftime("%y%m%d"))
    
    folder_base = "_".join(parts)
    return create_unique_folder(folder_base)




def create_output_folder(custom_name=""):
    """
    Erstellt ein Ausgabeverzeichnis basierend auf den Einstellungen in der INI.
    Verwendet die gleiche Logik wie create_folder().
    """
    return create_folder(custom_name)

# === Testaufrufe (nur ausgeführt, wenn _folder.py direkt gestartet wird) ===
if __name__ == "__main__":
    # Testbeispiele:
    folder_created = create_folder("textdokumen")
    log_message(f"Test: Folder created: {folder_created}", level="info")
    
    output_folder = create_output_folder("textdokumen")
    log_message(f"Test: Output Folder created: {output_folder}", level="info")
