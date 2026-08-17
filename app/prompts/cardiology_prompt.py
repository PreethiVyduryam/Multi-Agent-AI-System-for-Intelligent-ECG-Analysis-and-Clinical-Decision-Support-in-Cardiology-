import json
from dataclasses import asdict
from typing import Optional

from app.models.patient import PatientCase
def build_cardiology_user_prompt(
    patient_case: PatientCase,
    history_summary: Optional[str],
    clinical_summary: Optional[str] = None,
) -> str:
    structured_case = json.dumps(asdict(patient_case), indent=2)
    history_block = history_summary or "No prior visit history is available for this patient."

    return f"""
Review this structured patient case and provide a cautious cardiology decision-support response.

Prior patient history:
{history_block}

Current patient case:
{structured_case}

Clinical Information Extraction Summary:
{clinical_summary or "Not available."}

Available tools:
1. analyze_ecg_tool(ecg_data: str)
   - Use when ECG data or ECG description is present and rhythm interpretation would help.

2. search_literature_tool(query: str)
   - Use when guideline support, review evidence, or medical literature grounding would help.
   - Use focused medical search queries, not long conversational sentences.

Tool use instructions:
- Decide for yourself whether either tool is needed.
- You may use neither, one, or both tools.
- Do not call analyze_ecg_tool if there is no ECG information.
- Prefer literature search when evidence or guideline support would materially improve the answer.
- After using tools, incorporate the results into the final answer.

Return your answer in exactly this format:

1. Possible cardiac considerations
- consideration 1 (Confidence: low/medium/high)
- consideration 2 (Confidence: low/medium/high)
- consideration 3 (Confidence: low/medium/high)

2. Recommended next tests or monitoring
- recommendation 1
- recommendation 2
- recommendation 3

3. Immediate safety note
A short paragraph that explicitly recommends clinician evaluation and mentions urgent review if symptoms are concerning.

4. Plain-language summary
A short paragraph.

5. Evidence Summary

Begin this section with:

Clinical reasoning was supported using evidence retrieved from the local clinical knowledge repository.

Then include:

Evidence Sources
- List the relevant guideline(s) or research evidence us ed (e.g., NICE, ESC, or peer-reviewed research) as bullet points where supported by the retrieved evidence.

Summary
- Explain how the retrieved evidence supports the clinical reasoning and recommendations.
- Keep the explanation concise and evidence-based.

6. Safety disclaimer
One short paragraph stating clearly that this is not medical advice and not a confirmed diagnosis.

Rules:
- Never present the output as a final or confirmed diagnosis.
- Use cautious language such as "possible", "suggests", "could indicate", or "should be considered".
- Use prior patient history when relevant.
- If literature search is used, mention it explicitly in the Evidence summary section.
- Keep the Evidence summary grounded in retrieved tool output, not general memory.
- Do not prescribe medication.
- Be clinically cautious.
- Mention when symptoms could be non-cardiac if appropriate.
- Clearly state that this is decision support, not medical diagnosis.
""".strip()


def build_cardiology_system_prompt() -> str:
    return (
        "You are a careful cardiology decision-support assistant. "
        "You help summarize possible cardiac considerations, but you do not diagnose. "
        "You must be concise, structured, safety-conscious, and non-definitive. "
        "When tools are available, decide whether tool use is necessary and use them only when helpful. "
        "When prior patient history is provided, use it as contextual history, not as confirmed diagnosis. "
        "Always include confidence labels for possible considerations and always recommend clinician review."
    )
