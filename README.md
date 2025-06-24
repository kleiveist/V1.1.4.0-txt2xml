# Brainyoo Karten XML Generator

Dieses Projekt ist ein **Kommandozeilen-Toolkit**, das aus strukturierten Textdateien Brainyoo-kompatible `.by2`-Karteikarten-Dateien erzeugt. Es unterstützt komplexe Multiple-Choice-Aufgaben inklusive LaTeX-Formeln und ist speziell für den Import in [https://brainyoo.iu.org/login](https://brainyoo.iu.org/login) (IU Internationale Hochschule) entwickelt.

---

## Features

- **Parser:** Wandelt klar strukturierte Text-Prompts (Format siehe unten) in interne Datenstrukturen um.
- **Export:** Erzeugt `by_content.xml` und packt diese in eine gültige `.by2`-Datei.
- **LaTeX-Unterstützung:** Alle Formeln bleiben im LaTeX-Format erhalten und werden korrekt in die XML eingebettet.
- **Konfigurierbares Ordner- und Logging-Management.**
- **Workaround:** Fallback-Mechanismus, falls der direkte Import in Brainyoo fehlschlägt.

---

## Projektstruktur
```md
├── _folder.py # Ordnerverwaltung & INI-Config  
├── _logger.py # Logging, gesteuert über INI  
├── archiver.py # Archivmanagement (.by2-Paketierung)  
├── b2y.py # .by2-Updater-Utility (nutzt 7-Zip)  
├── parser.py # Parser für Text → Datenstruktur  
├── xml_builder.py # XML-Erzeugung für Brainyoo  
├── settings.ini # Konfiguration  
├── lesson_xxx.by2 # Exportierte Template-.by2-Datei (für Plan B)  
├── Karteikarten.md # Beispielhafte Eingabedatei
```

---
## Voraussetzungen

- **Python 3.8+** (getestet mit 3.10)
- **7-Zip** installiert unter  
  `C:\Program Files\7-Zip\7z.exe` (notwendig für die .by2-Bearbeitung)
- **Windows-Betriebssystem** (Pfad zu 7-Zip ist hardcodiert)

---
## Schnelleinstieg

1. **Karteikarten-Textdatei erstellen**  
   Beachte das Format unten oder verwende die Beispiele aus [`Karteikarten.md`](Karteikarten.md).
	1. Verwende für LMM´s das [[PROMPT]] um die automatisiert Karteikarten erstellen zu lassen.

3. **`settings.ini` anpassen**  
   Logging und Ordnerstruktur nach Bedarf einstellen.

4. **Verarbeitung starten**  
   Ausführung im Projektordner, beispielhaft:

```Sh
   python parser.py deine_karteikarten.txt
   # Ausgabe: Struktur im Speicher
   python xml_builder.py
   # Ausgabe: by_content.xml im Output-Ordner
   python archiver.py
   # Paketiert die by_content.xml in eine .by2-Datei
```


Alternativ: .by2-Datei manuell aktualisieren:
```sh
python b2y.py pfad_zur.by2 pfad_zur/by_content.xml
```

---
```yaml
Karteikarte x: [Titel]
Frage:
[Fragetext ggf. mit:]
Formel: \( \text{LaTeX-Formel} \)

Antwortmöglichkeiten:
A) Korrekt/Falsch: [Antworttext]
Formel: \( \text{LaTeX-Formel} \)
B) ...
C) ...
D) ...

Hinweis:
[Hinweistext]
Formel: \( \text{LaTeX-Formel} \)

```

- Formeln immer im LaTeX-Format und wie gezeigt notieren.
- Reihenfolge und Schreibweise der Abschnitte **muss** eingehalten werden.
- Der Parser erkennt und extrahiert Formeln automatisch
Siehe `Karteikarten.md` für konkrete Beispiele.
---
## onfiguration (`settings.ini`)
- **[LOGGER]**: Steuerung des Loggings (Datei/Konsole).
- **[FOLDER]**: Einstellung der Ordnerstruktur (z. B. Datum, Suffix, Name).
- **[MODULS]**: Sonstige Optionen.

```ini
[LOGGER]
logger_folder = true
logging_enabled = true
console_output = false

[FOLDER]
folder_jjmmtt = true
folder_data = true
folder_output = true
folder_name = karteikarten
```

---
## Import-Probleme? Plan B (Fallback-Plan)

Manche `.by2`-Dateien werden von Brainyoo **nicht direkt akzeptiert**. Mit diesem Workaround kannst du trotzdem importieren:

**1. Exportiere eine gültige Lektion aus Brainyoo**
- Lade eine funktionierende `.by2`-Datei über die Website herunter.

**2. Ersetze die `by_content.xml` in diesem Archiv**
- Kopiere die exportierte `.by2`-Datei in deinen Output-Ordner.
- Öffne sie mit 7-Zip (oder kompatiblem Archiv-Tool).
- Ersetze die enthaltene `by_content.xml` durch die von diesem Tool erzeugte Datei.
- Archiv speichern.

**3. Importiere die geändete Datei erneut**
- Die .by2-Datei sollte nun problemlos importierbar sein, da alle Metadaten der Website entsprechen.

---
## Wichtige Module
- **_folder.py**  
    Dynamische und eindeutige Ordnererstellung, liest Konfiguration.
- **_logger.py**  
    Eigenes Logging-Modul, unterstützt verschiedene Log-Level und Ausgabepfade.
- **parser.py**  
    Strikter Textparser für das Karteikarten-Format.
- **xml_builder.py**  
    Baut den XML-Output entsprechend der Brainyoo-Struktur.
- **archiver.py & b2y.py**  
    Automatisches oder manuelles Verpacken/Ersetzen der XML in .by2-Dateien per 7-Zip.
---
## Troubleshooting

- **7-Zip nicht gefunden:**  
    Passe den Pfad zu 7-Zip in `archiver.py` und `b2y.py` an.
    
- **Keine .by2-Datei gefunden:**  
    Lege eine .by2-Template-Datei im Skriptordner ab.
    
- **Import wird abgelehnt:**  
    Nutze „Plan B“ wie oben beschrieben.
    
- **Logging funktioniert nicht:**  
    `logging_enabled = true` setzen und Schreibrechte prüfen.
    
---
## Lizenz
MIT License (siehe [[LICENSE.md]]

---
## Credits
Entwickelt für fortgeschrittene, formelreiche MC-Karteikarten an der [IU Internationale Hochschule](https://iu.org/).