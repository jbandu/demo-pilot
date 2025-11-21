# Demo Copilot - Autonomous Product Demo Agent

An AI-powered sales engineer that autonomously conducts product demonstrations by controlling a live browser, narrating actions with natural voice, and answering customer questions in real-time.

## Overview

Demo Copilot is a proof-of-concept for Number Labs demonstrating agentic AI capabilities. It combines:

- **Browser Automation** (Playwright) - Controls live product interfaces
- **Voice Synthesis** (ElevenLabs) - Natural, conversational narration
- **AI Q&A** (Claude Sonnet 4.5) - Intelligent question handling
- **Real-time Streaming** (WebSocket) - Live video and audio to customers

## Features

- Fully autonomous product demonstrations
- Natural voice narration with multiple voice options
- Real-time customer question answering
- Pause/resume/skip demo controls
- Comprehensive audit trails
- Scalable architecture for multiple products

## Initial Target: InSign Demo

The first implementation demonstrates InSign (DocuSign alternative) with a 10-minute demo flow:

1. Login to platform
2. Dashboard overview
3. Sign a document
4. Send document for signature
5. Audit trail review

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend)
- API Keys:
  - Anthropic (Claude)
  - ElevenLabs
  - OpenAI (Whisper)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env

# Run server
python -m api.main
```

Server will start at `http://localhost:8000`

### Environment Variables

Create `backend/.env`:

```bash
# Required API Keys
ANTHROPIC_API_KEY=your_anthropic_key
ELEVENLABS_API_KEY=your_elevenlabs_key
OPENAI_API_KEY=your_openai_key

# Demo Environment
INSIGN_DEMO_URL=https://demo.insign.io
INSIGN_DEMO_EMAIL=demo@numberlabs.ai
INSIGN_DEMO_PASSWORD=your_password

# Optional
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│              WebSocket Client + Video Player             │
└──────────────────────┬──────────────────────────────────┘
                       │ WebSocket
┌──────────────────────▼──────────────────────────────────┐
│                  FastAPI Server                          │
│         REST API + WebSocket Streaming                   │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Demo Copilot                            │
│              Main Orchestrator                           │
└─────┬──────────┬──────────┬──────────┬─────────────────┘
      │          │          │          │
   ┌──▼──┐   ┌──▼──┐   ┌──▼──┐   ┌──▼──┐
   │ 🌐  │   │ 🔊  │   │ 🤖  │   │ 📜  │
   │Browser│ │Voice│ │ Q&A │ │Script│
   │Controller│ │Engine│ │Handler│ │     │
   └─────┘   └─────┘   └─────┘   └─────┘
   Playwright ElevenLabs Claude   InSign
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture.

## API Documentation

### Create Demo Session

```bash
POST /demo/create
{
  "product": "insign",
  "customer_name": "Sarah",
  "voice_id": "Rachel",
  "headless": true
}
```

### Start Demo

```bash
POST /demo/{session_id}/start
```

### Ask Question

```bash
POST /demo/{session_id}/question
{
  "question": "How does this compare to DocuSign?"
}
```

### WebSocket Streaming

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/demo/{session_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'screenshot') {
    // Display browser screenshot
  } else if (data.type === 'progress_update') {
    // Update progress bar
  }
};
```

See [docs/API.md](docs/API.md) for complete API reference.

## Demo Scripts

Demo scripts define the flow, narration, and interactions for each product.

### InSign Demo Script

Located at `backend/agents/demo_scripts/insign_demo.py`

To create a new demo script:

1. Copy `insign_demo.py` as a template
2. Define your demo steps
3. Add narration for each action
4. Register in `demo_copilot.py`

See [docs/DEMO_SCRIPTS.md](docs/DEMO_SCRIPTS.md) for guide.

## Testing Locally

```bash
# Terminal 1: Start backend
cd backend
python -m api.main

# Terminal 2: Test with curl
curl -X POST http://localhost:8000/demo/create \
  -H "Content-Type: application/json" \
  -d '{"product": "insign", "customer_name": "Test"}'

# Get session ID from response, then:
curl -X POST http://localhost:8000/demo/{session_id}/start
```

## Project Structure

```
demo-copilot/
├── backend/
│   ├── agents/
│   │   ├── demo_copilot.py          # Main orchestrator
│   │   ├── browser_controller.py    # Playwright wrapper
│   │   ├── voice_engine.py          # ElevenLabs TTS
│   │   ├── question_handler.py      # Claude Q&A
│   │   └── demo_scripts/
│   │       └── insign_demo.py       # InSign demo flow
│   ├── api/
│   │   └── main.py                  # FastAPI server
│   ├── database/
│   │   └── models.py                # PostgreSQL schemas
│   └── requirements.txt
├── frontend/                         # (Coming soon)
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEMO_SCRIPTS.md
└── README.md
```

## Roadmap

### Phase 1: MVP (Current)
- ✅ InSign demo script
- ✅ Browser automation
- ✅ Voice narration
- ✅ Question handling
- ✅ REST API

### Phase 2: Frontend
- [ ] React dashboard
- [ ] Live video streaming
- [ ] Interactive controls
- [ ] Demo analytics

### Phase 3: Scale
- [ ] Multi-product support
- [ ] Custom demo builder
- [ ] Recording playback
- [ ] A/B testing demos

### Phase 4: Production
- [ ] Cloud deployment (Cloud Run)
- [ ] CDN for video streaming
- [ ] Load testing
- [ ] Security hardening

## Contributing

This is an internal Number Labs project. For questions or contributions, contact the AI team.

## License

Proprietary - Number Labs

## Support

For issues or questions:
- Slack: #ai-demos
- Email: ai-team@numberlabs.ai
