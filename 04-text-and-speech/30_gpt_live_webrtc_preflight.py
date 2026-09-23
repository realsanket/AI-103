# Run: uv run python 04-text-and-speech/30_gpt_live_webrtc_preflight.py
# Practice-question coverage: Q128.
"""Preflight the GPT-Live WebRTC transport — SDP handshake shape, without any call.

The WebRTC transport is browser- or native-client native: audio flows on a negotiated
RTP media track, session events flow on a WebRTC data channel. Python has no first-class
place in that path. There's also no ephemeral client key, so the browser cannot open a
session directly — a trusted backend must sit in the SDP exchange to hold the API key or
Entra credentials.

This lesson is preflight only, on purpose. It documents the handshake, prints the URL a
backend POSTs to during session creation, and shows the exact JSON body shape the doc
specifies (session config + `transport: { type: "webrtc", sdp: offerSdp }`). It never
opens a socket, exchanges SDP, or spends a token. Use it as the release-review check for
"do we have a backend endpoint that proxies the SDP, and does it live behind our own
auth?" before wiring a browser client.

Code path:
  preflight(): read env → print WebRTC handshake steps, backend URL, and JSON schema
  for the session-creation request. No I/O, no network, no --apply.

What to watch. `AZURE_OPENAI_API_KEY` or Entra credentials must exist on the backend
(never the browser). Session id in the response is what a sideband WebSocket attaches to
via `wss://<resource>.openai.azure.com/openai/v1/live/sessions/{session_id}/attach` if the
server wants to observe or steer the session while media stays on the RTP track. Missing
transceiver direction, wrong Content-Type, or forgetting the data channel are the usual
first-day failures — surface them here before they cost time in the browser console.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT  — Foundry / Azure OpenAI resource endpoint (https://...)
  AZURE_OPENAI_API_KEY   — API key held on the backend (omit to use DefaultAzureCredential)
  GPT_LIVE_MODEL         — GPT-Live deployment name (default: gpt-live-1)
"""
import argparse
import json
import os


def _sessions_url(endpoint: str) -> str:
    # WebRTC session creation is HTTPS POST from the backend, not WSS.
    return f"{endpoint.rstrip('/')}/openai/v1/live/sessions"


def _creation_body_shape(model: str) -> dict:
    # Mirrors the WebRTC how-to doc verbatim. `sdp` is the browser's offer, forwarded by
    # the backend; the response contains { session: { id, ... }, transport: { sdp: <answer> } }.
    return {
        "session": {
            "model": model,
            "instructions": "Be concise.",
            "delegation": {"type": "client"},
        },
        "transport": {"type": "webrtc", "sdp": "<browser offer SDP goes here>"},
    }


def preflight() -> None:
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    model = os.environ.get("GPT_LIVE_MODEL", "gpt-live-1")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")

    print("GPT-Live WebRTC preflight (no cloud calls; preflight-only lesson).")
    print(f"- AZURE_OPENAI_ENDPOINT: {'configured' if endpoint else 'MISSING'}")
    print(f"- GPT_LIVE_MODEL: {model}")
    print(f"- AZURE_OPENAI_API_KEY (backend-held): "
          f"{'configured' if api_key else 'not set (DefaultAzureCredential fallback)'}")
    if endpoint:
        print(f"- Backend SDP-exchange URL: POST {_sessions_url(endpoint)}")
    print()
    print("Handshake steps (browser <-> backend <-> service):")
    print("  1. Browser: new RTCPeerConnection; addTransceiver('audio', sendrecv);")
    print("     createDataChannel('oai-events'); createOffer(); setLocalDescription(offer).")
    print("  2. Browser POSTs offer.sdp to your backend.")
    print("  3. Backend POSTs to /openai/v1/live/sessions with session config + transport.sdp,")
    print("     authenticated with API key or Entra credentials.")
    print("  4. Backend returns transport.sdp (the answer) to the browser; saves session.id")
    print("     if it plans to attach a sideband WebSocket.")
    print("  5. Browser: pc.setRemoteDescription({type: 'answer', sdp: answer}).")
    print("     Audio flows on the RTP media track; events flow on the data channel.")
    print()
    print("Backend session-creation JSON body shape:")
    print(json.dumps(_creation_body_shape(model), indent=2))
    print()
    print("Why this lesson is preflight-only:")
    print("- WebRTC needs a browser peer connection; Python is not the primary transport.")
    print("- No ephemeral client keys exist for GPT-Live; the browser never authenticates directly.")
    print("- Server-to-server integrations should use the WebSocket transport (lesson 28) instead.")
    print("- All non-audio session events (session.update, context appends, delegation, transcripts,")
    print("  usage, errors) use the same schema as WebSocket - see the GPT-Live event reference.")


def main(argv: list[str] | None = None) -> None:
    # No --apply on purpose. Kept argparse for consistency with sibling lessons.
    parser = argparse.ArgumentParser(description="Preflight the GPT-Live WebRTC handshake (no cloud calls).")
    parser.parse_args(argv)
    preflight()


if __name__ == "__main__":
    main()
