import re

def parse_txt_file(filepath):
    """
    Liest die Textdatei ein und extrahiert Karteikarten.
    
    Erkannt werden:
      - "Karteikarte ..." als Beginn eines neuen Blocks.
      - "Frage:" leitet den Fragetext ein.
      - "Antwortmöglichkeiten:" leitet den Antwortenbereich ein.
      - Antworten beginnen mit einem Großbuchstaben und ")" und enthalten entweder "Korrekt:" oder "Falsch:".
      - "Hinweis:" leitet den Hinweistext ein.
      - "Formel:" in Frage, Antwort oder Hinweis wird als Formel erkannt.
      
    Im Hinweisbereich werden leere Zeilen nicht übersprungen, um Absatz-Trennungen zu ermöglichen.
    """
    cards = []
    current_card = None
    state = None  # Mögliche Zustände: None, 'question', 'answers', 'hint'
    question_lines = []
    answer_list = []  # Liste von Antwort-Dictionaries: {"is_correct": ..., "text": ..., "formulas": []}
    hint_lines = []
    question_formulas = []  # Liste von Formeln im Fragetext

    with open(filepath, 'r', encoding='utf-8') as f:
        for raw_line in f:
            # Entferne nur den Zeilenumbruch, aber nicht alle Leerzeichen (damit im Hint leere Zeilen erhalten bleiben)
            line = raw_line.rstrip("\n")
            # Für alle Zustände außer "hint" überspringen wir komplett leere Zeilen:
            if state != 'hint' and line.strip() == "":
                continue

            if line.startswith("Karteikarte"):
                if current_card is not None:
                    current_card['question'] = "\n".join(question_lines).strip()
                    current_card['question_formulas'] = question_formulas[:]
                    current_card['answers'] = answer_list[:]
                    # Im Hinweis werden die Zeilen per "\n" zusammengefügt (so bleiben Absätze erhalten)
                    current_card['hint'] = "\n".join(hint_lines).rstrip()
                    cards.append(current_card)
                current_card = {}
                m = re.match(r"Karteikarte\s+(\d+):\s*(.*)", line)
                if m:
                    current_card['id'] = m.group(1)
                    current_card['title'] = m.group(2)
                else:
                    current_card['id'] = ""
                    current_card['title'] = ""
                state = None
                question_lines = []
                answer_list = []
                hint_lines = []
                question_formulas = []
                continue

            if line.startswith("Frage:"):
                state = 'question'
                q = line[len("Frage:"):].strip()
                if q:
                    question_lines.append(q)
                continue

            if line.startswith("Antwortmöglichkeiten:"):
                state = 'answers'
                continue

            if line.startswith("Hinweis:"):
                state = 'hint'
                h = line[len("Hinweis:"):].strip()
                if h:
                    hint_lines.append(h)
                continue

            # Verarbeitung je nach Zustand:
            if state == 'question':
                if line.startswith("Formel:"):
                    formula_text = line[len("Formel:"):].strip()
                    question_formulas.append(formula_text)
                else:
                    question_lines.append(line.strip())
            elif state == 'answers':
                if line.startswith("Formel:"):
                    if answer_list:
                        formula_text = line[len("Formel:"):].strip()
                        if "formulas" not in answer_list[-1]:
                            answer_list[-1]["formulas"] = []
                        answer_list[-1]["formulas"].append(formula_text)
                else:
                    m = re.match(r"([A-Z])\)\s*(Korrekt:|Falsch:)\s*(.*)", line)
                    if m:
                        is_correct = "true" if "Korrekt" in m.group(2) else "false"
                        answer_text = m.group(3).strip()
                        answer_list.append({
                            "is_correct": is_correct,
                            "text": answer_text,
                            "formulas": []
                        })
            elif state == 'hint':
                # Im Hint-Zustand speichern wir auch leere Zeilen, um Absätze zu trennen
                hint_lines.append(line)
    
    if current_card is not None:
        current_card['question'] = "\n".join(question_lines).strip()
        current_card['question_formulas'] = question_formulas[:]
        current_card['answers'] = answer_list[:]
        current_card['hint'] = "\n".join(hint_lines).rstrip()
        cards.append(current_card)
    
    return cards
