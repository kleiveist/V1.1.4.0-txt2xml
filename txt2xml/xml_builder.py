import xml.etree.ElementTree as ET
import random

def generate_user_card_id():
    """
    Generiert eine zufällige 9-stellige Zahl als String.
    """
    return str(random.randint(600000000, 699999999))

def build_hint_block(hint_text):
    """
    Erzeugt XML-Elemente für den Hinweisbereich.
    
    - Teilt den gesamten Hinweistext in Absätze, getrennt durch mindestens eine leere Zeile.
    - Der erste Absatz wird als Beschreibung in einem <para> ausgegeben.
    - Weitere Absätze werden in eine <ul> mit <li>-Elementen verpackt.
    - In jedem Absatz werden Zeilen, die mit "Formel:" beginnen, als <formula> in einem <font size="18"> ausgegeben.
    """
    hint_text = hint_text.strip()
    if not hint_text:
        return []
    # Absätze: geteilte Blöcke durch mindestens doppelte Zeilenumbrüche
    paragraphs = hint_text.split("\n\n")
    elements = []
    # Ersten Absatz als beschreibenden Text ausgeben:
    desc_para = ET.Element("para")
    desc_font = ET.SubElement(desc_para, "font", {"size": "18"})
    desc_font.text = paragraphs[0].replace("\n", " ")  # innerer Zeilenumbruch als Leerzeichen
    # Optional: Ein <br/> hinzufügen
    desc_para.append(ET.Element("br"))
    elements.append(desc_para)
    
    # Weitere Absätze in eine Liste packen:
    if len(paragraphs) > 1:
        ul_elem = ET.Element("ul")
        for p in paragraphs[1:]:
            p = p.strip()
            if not p:
                continue
            li_elem = ET.Element("li")
            # Jede Zeile im Absatz
            for line in p.split("\n"):
                line = line.strip()
                if not line:
                    continue
                if line.startswith("Formel:"):
                    # Entferne den Marker "Formel:" und erstelle ein <formula>-Element
                    formula_text = line[len("Formel:"):].strip()
                    font_elem = ET.Element("font", {"size": "18"})
                    formula_elem = ET.SubElement(font_elem, "formula")
                    formula_elem.text = formula_text
                    li_elem.append(font_elem)
                    li_elem.append(ET.Element("br"))
                else:
                    font_elem = ET.Element("font", {"size": "18"})
                    font_elem.text = line
                    li_elem.append(font_elem)
                    li_elem.append(ET.Element("br"))
            ul_elem.append(li_elem)
        elements.append(ul_elem)
    return elements

def build_xml(cards, lesson_title, user_lesson_id="123456"):
    """
    Erzeugt einen XML-Baum mit folgender Struktur:
    
    <BYXML ...>
      <lesson title="lesson_title" userLessonID="user_lesson_id">
        <multiplechoicefilecard userCardID="...">
          <question>
            <para>
              <font size="18">Fragetext</font>
              <!-- Für jede in der Frage definierte Formel: -->
              <formula>...</formula>
            </para>
          </question>
          <mcAnswers>
            <mcAnswer correct="true/false">
              <answer>
                <para>
                  <font size="18">Antworttext</font>
                  <!-- Für jede in der Antwort definierte Formel: -->
                  <formula>...</formula>
                </para>
              </answer>
            </mcAnswer>
            ...
          </mcAnswers>
          <crib>
            <!-- Hinweisbereich wird in beschreibenden Teil und Liste aufgeteilt -->
          </crib>
        </multiplechoicefilecard>
        ...
      </lesson>
    </BYXML>
    """
    root = ET.Element("BYXML", {
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "version": "1.0",
        "xsi:noNamespaceSchemaLocation": "https://brainyoo.iu.org/Brainyoo2/xsd/brainyoo_xml_v2.0.xsd"
    })
    lesson = ET.SubElement(root, "lesson", {
        "title": lesson_title,
        "userLessonID": user_lesson_id
    })
    
    for card in cards:
        userCardID = generate_user_card_id()
        mcard = ET.SubElement(lesson, "multiplechoicefilecard", {"userCardID": userCardID})
        
        # Frage-Block:
        question_elem = ET.SubElement(mcard, "question")
        para_elem = ET.SubElement(question_elem, "para")
        font_elem = ET.SubElement(para_elem, "font", {"size": "18"})
        font_elem.text = card.get("question", "")
        # Hänge alle im Fragetext definierten Formeln an:
        for formula in card.get("question_formulas", []):
            formula_elem = ET.SubElement(para_elem, "formula")
            formula_elem.text = formula
        
        # Antworten-Block:
        mcAnswers_elem = ET.SubElement(mcard, "mcAnswers")
        for answer in card.get("answers", []):
            mcAnswer_elem = ET.SubElement(mcAnswers_elem, "mcAnswer", {"correct": answer.get("is_correct", "false")})
            answer_elem = ET.SubElement(mcAnswer_elem, "answer")
            para_ans = ET.SubElement(answer_elem, "para")
            font_ans = ET.SubElement(para_ans, "font", {"size": "18"})
            font_ans.text = answer.get("text", "")
            for formula in answer.get("formulas", []):
                formula_elem = ET.SubElement(para_ans, "formula")
                formula_elem.text = formula
        
        # Hinweis-Block (crib):
        if card.get("hint", ""):
            crib_elem = ET.SubElement(mcard, "crib")
            hint_nodes = build_hint_block(card.get("hint", ""))
            for node in hint_nodes:
                crib_elem.append(node)
        
    return root
