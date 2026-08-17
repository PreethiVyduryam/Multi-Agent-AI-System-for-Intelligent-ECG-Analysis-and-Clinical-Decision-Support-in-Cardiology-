import json
import sys
from pathlib import Path

from rouge_score import rouge_scorer
from bert_score import score as bert_score


# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

REFERENCE_DIR = (
    BASE_DIR
    / "evaluation"
    / "references"
    / "text"
)

RESULTS_DIR = (
    BASE_DIR
    / "evaluation"
    / "results"
)

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# CASES
# =========================================================

CASE_IDS = [
    "case_001",
    "case_002",
    "case_003",
    "case_004",
    "case_005",
]


# =========================================================
# FILE LOADING
# =========================================================

def load_text(path):

    if not path.exists():
        raise FileNotFoundError(
            f"File not found:\n{path}"
        )

    return path.read_text(
        encoding="utf-8"
    ).strip()


# =========================================================
# ROUGE-L
# =========================================================

def calculate_rouge_l(reference, candidate):

    scorer = rouge_scorer.RougeScorer(
        ["rougeL"],
        use_stemmer=True,
    )

    result = scorer.score(
        reference,
        candidate,
    )

    rouge_l = result["rougeL"]

    return {
        "precision": rouge_l.precision,
        "recall": rouge_l.recall,
        "f1": rouge_l.fmeasure,
    }


# =========================================================
# BERTSCORE
# =========================================================

def calculate_bertscore(
    references,
    candidates,
):

    precision, recall, f1 = bert_score(
        candidates,
        references,
        lang="en",
        verbose=True,
    )

    return {
        "precision": precision.tolist(),
        "recall": recall.tolist(),
        "f1": f1.tolist(),
    }


# =========================================================
# MAIN
# =========================================================

def main():

    references = []
    candidates = []

    print(
        "\n=============================================="
    )
    print(
        "TEXT GENERATION EVALUATION"
    )
    print(
        "ROUGE-L + BERTScore"
    )
    print(
        "==============================================\n"
    )

    # -----------------------------------------------------
    # Load all cases
    # -----------------------------------------------------

    for case_id in CASE_IDS:

        reference_file = (
            REFERENCE_DIR
            / f"{case_id}_reference.txt"
        )

        candidate_file = (
            RESULTS_DIR
            / f"{case_id}_gemini_output.txt"
        )

        reference = load_text(
            reference_file
        )

        candidate = load_text(
            candidate_file
        )

        references.append(reference)
        candidates.append(candidate)

        print(
            f"Loaded {case_id}"
        )

    # -----------------------------------------------------
    # ROUGE-L
    # -----------------------------------------------------

    print(
        "\n=============================================="
    )
    print(
        "ROUGE-L RESULTS"
    )
    print(
        "==============================================\n"
    )

    rouge_results = {}

    for case_id, reference, candidate in zip(
        CASE_IDS,
        references,
        candidates,
    ):

        result = calculate_rouge_l(
            reference,
            candidate,
        )

        rouge_results[case_id] = result

        print(
            f"{case_id}: "
            f"Precision={result['precision']:.4f}, "
            f"Recall={result['recall']:.4f}, "
            f"F1={result['f1']:.4f}"
        )

    rouge_mean = sum(
        result["f1"]
        for result in rouge_results.values()
    ) / len(rouge_results)

    print(
        f"\nMean ROUGE-L F1: {rouge_mean:.4f}"
    )

    # -----------------------------------------------------
    # BERTScore
    # -----------------------------------------------------

    print(
        "\n=============================================="
    )
    print(
        "BERTSCORE RESULTS"
    )
    print(
        "==============================================\n"
    )

    bert_results = calculate_bertscore(
        references,
        candidates,
    )

    bert_case_results = {}

    for index, case_id in enumerate(
        CASE_IDS
    ):

        bert_case_results[case_id] = {
            "precision": bert_results[
                "precision"
            ][index],
            "recall": bert_results[
                "recall"
            ][index],
            "f1": bert_results[
                "f1"
            ][index],
        }

        result = bert_case_results[
            case_id
        ]

        print(
            f"{case_id}: "
            f"Precision={result['precision']:.4f}, "
            f"Recall={result['recall']:.4f}, "
            f"F1={result['f1']:.4f}"
        )

    bert_mean = sum(
        result["f1"]
        for result in bert_case_results.values()
    ) / len(bert_case_results)

    print(
        f"\nMean BERTScore F1: {bert_mean:.4f}"
    )

    # -----------------------------------------------------
    # Save results
    # -----------------------------------------------------

    output = {
        "evaluation_type": (
            "Enhanced Gemini text generation "
            "evaluation"
        ),
        "cases": {},
        "mean": {
            "rouge_l_f1": rouge_mean,
            "bertscore_f1": bert_mean,
        },
    }

    for case_id in CASE_IDS:

        output["cases"][case_id] = {
            "rouge_l": rouge_results[
                case_id
            ],
            "bertscore": bert_case_results[
                case_id
            ],
        }

    result_file = (
        RESULTS_DIR
        / "text_generation_metrics.json"
    )

    with result_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
        )

    print(
        "\n=============================================="
    )
    print(
        "RESULTS SAVED"
    )
    print(
        "=============================================="
    )

    print(result_file)


if __name__ == "__main__":
    main()
