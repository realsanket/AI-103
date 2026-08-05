"""Stream reviewed PCM WAV audio through Voice Live and save response PCM.

No flags makes no Azure call. `--run` needs a supported mono 16-bit PCM WAV,
an output `.pcm` path, and a Voice Live model. It uses Microsoft Entra with
the `https://ai.azure.com/.default` scope; assign Cognitive Services User and
Foundry User at the narrowest scope. The 2026-04-10 API supports 16 kHz or
24 kHz input and streams `response.audio.delta` as base64 PCM.

This is file-to-file flow, not microphone capture or speaker playback. Do not
stream unconsented audio. Protect transcripts and output audio with retention,
access, and review controls. API reference:
https://learn.microsoft.com/azure/ai-services/speech-service/voice-live-how-to
"""
import argparse
import asyncio
import base64
import json
from pathlib import Path
from urllib.parse import urlencode, urlsplit, urlunsplit
import wave

from azure.identity import DefaultAzureCredential
import websockets

from _shared.config import settings

_API_VERSION = "2026-04-10"
_SCOPE = "https://ai.azure.com/.default"
_CHUNK_BYTES = 256 * 1024


def pcm_wav(path: Path) -> tuple[bytes, int]:
    if not path.is_file():
        raise SystemExit(f"Audio file does not exist: {path}")
    with wave.open(str(path), "rb") as audio:
        rate = audio.getframerate()
        if audio.getnchannels() != 1 or audio.getsampwidth() != 2 or rate not in {16000, 24000}:
            raise SystemExit("Audio must be mono, 16-bit PCM WAV at 16000 or 24000 Hz.")
        return audio.readframes(audio.getnframes()), rate


def voice_live_url(endpoint: str, model: str) -> str:
    parsed = urlsplit(endpoint)
    if parsed.scheme != "wss" or not parsed.hostname:
        raise SystemExit("VOICE_LIVE_ENDPOINT must be a wss:// Voice Live endpoint.")
    if not model:
        raise SystemExit("--model is required with --run.")
    return urlunsplit((
        "wss", parsed.netloc, parsed.path.rstrip("/"),
        urlencode({"api-version": _API_VERSION, "model": model}), "",
    ))


def session_update(rate: int) -> dict:
    return {
        "type": "session.update",
        "session": {
            "modalities": ["text", "audio"],
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_sampling_rate": rate,
            "voice": {"type": "azure-standard", "name": "en-US-Ava:DragonHDLatestNeural"},
        },
    }


async def run(endpoint: str, model: str, audio_path: Path, output_path: Path) -> None:
    audio, rate = pcm_wav(audio_path)
    if output_path.suffix.lower() != ".pcm":
        raise SystemExit("--output must end in .pcm (raw 16-bit PCM response audio).")
    if output_path.exists():
        raise SystemExit(f"Refusing to overwrite {output_path}; choose a new path.")
    if not output_path.parent.is_dir():
        raise SystemExit(f"Output directory does not exist: {output_path.parent}")

    token = DefaultAzureCredential().get_token(_SCOPE).token
    received: list[bytes] = []
    async with websockets.connect(
        voice_live_url(endpoint, model),
        additional_headers={"Authorization": "Bearer " + token},
    ) as socket:
        await socket.send(json.dumps(session_update(rate)))
        for start in range(0, len(audio), _CHUNK_BYTES):
            await socket.send(json.dumps({
                "type": "input_audio_buffer.append",
                "audio": base64.b64encode(audio[start:start + _CHUNK_BYTES]).decode("ascii"),
            }))
        await socket.send(json.dumps({"type": "input_audio_buffer.commit"}))
        await socket.send(json.dumps({"type": "response.create"}))
        async for message in socket:
            event = json.loads(message)
            if event.get("type") == "response.audio.delta":
                received.append(base64.b64decode(event["delta"], validate=True))
            elif event.get("type") == "error":
                raise RuntimeError(f"Voice Live error: {event.get('error', event)}")
            elif event.get("type") == "response.done":
                break
    if not received:
        raise RuntimeError("Voice Live completed without response audio.")
    output_path.write_bytes(b"".join(received))
    print(f"Saved {output_path.stat().st_size} PCM bytes to {output_path}.")


def preflight(audio_path: Path | None = None) -> None:
    print("Voice Live audio-flow preflight. No cloud calls made.")
    print(f"- voice_live_endpoint: {'configured' if settings().voice_live_endpoint else 'missing'}")
    print("- required run inputs: --model, mono PCM WAV (16/24 kHz), and new --output PATH.pcm")
    if audio_path:
        _, rate = pcm_wav(audio_path)
        print(f"- audio contract: valid ({rate} Hz)")
    print("Use --run only after consent, model/region availability, role, cost, and retention review.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight or run a Voice Live PCM file-to-file flow.")
    parser.add_argument("--run", action="store_true", help="Connect to Voice Live and save response PCM.")
    parser.add_argument("--audio", type=Path, help="Mono 16-bit PCM WAV at 16 kHz or 24 kHz.")
    parser.add_argument("--output", type=Path, help="New .pcm response-audio path.")
    parser.add_argument("--model", help="Voice Live model query parameter.")
    args = parser.parse_args(argv)
    if not args.run:
        preflight(args.audio)
        return
    if not args.audio or not args.output:
        parser.error("--audio and --output are required with --run.")
    asyncio.run(run(settings().voice_live_endpoint, args.model or "", args.audio, args.output))


if __name__ == "__main__":
    main()
