import logging
import configparser
import os
import textwrap
from datetime import datetime

# === SETTINGS EINLESEN AUS [LOGGER] ===
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.ini")
if not os.path.exists(config_path):
    raise FileNotFoundError("[ERROR] settings.ini not found!")
config.read(config_path)

def get_boolean(config, section, key, default=False):
    """Sichere Methode, um einen Boolean-Wert aus der INI-Datei zu laden."""
    try:
        value = config.get(section, key).strip().lower()
        if value in ["true", "1", "yes", "on"]:
            return True
        elif value in ["false", "0", "no", "off"]:
            return False
        else:
            print(f"[WARN] Ungültiger Wert für {section}.{key}: '{value}', verwende Default ({default}).")
            return default
    except (ValueError, KeyError):
        print(f"[WARN] Schlüssel {section}.{key} fehlt oder ist ungültig, verwende Default ({default}).")
        return default

# Logger-spezifische Einstellungen aus [LOGGER]
logger_folder   = get_boolean(config, "LOGGER", "logger_folder", default=False)
logging_enabled = get_boolean(config, "LOGGER", "logging_enabled", default=True)
console_output  = get_boolean(config, "LOGGER", "console_output", default=True)

# Globale Variablen für lazy initialization:
logging_initialized = False
_error_logger = None

def initialize_logging():
    """Initialisiert die Logging-Konfiguration (lazy)."""
    global logging_initialized, log_file
    if not logging_initialized:
        # Basisordner: Das Arbeitsverzeichnis (wo das Startskript ausgeführt wird)
        base_logger_dir = os.getcwd()
        if logger_folder:
            # Erstelle erst jetzt den Ordner, wenn er noch nicht existiert
            log_dir = os.path.join(base_logger_dir, "_log")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            log_file_path = os.path.join(log_dir, "log.txt")
        else:
            log_file_path = os.path.join(base_logger_dir, "log.txt")
        logging.basicConfig(
            filename=log_file_path,
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
            encoding="utf-8"
        )
        logging_initialized = True

def get_error_logger():
    """
    Lazy-Initialisierung des Error-Loggers.
    Dieser Logger schreibt in error_log.txt.
    """
    global _error_logger
    if _error_logger is None:
        # Basisordner: Arbeitsverzeichnis
        base_logger_dir = os.getcwd()
        if logger_folder:
            log_dir = os.path.join(base_logger_dir, "_log")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            error_log_path = os.path.join(log_dir, "error_log.txt")
        else:
            error_log_path = os.path.join(base_logger_dir, "error_log.txt")
        _error_logger = logging.getLogger("error_logger")
        _error_logger.propagate = False
        _error_logger.setLevel(logging.INFO)
        handler = logging.FileHandler(error_log_path, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
        _error_logger.addHandler(handler)
    return _error_logger

# === Weitere Helper-Funktionen ===
BASE_DIRECTORY = None

def init_logger(base_directory):
    """Initialisiert das Logging und speichert das Basisverzeichnis für verkürzte Pfade."""
    global BASE_DIRECTORY
    BASE_DIRECTORY = base_directory

    # Falls logging_enabled, erzwinge lazy initialization durch einen ersten Log-Eintrag
    if logging_enabled:
        log_separator()
        log_message("Working directory:", level="info")
        log_message(BASE_DIRECTORY, level="info")
        log_separator()
    # Error-Logger wird hier nicht explizit initialisiert – er wird beim ersten Bedarf erstellt.
    
def shorten_path(path, max_length=45):
    """
    Verkürzt lange Dateipfade mit "..." und zeigt sie relativ zu BASE_DIRECTORY an.
    """
    if BASE_DIRECTORY and path.startswith(BASE_DIRECTORY):
        relative_path = os.path.relpath(path, BASE_DIRECTORY)
        result = os.path.join("...", relative_path)
    else:
        result = path

    if len(result) > max_length:
        part_length = (max_length - 3) // 2
        result = f"{result[:part_length]}...{result[-part_length:]}"
    return result

def shorten_path_last_n(path, n=4):
    """Verkürzt den Pfad, sodass nur die letzten n Verzeichnisse + Dateiname angezeigt werden."""
    path_parts = path.split(os.sep)
    if len(path_parts) > n:
        return os.path.join("...", *path_parts[-n:])
    return path

def format_log_message(message):
    """Formatiert lange Log-Nachrichten (max. 90 Zeichen pro Zeile)."""
    return "\n".join(textwrap.wrap(message, width=90))

def log_message(message, level=None):
    """
    Schreibt eine Nachricht in den Hauptlog (z. B. log.txt).
    Wird ein Log-Level angegeben, erscheint ein entsprechendes Symbol vorangestellt.
    Zusätzlich werden Meldungen der Typen "warning", "error" und "delete"
    an den Error-Logger weitergeleitet (und somit in error_log.txt geschrieben).
    """
    if not logging_initialized and logging_enabled:
        initialize_logging()

    ICONS = {
        "info": "[INFO]",
        "warning": "[WARN]",
        "error": "[ERROR]",
        "delete": "[DELETE]"
    }
    formatted_message = format_log_message(message)
    if level:
        log_entry = f"{ICONS.get(level, '[INFO]')} {formatted_message}"
    else:
        log_entry = formatted_message

    if logging_enabled:
        logging.info(log_entry)

    if level in ["warning", "error", "delete"]:
        get_error_logger().info(log_entry)
        print(log_entry)
    elif console_output:
        print(log_entry)

def log_separator():
    """Fügt eine Trennlinie in den Log (und ggf. in der Konsole) ein."""
    log_message("-" * 66, level="info")

def log_sub_separator():
    """Fügt eine Untertrennlinie in den Log ein (z. B. zur Gruppierung von Dateioperationen)."""
    log_message("- " * 33, level="info")

# === Beispielhafte Nutzung ===
if __name__ == "__main__":
    init_logger(os.getcwd())
    log_message("Dies ist eine normale Info-Nachricht.", level="info")
    log_message("Dies ist eine Warnung!", level="warning")
    log_message("Dies ist eine Fehlernachricht!", level="error")
    log_message("Dies ist eine Löschmeldung.", level="delete")
    log_message("Noch eine Info ohne Level.")
