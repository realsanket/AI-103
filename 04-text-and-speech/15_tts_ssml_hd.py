# Run: uv run python 04-text-and-speech/15_tts_ssml_hd.py [--voice hd|neural] [--print-ssml]
# Practice-question coverage: Q138.
"""SSML pronunciation and style control with Dragon HD and standard neural voices.

SSML is how you control *how* text is spoken: pauses (`<break>`), exact
pronunciation (`<phoneme>`), abbreviations (`<sub>`), content type
(`<say-as>`), speaking rate/pitch (`<prosody>`), and style
(`<mstts:express-as>`). Builds on 14_tts_neural.py, which sends plain text.

Voice families support different SSML subsets:
  --voice hd      `en-US-Ava:DragonHDLatestNeural` (Dragon HD). Supports
                  `<phoneme>`, `<break>`, `<say-as>`, `<sub>`, `<lang>`,
                  `<p>`/`<s>`, and alias-only `<lexicon>`. Does NOT support
                  `<prosody>` or `<mstts:express-as>`.
  --voice neural  `en-US-JennyNeural` (standard neural). Full SSML, including
                  `<prosody>` and `<mstts:express-as style="friendly">`.

`<phoneme alphabet="ipa" ph="...">` fixes one word's pronunciation inline. For
many terms, host a custom lexicon file and reference it with `<lexicon uri>`.

Code path:
  build_ssml(voice) → unsupported_hd_elements() guard → speak_ssml_async().get()
  → check ResultReason → keep WAV or clean it up.

What to watch: "OK — synthesized to .../northwind_ssml_<voice>.wav". Listen for
the pause after "Northwind", "gnocchi" pronounced as written in IPA, and the
order number read digit by digit. `--print-ssml` validates and prints the
document without calling Azure.

Prerequisites / env vars:
  SPEECH_ENDPOINT — Speech resource endpoint. Dragon HD voices are available in
  a subset of regions; check the HD voices region table before depending on one.
"""
import argparse
import xml.etree.ElementTree as ET

from _shared.config import SAMPLE_DATA

VOICES = {
    "hd": "en-US-Ava:DragonHDLatestNeural",
    "neural": "en-US-JennyNeural",
}

# Elements the Dragon HD voice model ignores or rejects (Microsoft HD voices doc).
_HD_UNSUPPORTED = {
    "prosody", "express-as", "emphasis", "audio", "audioduration",
    "backgroundaudio", "math", "bookmark", "silence", "viseme", "ttsembedding",
}

_PRONUNCIATION = """
      Thank you for contacting <break time="300ms"/> Northwind.
      Your order <say-as interpret-as="characters">4521</say-as>
      of <phoneme alphabet="ipa" ph="ˈnɑː.ki">gnocchi</phoneme>
      ships from our <sub alias="Seattle distribution center">SEA DC</sub> today."""


def build_ssml(voice: str) -> str:
    if voice not in VOICES:
        raise ValueError(f"voice must be one of {sorted(VOICES)}")
    body = _PRONUNCIATION
    if voice == "neural":
        body = f"""
    <mstts:express-as style="friendly">{_PRONUNCIATION}
    </mstts:express-as>
    <prosody rate="-5%">A specialist will contact you shortly.</prosody>"""
    return f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">
  <voice name="{VOICES[voice]}">{body}
  </voice>
</speak>"""


def unsupported_hd_elements(ssml: str) -> list[str]:
    """Return SSML elements in this document that Dragon HD voices do not support."""
    root = ET.fromstring(ssml)  # also proves the document is well-formed XML
    tags = {element.tag.rsplit("}", 1)[-1] for element in root.iter()}
    return sorted(tags & _HD_UNSUPPORTED)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--voice", choices=sorted(VOICES), default="hd")
    parser.add_argument("--print-ssml", action="store_true", help="Validate and print SSML; no Azure call.")
    args = parser.parse_args(argv)

    ssml = build_ssml(args.voice)
    unsupported = unsupported_hd_elements(ssml)
    if args.voice == "hd" and unsupported:
        raise SystemExit(f"Dragon HD voices do not support: {', '.join(unsupported)}")
    if args.print_ssml:
        print(ssml)
        return

    import azure.cognitiveservices.speech as speechsdk

    from _shared.speech_config import prepare_audio_output, speech_config

    output = SAMPLE_DATA / "generated" / f"northwind_ssml_{args.voice}.wav"
    prepare_audio_output(output)
    audio_out = speechsdk.audio.AudioOutputConfig(filename=str(output))
    synth = speechsdk.SpeechSynthesizer(speech_config=speech_config(), audio_config=audio_out)
    try:
        result = synth.speak_ssml_async(ssml).get()
    except Exception:
        output.unlink(missing_ok=True)
        raise
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"OK — synthesized to {output}")
    else:
        output.unlink(missing_ok=True)
        details = getattr(result, "cancellation_details", None)
        print(f"failed: {result.reason} — {getattr(details, 'error_details', '')}")


if __name__ == "__main__":
    main()
