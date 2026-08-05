"""Use Translator Text with keyless Microsoft Entra authentication.

No flags performs a local preflight. `--run` sends the supplied text to the
Translator Text global endpoint through the existing keyless client, which
uses `DefaultAzureCredential` and does not read a Translator key. Grant the
calling identity only the documented Translator/Cognitive Services data role.

Do not send secrets or unreviewed sensitive text. Redact before telemetry,
choose a regional endpoint only when its data-residency rules fit, and add
human review for high-impact translations. Microsoft documentation:
https://learn.microsoft.com/azure/ai-services/translator/how-to/microsoft-entra-id-auth
"""
import argparse
import re

from _shared.translator_client import translate

_LANGUAGE = re.compile(r"^[a-z]{2,3}(?:-[a-z]{2,4})?$")


def _language_tags(value: str, option: str) -> list[str]:
    targets = [item.strip().lower() for item in value.split(",") if item.strip()]
    if not targets or any(not _LANGUAGE.fullmatch(target) for target in targets):
        raise SystemExit(f"{option} needs comma-separated language tags, for example fr,ja.")
    return targets


def target_languages(value: str) -> list[str]:
    return _language_tags(value, "--targets")


def source_language(value: str) -> str:
    sources = _language_tags(value, "--source")
    if len(sources) != 1:
        raise SystemExit("--source needs one language tag.")
    return sources[0]


def preflight() -> None:
    print("Translator secure-configuration preflight. No cloud calls made.")
    print("Auth with --run: DefaultAzureCredential obtains an Entra token; no Translator key is configured.")
    print("Grant least-privilege Translator/Cognitive Services access and use managed identity in Azure.")
    print("Redact sensitive text before logs; verify residency, private networking, retention, and review gates.")
    print("Use --run only for reviewed text.")


def run(text: str, targets: list[str], source: str) -> None:
    for result in translate(text, targets=targets, source_language=source):
        for translation in result["translations"]:
            print(f"[{translation['to']}] {translation['text']}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight or translate reviewed text with Entra auth.")
    parser.add_argument("--run", action="store_true", help="Send reviewed text to Translator Text.")
    parser.add_argument("--text", default="Northwind support is available Monday through Friday.")
    parser.add_argument("--source", default="en")
    parser.add_argument("--targets", default="fr,ja")
    args = parser.parse_args(argv)
    if not args.run:
        preflight()
        return
    run(args.text, target_languages(args.targets), source_language(args.source))


if __name__ == "__main__":
    main()
