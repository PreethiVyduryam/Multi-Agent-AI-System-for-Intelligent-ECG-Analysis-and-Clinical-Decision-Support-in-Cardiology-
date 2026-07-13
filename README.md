# 🫀 Multi-Agent AI System for Intelligent ECG Analysis and Clinical Decision Support in Cardiology

A cardiology relate multi-agent AI decision-support system that combines multilple agents such as a Large Language Model (LLM), Retrieval-Augmented Generation (RAG), ECG analysis, patient memory, and safety-aware reasoning in a web application.

---

# Overview

This project was developed as an academic prototype to explore how modern Artificial Intelligence techniques can support cardiology-related clinical decision making in a more efficient  and evidence-grounded manner.

Unlike a traditional chatbot, the system is designed as a modular multi-agent architecture which:

- Accepts structured patient information
- Uses Google's Gemini model for clinical reasoning
- Retrieves supporting evidence from a local Retrieval-Augmented Generation (RAG) knowledge repository
- Integrates ECG analysis tools
- Stores patient history across consultations
- Applies a safety layer before presenting results
- Provides a Flask-based web interface

The project was developed as part of an MSc Data Science and Computational Intelligence dissertation exploring the use of Multi-Agent AI and Retrieval-Augmented Generation for intelligent ECG analysis and clinical decision support in Cardiology.

-------

# Features

- Structured patient assessment form
- AI-assisted cardiology report generation
- Google Gemini API integration
- ECG interpretation support
- Retrieval-Augmented Generation (RAG)
- Local structured clinical knowledge repository
- NICE guideline evidence retrieval
- ESC guideline evidence retrieval
- Peer-reviewed research evidence retrieval
- SQLite-based patient history memory
- Safety layer with clinician review safeguards
- Demo patient case loading
- Patient history viewer
- Automated testing using pytest

------

# Research Contribution

This project extends an existing multi-agent cardiology decision-support prototype by integrating a Retrieval-Augmented Generation (RAG) pipeline.

The enhancement retrieves relevant evidence from a structured local clinical knowledge repository containing summaries of NICE clinical guidelines, ESC clinical guidelines, and peer-reviewed research before generating clinical reasoning.
Grounding AI-generated recommendations in a curated evidence improves transparency, supports clinician review and reduces the likelihood of unsupported responses while maintaining patient safety through an additional safety validation layer.

--------

# Tech Stack

| Component | Technology |
|------------|------------|
| Programming Language | Python |
| Web Framework | Flask |
| Database | SQLite |
| Large Language Model | Google Gemini |
| Knowledge Repository | JSON |
| Evidence Retrieval | Local Retrieval-Augmented Generation (RAG) |
| Environment Variables | python-dotenv |
| Testing | pytest |

---

## Project Structure

The project follows a modular structure organised into separate components.

- `app/` – Core application modules.
- `app/services/` – AI reasoning and supporting services.
- `app/tools/` – ECG analysis and supporting tools.
- `app/rag/` – Retrieval-Augmented Generation components and local knowledge repository.
- `app/models/` – Patient data models.
- `app/db/` – Database operations.
- `templates/` – HTML templates.
- `static/` – CSS and static assets.
- `tests/` – Unit tests.

---

# How to Run

## 1. Clone the repository

```bash
git clone <repository-url>
cd Multi-Agent-AI-System-for-Intelligent-ECG-Analysis-and-Clinical-Decision-Support-in-Cardiology
```

---

## 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it.

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Create an API key file

Create a file named:

```text
apikey.env
```

Add the following:

```text
GEMINI_API_KEY=your_gemini_api_key

NCBI_TOOL=cardiology_agent
NCBI_EMAIL=your_email@example.com
```

Generate a Gemini API key using Google AI Studio and replace `your_gemini_api_key` with your own key.

---

## 5. Run the application

```bash
python web_app.py
```

Open your browser and navigate to:

```text
http://127.0.0.1:5000
```

---

# Running Tests

Run the automated test suite using:

```bash
pytest
```

---

# Example Workflow

1. Enter patient demographics, symptoms, vital signs, ECG description, medical history, and clinician question.
2. The application validates the patient information.
3. The RAG module retrieves relevant evidence from the local clinical knowledge repository.
4. Google's Gemini model generates evidence-grounded clinical reasoning.
5. ECG analysis tools provide additional clinical decision support.
6. The safety layer reviews the generated report and applies appropriate safety disclaimers.
7. A structured assessment report is presented and stored in the patient history database.

---

# Safety Notice

This project is an academic prototype developed for research and educational purposes only.

It is **not** a medical device, **not** a diagnostic system, and **must not** be used for real-world clinical decision making.

All generated outputs are intended solely as decision-support information and must always be reviewed by a qualified healthcare professional.

---

# Limitations

- ECG interpretation is based on ECG descriptions rather than raw ECG waveform data.
- The knowledge repository contains curated summaries rather than full clinical guideline documents.
- Evidence retrieval currently uses keyword-based matching rather than semantic vector retrieval.
- AI-generated outputs may still contain inaccuracies and require clinician review.
- The system has not undergone formal clinical validation.

---

# Future Improvements

- Semantic retrieval using vector databases (e.g., FAISS or ChromaDB)
- Integration with real ECG waveform analysis
- Multimodal ECG image interpretation
- Clinical evaluation with cardiologists
- Integration with Electronic Health Record (EHR) systems
- Containerised deployment using Docker and cloud infrastructure

---

# Academic Context

This project was developed as part of an MSc Data Science and Computational Intelligence dissertation investigating the application of Multi-Agent Artificial Intelligence, Retrieval-Augmented Generation (RAG), a Large Language Model (LLM),  and clinical decision support systems for intelligent ECG analysis and evidence-grounded cardiology decision support.

---

# Author

**Preethi Vyduryam**

MSc Computing Dissertation Project
