import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


MODEL_NAME = "google/flan-t5-base"


def main():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

    model.eval()

    prompt = """
Extract the following information.

Text:
John is 35 years old and lives in London.

Return exactly:

AGE:
LOCATION:
""".strip()

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512,
    )

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=50,
        )

    result = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
    )

    print("\n========== FLAN-T5 CONTROL TEST ==========\n")
    print(result)


if __name__ == "__main__":
    main()
