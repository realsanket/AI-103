# Run: uv run python 04-text-and-speech/20_language_sentiment.py
# Practice-question coverage: Q158.
"""Azure AI Language — structured sentiment with opinion mining.

analyze_sentiment() with show_opinion_mining=True returns: (1) document-level
sentiment (positive/negative/neutral/mixed), (2) per-sentence sentiment, and
(3) opinion mining — target+assessment pairs that associate descriptors with their
target (e.g., "frustrating" → "onboarding process"). This is the structured
alternative to the LLM approach in 02_llm_sentiment.py. Retirement: March 31 2029;
prefer Foundry models for new production workloads.

Code path:
  language_client() → analyze_sentiment(_DOCS, language="en", show_opinion_mining=True)
  → for each doc: print document sentiment, per-sentence sentiment, then mined_opinions
  with target.text, target.sentiment, and assessment text+sentiment.

What to watch: document-level "mixed", sentence for "reliable" → positive,
"frustrating" → negative. Opinion mining output:
  onboarding process (negative): frustrating (negative).

Prerequisites / env vars:
  LANGUAGE_ENDPOINT — Azure AI Language endpoint (cognitiveservices.azure.com)
"""
from _shared.language_client import language_client

_DOCS = [
    "Northwind Connect is reliable, but the onboarding process is frustrating. "
    "Marcus from support was helpful.",
]


def main() -> None:
    client = language_client()
    response = client.analyze_sentiment(
        _DOCS, language="en", show_opinion_mining=True
    )
    for idx, doc in enumerate(response):
        if doc.is_error:
            print(f"--- Document {idx + 1} failed: {doc.error.code} ---")
            continue
        print(f"--- Document {idx + 1}: {doc.sentiment} ---")
        for sentence in doc.sentences:
            print(f"  [{sentence.sentiment}] {sentence.text}")
            for opinion in sentence.mined_opinions:
                target = opinion.target
                assessments = ", ".join(
                    f"{assessment.text} ({assessment.sentiment})"
                    for assessment in opinion.assessments
                )
                print(f"    {target.text} ({target.sentiment}): {assessments}")


if __name__ == "__main__":
    main()
