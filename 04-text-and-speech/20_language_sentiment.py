"""Azure AI Language sentiment analysis with opinion mining."""
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
