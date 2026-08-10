import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from app.prompts.flant5_prompt import build_flant5_prompt


class FlanT5Client:
    """
    Clinical Information Extraction Agent using Flan-T5.

    This agent converts patient information into a structured
    clinical summary before ECG interpretation.
    """

    def __init__(self, model_name: str = "google/flan-t5-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        self.model.eval()

    def extract_clinical_information(
        self,
        patient_information: str,
    ) -> str:
        """
        Extract structured clinical information from
        unstructured patient information.
        """

        prompt = build_flant5_prompt(patient_information)

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
        )

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=200,
            )

        return self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True,
        )