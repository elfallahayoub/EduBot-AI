# EduBot AI

Chatbot académique intelligent pour les étudiants universitaires marocains. Répond aux questions à partir des documents uploadés par l'étudiant (PDF, Word, PowerPoint, etc.) en utilisant une pipeline RAG complète.

---

## Architecture

```
EduBot AI
├── module1_lstm/        — Classification d'intention (LSTM)
├── module2_distilbert/  — Encodage sémantique (DistilCamemBERT)
├── module3_rag/         — Pipeline RAG (parsing, chunking, indexation, génération)
├── app/                 — Interface Streamlit
└── router.py            — Orchestrateur principal
```

**Pipeline complète :**

1. **LSTM** classifie l'intention (salutation, question documentaire, au revoir...)
2. **DistilCamemBERT** (`cmarkea/distilcamembert-base`) encode la question et les chunks
3. **FAISS** effectue la recherche vectorielle (similarité cosinus)
4. **Scoring hybride** re-classe les résultats : 40% sémantique + 60% correspondance mots-clés
5. **Gemini 2.0 Flash** génère une réponse en français à partir des extraits pertinents

---

## Fonctionnalités

- Upload de documents : PDF, DOCX, TXT, MD, PPTX, XLSX, CSV
- Sessions isolées par utilisateur (UUID, persistance disque, expiration 24h)
- Extraction PDF avec préservation de la structure des tableaux
- Normalisation des élisions françaises (`l'examen` → `examen`)
- Seuil de confiance : aucune réponse si le score < 0.50
- Fallback local si l'API Gemini est indisponible

---

## Installation

**Prérequis :** Python 3.10+, 4 GB RAM minimum

```bash
git clone https://github.com/<your-username>/EduBot-AI.git
cd EduBot-AI
pip install -r requirements.txt
```

Créez un fichier `.env` à la racine :

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

> Obtenez une clé gratuite sur [aistudio.google.com](https://aistudio.google.com)

---

## Utilisation

```bash
streamlit run app/app.py
```

Ouvrez [http://localhost:8501](http://localhost:8501), uploadez un document (ex. calendrier d'examens, règlement, emploi du temps), puis posez vos questions.

---

## Stack technique

| Composant | Technologie |
|---|---|
| Classification | TensorFlow / Keras (LSTM) |
| Embeddings | `cmarkea/distilcamembert-base` (HuggingFace) |
| Recherche vectorielle | FAISS (IndexFlatIP) |
| Génération | Gemini 2.0 Flash (`google-genai`) |
| Interface | Streamlit |
| Parsing PDF | pypdf (layout mode) |

---

## Variables d'environnement

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Clé API Google AI Studio |

Voir `.env.example` pour le modèle.

---

## Notes

- Le modèle LSTM (`module1_lstm/`) est pré-entraîné et ne doit pas être modifié.
- Le modèle DistilCamemBERT est téléchargé automatiquement par HuggingFace au premier lancement.
- Sur Windows avec peu de RAM, un chargeur streaming de poids est utilisé automatiquement pour contourner la limite du fichier de pagination.
