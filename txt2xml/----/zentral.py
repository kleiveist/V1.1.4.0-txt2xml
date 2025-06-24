import os

def main():
    # Name der Ausgabedatei
    output_filename = "zusammenfassung.txt"
    
    # Den Namen des aktuell laufenden Skripts ermitteln, um es ggf. auszuschließen
    script_name = os.path.basename(__file__)
    
    # Alle .py- und .ini-Dateien im aktuellen Verzeichnis auflisten (das eigene Skript wird ausgelassen)
    dateien = [f for f in os.listdir('.') 
               if (f.endswith('.py') or f.endswith('.ini')) and f != script_name]
    
    # Alphabetische Sortierung der Dateien (optional)
    dateien.sort()
    
    with open(output_filename, "w", encoding="utf-8") as output_file:
        for file in dateien:
            # Kopfzeile zur Trennung der Dateien
            output_file.write("#" * 80 + "\n")
            output_file.write(f"# Datei: {file}\n")
            output_file.write("#" * 80 + "\n\n")
            
            # Inhalt der jeweiligen Datei einlesen und in die Ausgabedatei schreiben
            try:
                with open(file, "r", encoding="utf-8") as input_file:
                    output_file.write(input_file.read())
            except Exception as e:
                output_file.write(f"Fehler beim Lesen der Datei: {e}\n")
            
            # Leerzeilen als Trenner zwischen den Dateien
            output_file.write("\n\n")
    
    print(f"Zusammenfassung wurde in '{output_filename}' gespeichert.")

if __name__ == "__main__":
    main()
