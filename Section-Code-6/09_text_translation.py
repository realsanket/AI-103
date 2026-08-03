import requests

ENDPOINT = "https://foundry-dev-eus-01.services.ai.azure.com/"
API_VERSION = "2025-10-01-preview"
SUBSCRIPTION_KEY = ""


def translate_text(text, targets, source_language):
    headers = {
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
        "Content-Type": "application/json"
    }
    url = f"{ENDPOINT}translator/text/translate?api-version={API_VERSION}"
    body = {
        "inputs": [
            {
                "Text": text,
                "language": source_language,
                "targets": targets
            }
        ]
    }

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    return response.json()


def main():
    text = (
        "Our VPN keeps dropping every 10 minutes since the last update. "
        "This is affecting our whole sales team."
    )
    targets = [
        {"language": "fr"},
        {"language": "ja"},
        {"language": "es"},
    ]
    source_language = "en"

    try:
        result = translate_text(text, targets, source_language)

        for t in result["value"][0]["translations"]:
            print(f"[{t['language']}] {t['text']}")

    except Exception as e:
        print(f"Translation failed: {e}")


if __name__ == "__main__":
    main()