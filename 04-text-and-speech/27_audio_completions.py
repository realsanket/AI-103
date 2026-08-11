# Run: uv run python 04-text-and-speech/27_audio_completions.py [--apply] [--input-file <wav>]
"""Send audio input to a model and receive a text response via Audio Completions.

Audio Completions extends chat completions with an audio input modality: instead
of a text prompt, you supply base64-encoded audio and the model transcribes and
responds in one round trip. This is a standard HTTP request — NOT the WebSocket
Realtime API. Use it for batch audio analysis where streaming latency is not needed.

Default preflight checks AUDIO_MODEL env var. --apply base64-encodes a WAV file
(or synthesizes a silent WAV if no file is given) and sends it as input_audio content.
The silent WAV demonstrates the API call shape; real transcription needs spoken audio.

Code path:
  --apply: openai_client().chat.completions.create(
  model=AUDIO_MODEL, modalities=["text"],
  messages=[{"role":"user","content":[{"type":"input_audio",
  "input_audio":{"data":b64,"format":"wav"}}]}])
  → choices[0].message.content.

What to watch. Response text = model's transcription or response to the audio.
Empty or error = model deployment does not support audio input modality.
Upgrade: gpt-4o-audio-preview supports input_audio; gpt-4o does not.

Prerequisites / env vars:
  PROJECT_ENDPOINT  — Foundry project HTTPS URL (used by openai_client())
  AUDIO_MODEL       — GPT-4o audio deployment (e.g. gpt-4o-audio-preview)
  --input-file      — path to WAV file (optional; synthesizes silent WAV if omitted)
  --apply           — send audio to model
"""
import argparse
import base64
import os
import struct
import wave
from io import BytesIO
from pathlib import Path

from _shared.openai_client import openai_client


def _silent_wav_b64(sample_rate: int = 16000, duration_ms: int = 500) -> str:
    num_samples = sample_rate * duration_ms // 1000
    buf = BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{num_samples}h", *([0] * num_samples)))
    return base64.b64encode(buf.getvalue()).decode()


def preflight(input_file: str | None) -> None:
    model = os.environ.get("AUDIO_MODEL", "")
    print("Audio completions preflight (no cloud calls).")
    print(f"- AUDIO_MODEL: {model or 'MISSING — set to gpt-4o-audio-preview deployment'}")
    print(f"- input file: {input_file or '(none — will synthesize 0.5s silent WAV)'}")
    print("- modality: input_audio (WAV format)")
    print("- NOT the Realtime API — standard HTTP, single round trip")
    print("Run --apply to send audio and receive text response.")


def apply(input_file: str | None) -> None:
    model = os.environ.get("AUDIO_MODEL", "")
    if not model:
        raise SystemExit("Set AUDIO_MODEL to your gpt-4o-audio-preview deployment name.")
    if input_file:
        audio_b64 = base64.b64encode(Path(input_file).read_bytes()).decode()
        print(f"Using audio file: {input_file}")
    else:
        print("No --input-file given; using synthesized 0.5s silent WAV.")
        audio_b64 = _silent_wav_b64()

    client = openai_client()
    response = client.chat.completions.create(
        model=model,
        modalities=["text"],
        messages=[{
            "role": "user",
            "content": [{
                "type": "input_audio",
                "input_audio": {"data": audio_b64, "format": "wav"},
            }],
        }],
    )
    content = response.choices[0].message.content
    print(f"Model response: {content}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Send audio input to model, receive text response.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--input-file", default=None, help="Path to WAV file.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight(args.input_file)
        return
    apply(args.input_file)


if __name__ == "__main__":
    main()
