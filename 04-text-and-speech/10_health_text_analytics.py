# Run: uv run python 04-text-and-speech/10_health_text_analytics.py
"""Text Analytics for Health — extract clinical entities from unstructured text.

begin_analyze_healthcare_entities() extracts structured clinical concepts from free
text: MedicationName, Dosage, RouteOfAdministration, Diagnosis, SymptomOrSign,
ExaminationName, and more. Many entities include a normalized_text field that maps
to UMLS concepts — critical for downstream analytics. This is an extraction aid,
NOT a diagnostic tool, clinical decision support, or compliance control. Health
data requires approved privacy, access, and human-review processes.

Code path:
  language_client() → begin_analyze_healthcare_entities(_CLINICAL, language="en") →
  poller.result() (async internally) → for each entity: print category, text,
  confidence, and normalized_text if present.

What to watch: [SymptomOrSign] 'dry cough', [Diagnosis] 'hypertension',
[MedicationName] 'lisinopril' with [Dosage] '10mg'. The normalized_text field
links medication names to UMLS codes when available.

Prerequisites / env vars:
  LANGUAGE_ENDPOINT — Azure AI Language endpoint (cognitiveservices.azure.com)
"""
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
