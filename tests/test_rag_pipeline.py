"""
Full end-to-end test of the EduBot RAG pipeline.
Creates 4 demo PDFs matching the user's test documents, then runs all questions.
"""
import sys
import os
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fpdf import FPDF


# ──────────────────────────────────────────────
# PDF CREATION
# ──────────────────────────────────────────────

def _make_pdf(path: str, title: str, rows: list, extra_sections: dict = None):
    """Create a PDF with a header, an optional table of rows, and extra text sections."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Use built-in helvetica (no unicode issues with basic French chars via latin-1)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, title.encode("latin-1", errors="replace").decode("latin-1"), ln=True, align="C")
    pdf.ln(4)

    if rows:
        pdf.set_font("Helvetica", size=9)
        # Compute column widths
        col_count = len(rows[0])
        col_w = 190 // col_count
        for i, row in enumerate(rows):
            if i == 0:
                pdf.set_font("Helvetica", "B", 9)
            else:
                pdf.set_font("Helvetica", size=9)
            for cell in row:
                txt = str(cell).encode("latin-1", errors="replace").decode("latin-1")
                pdf.cell(col_w, 7, txt, border=1)
            pdf.ln()

    if extra_sections:
        pdf.ln(6)
        for section_title, section_body in extra_sections.items():
            pdf.set_font("Helvetica", "B", 11)
            t = section_title.encode("latin-1", errors="replace").decode("latin-1")
            pdf.cell(0, 8, t, ln=True)
            pdf.set_font("Helvetica", size=9)
            b = section_body.encode("latin-1", errors="replace").decode("latin-1")
            pdf.multi_cell(0, 5, b)
            pdf.ln(3)

    pdf.output(path)


def create_test_pdfs(dest_dir: str) -> dict:
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    paths = {}

    # ── PDF 1 : Calendrier des examens ──
    p = str(dest / "1_Calendrier_Examens.pdf")
    _make_pdf(p,
        "Calendrier des Examens - Session de Printemps 2026",
        rows=[
            ["Matiere", "Date", "Heure", "Salle", "Duree"],
            ["Mathematiques", "15 juin 2026", "09h00", "Salle 204", "2h00"],
            ["Algorithmique", "16 juin 2026", "09h00", "Salle 101", "2h30"],
            ["Physique", "17 juin 2026", "14h00", "Amphi B", "2h00"],
            ["Anglais", "18 juin 2026", "10h30", "Salle 305", "1h30"],
            ["Chimie organique", "19 juin 2026", "09h00", "Labo 3", "2h00"],
            ["Bases de donnees", "22 juin 2026", "09h00", "Salle 201", "2h30"],
            ["Reseaux", "23 juin 2026", "14h00", "Salle 101", "2h00"],
            ["Statistiques", "24 juin 2026", "09h00", "Salle 204", "2h00"],
            ["Economie generale", "25 juin 2026", "10h30", "Amphi A", "1h30"],
            ["Systemes d'exploitation", "26 juin 2026", "09h00", "Salle 102", "2h00"],
            ["Session rattrapage - toutes matieres", "8 au 12 juillet 2026", "Selon convocation", "Voir affichage", "-"],
        ],
        extra_sections={
            "Regles": (
                "Les etudiants doivent se presenter quinze minutes avant le debut de chaque epreuve, "
                "munis de leur carte etudiant et d'une piece d'identite. "
                "Toute absence non justifiee entraine la note zero. "
                "Les resultats sont publies sur le portail etudiant deux semaines apres la fin des examens."
            )
        }
    )
    paths["calendrier"] = p

    # ── PDF 2 : Catalogue des cours ──
    p = str(dest / "2_Catalogue_Cours.pdf")
    _make_pdf(p,
        "Catalogue des Cours - Licence Informatique 2025-2026",
        rows=[
            ["N", "Titre du module", "Description", "Credits"],
            ["1", "Algorithmique et structures de donnees", "Variables, boucles, tableaux, listes chainees, complexite algorithmique.", "5"],
            ["2", "Bases de donnees relationnelles", "Modelisation entite-association, langage SQL, normalisation.", "4"],
            ["3", "Reseaux informatiques", "Modele OSI, protocoles TCP/IP, configuration reseau de base.", "4"],
            ["4", "Mathematiques appliquees", "Algebre lineaire, analyse, probabilites pour l'informatique.", "5"],
            ["5", "Programmation orientee objet", "Classes, heritage, polymorphisme en Python et Java.", "5"],
            ["6", "Systemes d'exploitation", "Gestion des processus, de la memoire et des fichiers sous Linux.", "4"],
            ["7", "Intelligence artificielle - Introduction", "Notions de machine learning et de reseaux de neurones.", "4"],
            ["8", "Anglais technique", "Vocabulaire informatique, redaction de documentation technique.", "2"],
            ["9", "Genie logiciel", "Cycle de vie des projets, methodes agiles, Git.", "3"],
            ["10", "Securite informatique", "Cryptographie de base, securisation des applications web.", "3"],
        ],
        extra_sections={
            "Volume horaire": (
                "Chaque module comprend en moyenne 20 heures de cours magistral, "
                "15 heures de travaux diriges et 10 heures de travaux pratiques."
            )
        }
    )
    paths["catalogue"] = p

    # ── PDF 3 : Guide d'inscription ──
    p = str(dest / "3_Guide_Inscription.pdf")
    _make_pdf(p,
        "Guide d'Inscription - Procedure 2026",
        rows=[
            ["Etape", "Date limite"],
            ["Ouverture des inscriptions en ligne", "1er juillet 2026"],
            ["Date limite de depot du dossier", "30 juillet 2026"],
            ["Confirmation definitive de l'inscription", "15 aout 2026"],
            ["Rentree universitaire", "8 septembre 2026"],
        ],
        extra_sections={
            "Documents a fournir": (
                "Pour finaliser votre inscription, vous devez deposer : copie legalisee du baccalaureat, "
                "quatre photos d'identite recentes, copie de la carte nationale, certificat medical de moins de trois mois, "
                "formulaire d'inscription signe. Les dossiers incomplets ne seront pas traites."
            ),
            "Frais d'inscription": (
                "Les frais d'inscription s'elevent a 1200 dirhams pour les etudiants marocains "
                "et 3500 dirhams pour les etudiants internationaux. "
                "Une reduction de 20% est accordee aux etudiants boursiers."
            ),
            "Procedure": (
                "1. Creez votre compte sur le portail avec votre numero de baccalaureat. "
                "2. Remplissez le formulaire. 3. Telechargez les documents. "
                "4. Payez les frais. 5. Presentez-vous au service de scolarite avec les originaux."
            ),
        }
    )
    paths["inscription"] = p

    # ── PDF 4 : Guide de réussite étudiante ──
    p = str(dest / "4_Guide_Reussite.pdf")
    _make_pdf(p,
        "Guide de Reussite Etudiante",
        rows=[],
        extra_sections={
            "Soutien academique": (
                "Les etudiants en difficulte peuvent prendre rendez-vous avec le responsable pedagogique "
                "pour etablir un plan de rattrapage personnalise. "
                "Des seances de soutien gratuites sont organisees chaque semaine pour les modules "
                "d'algorithmique, de mathematiques appliquees et de systemes d'exploitation. "
                "Les inscriptions aux seances de soutien se font aupres du secretariat pedagogique."
            ),
            "Que faire en cas d'echec": (
                "En cas de note insuffisante, l'etudiant a automatiquement acces a la session de rattrapage en juillet. "
                "Il est recommande de revoir les exercices corriges et de participer aux seances de revision. "
                "Un entretien individuel avec l'enseignant permet d'identifier les points a retravailler."
            ),
            "Methodologie de travail": (
                "Il est conseille de consacrer au moins deux heures de revision personnelle "
                "pour chaque heure de cours magistral. La regularite est plus efficace que les revisions intensives. "
                "Travailler en petits groupes de trois a quatre etudiants aide a mieux comprendre."
            ),
            "Soutien psychologique": (
                "L'universite met a disposition un service d'ecoute psychologique gratuit et confidentiel "
                "pour tous les etudiants qui ressentent du stress ou de l'anxiete. "
                "Les rendez-vous peuvent etre pris directement aupres du bureau des affaires estudiantines."
            ),
        }
    )
    paths["reussite"] = p

    return paths


# ──────────────────────────────────────────────
# PIPELINE TEST
# ──────────────────────────────────────────────

def run_tests():
    from module3_rag.document_parser import parse_document
    from module3_rag.text_chunker import chunk_text
    from module3_rag.session_manager import create_session, add_file_to_session, cleanup_session
    from module3_rag.rag_engine import answer_question

    tmp_dir = tempfile.mkdtemp(prefix="edubot_test_")
    try:
        print("=" * 70)
        print("  CREATION DES PDFs DE TEST")
        print("=" * 70)
        pdf_paths = create_test_pdfs(tmp_dir)
        for k, p in pdf_paths.items():
            print(f"  [OK] {Path(p).name}")

        print()
        print("=" * 70)
        print("  ETAPE 1 - PARSING (parse_document)")
        print("=" * 70)
        parsed_texts = {}
        for key, path in pdf_paths.items():
            text = parse_document(path)
            parsed_texts[key] = text
            lines = [l for l in text.split("\n") if l.strip()]
            print(f"\n[{key}] {len(text)} chars, {len(lines)} lignes")
            for i, line in enumerate(lines[:20]):
                print(f"  L{i+1:02d}: {line[:100]}")
            if len(lines) > 20:
                print(f"  ... ({len(lines) - 20} lignes supplementaires)")

        print()
        print("=" * 70)
        print("  ETAPE 2 - CHUNKING (chunk_text)")
        print("=" * 70)
        all_chunks = {}
        for key, text in parsed_texts.items():
            chunks = chunk_text(text)
            all_chunks[key] = chunks
            print(f"\n[{key}] -> {len(chunks)} chunks")
            for i, chunk in enumerate(chunks):
                lines_in_chunk = [l for l in chunk.split("\n") if l.strip()]
                print(f"  Chunk {i+1:02d} ({len(lines_in_chunk)} lignes): {chunk[:120].replace(chr(10), ' | ')}")

        print()
        print("=" * 70)
        print("  ETAPE 3 - INDEXATION (add_file_to_session)")
        print("=" * 70)
        session_id = create_session()
        print(f"Session: {session_id[:8]}...")
        for key, path in pdf_paths.items():
            result = add_file_to_session(session_id, path, display_name=Path(path).name)
            print(f"  [{key}] {result['file']} -> {result['chunks']} chunks indexes")

        print()
        print("=" * 70)
        print("  ETAPE 4 - QUESTIONS (answer_question)")
        print("=" * 70)

        questions = [
            ("quand est l'examen de mathematiques ?",
             "15 juin 2026"),
            ("dans quelle salle est l'examen de reseaux ?",
             "Salle 101"),
            ("quel est le titre du module 7 ?",
             "Intelligence artificielle"),
            ("c'est quoi le contenu du cours de bases de donnees ?",
             "SQL"),
            ("quels documents dois-je fournir pour m'inscrire ?",
             "baccalaureat"),
            ("quelle est la date limite d'inscription ?",
             "30 juillet 2026"),
            ("j'ai des difficultes en algorithmique, que faire ?",
             "soutien"),
            ("est-ce qu'il y a un soutien psychologique ?",
             "confidentiel"),
        ]

        results_table = []
        for question, expected_keyword in questions:
            result = answer_question(question, session_id=session_id, top_k=3)
            answer  = result.get("answer", "")
            source  = result.get("source", "")
            conf    = result.get("confidence", 0)
            correct = expected_keyword.lower() in answer.lower()

            results_table.append({
                "question": question,
                "answer":   answer[:200],
                "source":   source,
                "conf":     conf,
                "correct":  correct,
                "keyword":  expected_keyword,
            })

            status = "OK" if correct else "FAIL"
            print(f"\n[{status}] Q: {question}")
            print(f"       Mot-clé attendu : '{expected_keyword}'")
            print(f"       Source : {source} | Confiance : {conf:.0%}")
            print(f"       R: {answer[:250]}")

        cleanup_session(session_id)

        print()
        print("=" * 70)
        print("  TABLEAU RECAPITULATIF")
        print("=" * 70)
        ok_count = sum(1 for r in results_table if r["correct"])
        print(f"\n{'Question':<50} {'Mot-clé':<20} {'OK?':<6} {'Conf'}")
        print("-" * 85)
        for r in results_table:
            status = "YES" if r["correct"] else "NO "
            print(f"{r['question'][:48]:<50} {r['keyword']:<20} {status:<6} {r['conf']:.0%}")
        print("-" * 85)
        print(f"Score : {ok_count}/{len(results_table)}")

        return results_table

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    run_tests()
