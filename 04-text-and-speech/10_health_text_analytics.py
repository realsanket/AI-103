"""Text Analytics for Health — extract clinical entities from unstructured text."""
from _shared.language_client import language_client

_CLINICAL = [
    "Patient presents with a persistent dry cough and shortness of breath for 5 days. "
    "PMH: hypertension controlled on lisinopril 10mg daily. "
    "Prescribed amoxicillin 500mg TID for 7 days.",
]


def main() -> None:
    client = language_client()
    poller = client.begin_analyze_healthcare_entities(_CLINICAL, language="en")
    result = poller.result()
    for idx, doc in enumerate(result):
        if doc.is_error:
            print(f"--- Document {idx + 1} failed: {doc.error.code} ---")
            continue
        print("--- Clinical entities ---")
        for e in doc.entities:
            print(f"  [{e.category}] '{e.text}'  conf={e.confidence_score:.2f}  norm={getattr(e, 'normalized_text', None)}")


if __name__ == "__main__":
    main()
