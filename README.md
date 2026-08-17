# 🫀 Multi-Agent AI System for Intelligent ECG Analysis and Clinical Decision Support in Cardiology

A cardiology relate multi-agent AI decision-support system that combines multilple agents such as a Large Language Model (LLM), Retrieval-Augmented Generation (RAG), ECG analysis, patient memory, and safety-aware reasoning in a web application.

---

# Overview

This project presents an academic prototype of a multi-agent Artificial Intelligence (AI) system for ECG-related clinical decision support in cardiology.

The project extends an existing cardiology decision-support prototype by integrating specialised AI components and a local Retrieval-Augmented Generation (RAG) framework. The enhanced system separates clinical information extraction, evidence retrieval, clinical reasoning and report generation into different stages.

The system processes structured patient information, ECG-related findings and previous patient history. Relevant clinical evidence is retrieved from a local knowledge repository and combined with outputs from multiple AI components to generate a structured cardiology decision-support report.

The main components of the enhanced system are:

- FLAN-T5 for clinical information extraction
- Local RAG for clinical evidence retrieval
- DeepSeek-R1 for specialised clinical reasoning
- Google Gemini for final report generation
- Deterministic safety layer for output validation
- ECG analysis support
- SQLite-based patient history
- Flask-based web interface

The system was developed as part of an MSc Data Science and Computational Intelligence research project.

------

## Research Contribution

The main contribution of this project is the enhancement of an existing cardiology decision-support prototype through the integration of specialised AI components and a local RAG framework.

The original prototype relied mainly on Gemini for clinical reasoning and report generation, supported by ECG analysis, patient history and existing safety mechanisms.

The enhanced system introduces FLAN-T5 for clinical information extraction, RAG for evidence retrieval and DeepSeek-R1 for a separate clinical reasoning stage. Gemini then integrates the patient information, extracted information, ECG analysis, patient history, retrieved evidence and reasoning into the final cardiology decision-support report.

The RAG knowledge repository contains selected clinical information derived from NICE guidance, European Society of Cardiology (ESC) guidance and relevant research material.

The safety layer is applied to the generated output before it is presented to the user. The system is designed to support clinical decision-making rather than provide autonomous diagnosis or treatment.

-------

# Features

- Structured patient assessment
- Patient demographic information
- Symptoms and medical history
- ECG analysis support
- FLAN-T5 clinical information extraction
- Local Retrieval-Augmented Generation (RAG)
- Curated clinical knowledge repository
- NICE guideline evidence retrieval
- ESC guideline evidence retrieval
- Selected research evidence retrieval
- DeepSeek-R1 clinical reasoning
- Gemini-based cardiology report generation
- SQLite-based patient history
- Previous visit retrieval
- Deterministic safety validation layer
- Clinician review safeguards
- Flask web interface
- Demonstration patient cases
- Automated testing using pytest

------
## System Workflow

The enhanced system follows the following workflow:

1. Patient information is entered through the web interface.
2. The information is validated and represented as a structured patient case.
3. FLAN-T5 extracts relevant clinical information.
4. The ECG analysis tool provides additional ECG-related information when available.
5. Previous patient history is retrieved from the SQLite database where applicable.
6. The RAG component retrieves relevant evidence from the local clinical knowledge repository.
7. DeepSeek-R1 performs a separate clinical reasoning stage using the available patient information and retrieved evidence.
8. Gemini integrates the available information and generates the output.
9. The safety layer checks the generated report against safety constraints.
10. The safety-checked final cardiology decision-support report is presented to the user and can be stored in patient history.

------

# Tech Stack
- Python
- Flask
- Google Gemini
- FLAN-T5
- DeepSeek-R1
- Hugging Face Transformers
- Retrieval-Augmented Generation (RAG)
- JSON
- SQLite
- python-dotenv
- pytest

---
## Knowledge Repository

The local RAG knowledge repository contains selected clinical information based on:

- NICE clinical guidelines
- European Society of Cardiology (ESC) guidelines
- Selected peer-reviewed research

The repository is used to retrieve relevant evidence for a patient case before the reasoning and report-generation stages.

The current retrieval approach uses local structured information and keyword-based matching. It does not currently use a vector database or semantic embedding-based retrieval.

## Patient History

Patient information and previous visits are stored using SQLite.

The system can retrieve previous patient visits and provide relevant historical information during a new assessment. This allows the system to consider previous information rather than treating each assessment as completely independent.

## ECG Analysis

The system includes an ECG analysis tool that processes the supplied ECG description and provides additional ECG-related information for the decision-support workflow.

The system does not directly analyse raw ECG waveform signals. ECG-related information is based on the description supplied to the application.

## Safety

The system includes a deterministic safety layer that is applied after Gemini generates the cardiology decision-support report.

The safety layer checks the generated output against predefined safety constraints. These include avoiding confirmed autonomous diagnoses and definitive treatment prescriptions.

The generated information is presented as decision-support information and requires review by a qualified healthcare professional.

## Evaluation

The enhanced system was evaluated using five representative cardiovascular cases.

Evaluation was performed at system, component and case levels.

### Baseline and Enhanced System

The original Gemini-based system was compared with the enhanced architecture incorporating FLAN-T5, RAG and DeepSeek-R1.

The enhanced system achieved higher compliance across all four cases for which both baseline and enhanced results were available.

### FLAN-T5 Evaluation

FLAN-T5 was evaluated using precision, recall and F1-score based on the clinical information extracted from each case.

The results showed high precision but lower recall. This indicates that the information extracted by FLAN-T5 was generally correct, although some relevant patient information was not extracted.

### RAG Evaluation

The RAG component was evaluated based on the relevance of retrieved clinical evidence to each patient case.

The retrieved evidence was generally relevant to the corresponding cardiovascular presentations. However, retrieval alone does not guarantee that all retrieved evidence will be reflected in the final report.

### DeepSeek-R1 Evaluation

DeepSeek-R1 was evaluated using structured clinical reasoning and safety-related criteria.

The component demonstrated strong performance in clinical reasoning, differential considerations, evidence use and information-gap awareness. Some cases nevertheless produced language suggesting a confirmed diagnosis, showing that safety monitoring remains necessary.

### Text Generation Evaluation

The generated Gemini reports were evaluated using ROUGE-L and BERTScore against clinician-level reference reports.

These metrics provide information about lexical and semantic similarity but cannot independently establish clinical correctness or safety.
---------

## Project Structure

The project follows a modular structure organised into separate components for application logic, AI services, clinical tools, Retrieval-Augmented Generation, data management, web interface, and testing.

- `app/` – Core application package containing the main system modules.
- `app/services/` – AI reasoning, Gemini client, assistant, history, and supporting services.
- `app/tools/` – Clinical analysis and supporting tools, including ECG analysis and literature search functionality.
- `app/rag/` – Retrieval-Augmented Generation components and the local clinical knowledge repository.
- `app/models/` – Data models used to represent patient and clinical information.
- `app/db/` – Database configuration, patient repository, and database operations.
- `app/prompts/` – Prompt templates used to guide clinical reasoning and report generation.
- `templates/` – HTML templates for the Flask web interface.
- `static/` – CSS, JavaScript, and other static web assets.
- `tests/` – Automated unit and integration tests using `pytest`.
- `Results/` – Evaluation results, generated outputs, and supporting project results.
- `web_app.py` – Main Flask application entry point.
- `cardiology_agent.py` – Core cardiology agent and multi-agent system functionality.
- `requirements.txt` – Python dependencies required to run the project.
- `apikey.env` – Local environment configuration containing API credentials; this file should not be committed to the repository.

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
The API key must remain local and should not be committed to the Git repository.

---

## 5. Run the application

```bash
python web_app.py
```

---

# Running Tests

The project uses pytest for automated testing. Run the automated test suite using:

```bash
pytest
```

---


# Safety and Ethical Considerations

This project is an academic research prototype and is not a clinically validated medical system.

The system is not:

-A medical device
-An autonomous diagnostic system
-A treatment recommendation system
-A replacement for professional clinical judgement

The generated outputs are intended to provide decision-support information only.

The safety layer applies predefined safety constraints to the generated report, including restrictions against confirmed autonomous diagnoses and definitive treatment prescriptions.

Clinician review remains an essential part of the workflow. Generated outputs should be reviewed and interpreted by an appropriately qualified healthcare professional before any clinical consideration.

---

# Limitations

The current prototype has several limitations:

- FLAN-T5 has limited information extraction recall.
- The RAG repository contains selected summaries rather than complete clinical guideline documents.
- Evidence retrieval does not guarantee that all retrieved information will appear in the final report.
- AI-generated reasoning may occasionally contain excessive diagnostic certainty.
- ECG interpretation is based on supplied ECG descriptions rather than raw ECG waveform data.
- The evaluation uses a limited number of representative cardiovascular cases.
- Automated language metrics cannot independently determine clinical correctness.
- External AI services may introduce API availability and configuration limitations.

---

# Future Improvements

- Future development could include:
- Improving FLAN-T5 information extraction recall
- Improving information transfer between agents
- Strengthening safety controls for diagnostic certainty
- Expanding the clinical knowledge repository
- Implementing semantic or vector-based retrieval
- Integrating raw ECG waveform analysis
- Supporting multimodal ECG image analysis
- Increasing the number and diversity of evaluation cases
- Conducting evaluation with cardiology or clinical experts
- Exploring cloud-based deployment

---

# Academic Context

This project was developed as part of the MSc Data Science and Computational Intelligence Individual Research Project at Coventry University.

The research investigates the use of Multi-Agent Artificial Intelligence, Large Language Models, Retrieval-Augmented Generation, clinical information extraction and specialised reasoning for ECG-related cardiology clinical decision support.

The project focuses on whether separating information extraction, evidence retrieval, clinical reasoning and report generation can improve the transparency, evidence grounding and structured reasoning of an existing cardiology AI prototype while maintaining appropriate safety boundaries and clinician oversight.

---

# Author

**Preethi Vyduryam**

MSc Computing Dissertation Project
