import sys
sys.path.insert(0, '.')
from module3_rag.rag_engine import answer_question
from module3_rag.session_manager import create_session, add_file_to_session, cleanup_session
import tempfile

sid = create_session()
content = (
    "Calendrier des examens\n"
    "Mathematiques 15 juin 2026 09h00 Salle 204 Examen final\n"
    "Algorithmique 16 juin 2026 09h00 Salle 101 Examen final\n"
    "Reseaux 23 juin 2026 14h00 Salle 101 Examen final\n"
    "Session rattrapage toutes matieres 8 au 12 juillet 2026\n"
    "Regles: carte etudiant obligatoire. Arrivee 15 min avant.\n"
)
with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
    f.write(content)
    p = f.name

add_file_to_session(sid, p, display_name="calendrier.txt")

tests = [
    ("quand est l examen de mathematiques", "15 juin 2026", False),
    ("dans quelle salle est l examen de reseaux", "Salle 101", False),
    ("c est quoi l archetecture", None, True),
    ("bonjour comment ca va", None, True),
    ("qui a invente python", None, True),
]

print("Question" + " " * 38 + "Conf    Source          OK?")
print("-" * 80)
score = 0
for q, expected, expect_no_source in tests:
    r = answer_question(q, session_id=sid)
    conf = r["confidence"]
    src  = r.get("source") or "none"
    if expect_no_source:
        ok = r["source"] is None
    else:
        ok = expected.lower() in r["answer"].lower()
    status = "OK " if ok else "NOK"
    if ok:
        score += 1
    print(f"{status}  {q[:42]:<42}  {conf:.0%}  {src[:18]:<18}")

cleanup_session(sid)
print(f"\nScore: {score}/{len(tests)}")
