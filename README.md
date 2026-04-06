# Mahadhan Kisan Saathi — AI Voice Agent for Farmer Onboarding Recovery

An AI-powered multilingual conversational voice agent that calls farmers who dropped off during app registration, identifies where they got stuck, and guides them to completion — in Hindi or Marathi, using natural voice conversation.

---

## What It Does

Farmers who download the Mahadhan app often start but don't finish registration. This agent makes an outbound call, detects the exact drop-off stage (OTP, profile, photo, crop details), and walks the farmer through completing it — warmly, patiently, in their own language.

The agent sounds like a helpful family member, not a customer service bot. It uses short turns, empathetic phrases, and waits for the farmer to respond before continuing.

---

## Architecture

```
Farmer (mic/speaker)
        │  raw PCM audio (24kHz)
        ▼
   Runtime (orchestrator)
   ├── VoiceLiveClient  ──── WebSocket ──▶  Azure Voice Live API
   │                                        (STT + LLM + TTS + VAD)
   ├── FarmerAgent       (system prompt / persona)
   └── ToolRegistry
        └── onboarding_tools.py  (6 callable tools)
```

**Azure Voice Live** replaces the traditional STT → LLM → TTS pipeline with a single WebSocket connection. Raw farmer audio goes in; agent voice audio comes back out. Speech recognition, LLM reasoning, voice synthesis, and voice activity detection all happen inside that one connection.

---

## Key Features

- **Multilingual** — Hindi and Marathi, Roman script only
- **Single WebSocket** — Azure Voice Live collapses STT + LLM + TTS + VAD into one connection
- **Server-side VAD** — Azure detects when the farmer finishes speaking; no manual commit logic needed
- **Streaming tool calls** — LLM function call arguments arrive as deltas and are assembled before execution
- **Echo prevention** — mic is paused during playback; Azure-side buffer is cleared after each response
- **Graceful shutdown** — `end_conversation` tool sets a flag; agent finishes speaking its farewell before disconnecting
- **Warm persona** — conversational turn-taking rules baked into the system prompt to prevent robotic responses

---


## The 6 Onboarding Tools

| Tool | Triggered when |
|---|---|
| `diagnose_dropoff` | Farmer mentions where they stopped in registration |
| `get_otp_help` | OTP not received, expired, or wrong number |
| `get_profile_help` | Profile section confusion — name, photo, address |
| `get_crop_entry_help` | Crop details confusion — area, date, which crop |
| `send_help_via_whatsapp` | Farmer wants step-by-step guide sent to them |
| `end_conversation` | Farmer says goodbye or task is complete |

Tools are registered with a `@registry.register(name, description, parameters)` decorator. The JSON schema for each tool is sent to Azure Voice Live during session setup, enabling the LLM to call them mid-conversation.

---

## Setup

### Prerequisites

- Python 3.10+
- A Microsoft Azure AI Foundry resource with Voice Live enabled
- A supported model deployed (e.g. `gpt-4o-realtime`)
- A microphone connected to the machine running the agent

### Install dependencies

```bash
pip install websockets sounddevice numpy python-dotenv
```

### Configure environment

Create a `.env` file in the project root:

```env
VOICE_LIVE_ENDPOINT=https://<your-resource-name>.services.ai.azure.com
VOICE_LIVE_KEY=<your-api-key>
VOICE_LIVE_MODEL=gpt-4o-realtime
```

### Run

```bash
python main.py
```

The agent will connect to Azure, configure the session, and immediately call out the opening greeting. Speak into your microphone to simulate a farmer responding.

---

## How the Conversation Works

1. Agent greets and asks language preference (Hindi / Marathi)
2. Farmer responds — Azure VAD detects end of speech automatically
3. LLM identifies drop-off stage from what the farmer says
4. LLM calls the appropriate tool (e.g. `get_otp_help`)
5. Tool result is sent back to Azure; LLM continues speaking with the guidance
6. Agent encourages farmer to try the app, offers WhatsApp guide if needed
7. When farmer says goodbye, `end_conversation` fires, agent delivers warm farewell, then disconnects

---


## Extending the Project

**Add a new tool** — decorate a function in `onboarding_tools.py` with `@registry.register(...)`. It will automatically be included in the next session's tool schema.

**Change the persona** — edit `farmer_agent.py`. The entire personality, language rules, turn-taking behavior, and drop-off detection keywords live in the `get_instructions()` string.

**Enable server-side echo cancellation** — add `"input_audio_echo_cancellation": {"type": "server_echo_cancellation"}` to the `session.update` payload in `runtime.py` to replace the client-side echo prevention logic.

**Switch to Semantic VAD** — replace `"type": "server_vad"` with `"type": "azure_semantic_vad"` in the session config for more robust turn detection in noisy environments.

---

## License

MIT
