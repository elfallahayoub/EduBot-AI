import sys
import tempfile
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import SUPPORTED_EXTENSIONS, MAX_FILES_PER_SESSION
from router import process_message
from module3_rag.session_manager import (
    create_session,
    add_file_to_session,
    list_session_files,
    cleanup_session,
)

st.set_page_config(
    page_title="EduBot AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .file-item {
        background: #f0f4f8;
        border-left: 3px solid #4CAF50;
        padding: 6px 10px;
        border-radius: 4px;
        margin-bottom: 6px;
        font-size: 0.85rem;
        color: #333;
    }

    .confidence-badge {
        display: inline-block;
        background: #e8f4fd;
        color: #1a73e8;
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 10px;
        margin-top: 4px;
    }
    </style>
""", unsafe_allow_html=True)


def init_state():
    if "session_id" not in st.session_state:
        st.session_state.session_id = create_session()
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": (
                "Bonjour ! Je suis EduBot, votre assistant académique. "
                "Uploadez un document de votre université dans le panneau de gauche "
                "(PDF, Word, TXT, PowerPoint...), puis posez-moi vos questions !"
            ),
            "source": None,
            "confidence": None,
        }]
    if "indexed_files" not in st.session_state:
        st.session_state.indexed_files = set()


def new_session():
    cleanup_session(st.session_state.session_id)
    st.session_state.session_id = create_session()
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Nouvelle session démarrée. Uploadez vos documents et posez vos questions !",
        "source": None,
        "confidence": None,
    }]
    st.session_state.indexed_files = set()


def handle_upload(uploaded_file):
    if uploaded_file.name in st.session_state.indexed_files:
        return

    current_files = list_session_files(st.session_state.session_id)
    if len(current_files) >= MAX_FILES_PER_SESSION:
        st.sidebar.error(f"Limite de {MAX_FILES_PER_SESSION} fichiers par session atteinte.")
        return

    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name

    try:
        with st.sidebar.spinner(f"Indexation de {uploaded_file.name}..."):
            add_file_to_session(st.session_state.session_id, tmp_path, display_name=uploaded_file.name)
        st.session_state.indexed_files.add(uploaded_file.name)
        st.sidebar.success(f"'{uploaded_file.name}' indexé avec succès !")
    except ValueError as e:
        st.sidebar.error(str(e))
    except Exception as e:
        st.sidebar.error(f"Erreur lors de l'indexation : {e}")


def sidebar():
    with st.sidebar:
        st.markdown("## EduBot AI")
        st.caption("Assistant académique personnel")
        st.divider()

        st.markdown("### Vos documents")
        st.caption(f"Formats acceptés : PDF, Word, TXT, PPTX, Excel, CSV — max {MAX_FILES_PER_SESSION} fichiers")

        allowed = [ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS]
        uploaded = st.file_uploader(
            "Glissez votre document ici",
            type=allowed,
            label_visibility="collapsed",
        )
        if uploaded:
            handle_upload(uploaded)

        indexed = list_session_files(st.session_state.session_id)
        if indexed:
            st.markdown("**Fichiers indexés :**")
            for name in indexed:
                st.markdown(f'<div class="file-item">{name}</div>', unsafe_allow_html=True)
        else:
            st.info("Aucun document chargé pour l'instant.")

        st.divider()
        if st.button("Nouvelle session", use_container_width=True, type="secondary"):
            new_session()
            st.rerun()

        st.divider()
        st.caption("EduBot AI — Projet portfolio IA")


def chat():
    st.markdown("## Posez vos questions")
    st.caption("Les réponses sont extraites de vos documents uploadés.")
    st.divider()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("source") and msg.get("confidence") is not None:
                st.markdown(
                    f'<span class="confidence-badge">Source : {msg["source"]} — '
                    f'Confiance : {msg["confidence"]:.0%}</span>',
                    unsafe_allow_html=True,
                )

    if prompt := st.chat_input("Votre question..."):
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "source": None,
            "confidence": None,
        })

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Recherche dans vos documents..."):
                result = process_message(prompt, session_id=st.session_state.session_id)

            st.write(result["answer"])

            if result.get("source") and result.get("confidence"):
                st.markdown(
                    f'<span class="confidence-badge">Source : {result["source"]} — '
                    f'Confiance : {result["confidence"]:.0%}</span>',
                    unsafe_allow_html=True,
                )

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "source": result.get("source"),
            "confidence": result.get("confidence"),
        })


def main():
    init_state()
    sidebar()
    chat()


if __name__ == "__main__":
    main()
