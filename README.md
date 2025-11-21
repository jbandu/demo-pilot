# Demo Copilot - Autonomous Product Demo Agent

An AI-powered sales engineer that autonomously conducts product demonstrations by controlling a live browser, narrating actions with natural voice, and answering customer questions in real-time.

## Overview

Demo Copilot is a proof-of-concept for Number Labs demonstrating agentic AI capabilities. It combines:

- **Browser Automation** (Playwright) - Controls live product interfaces
- **Voice Synthesis** (ElevenLabs) - Natural, conversational narration
- **AI Q&A** (Claude Sonnet 4.5) - Intelligent question handling
- **Real-time Streaming** (WebSocket) - Live video and audio to customers
- **Next.js Frontend** - Modern customer-facing demo interface

## Features

- Fully autonomous product demonstrations
- Natural voice narration with multiple voice options
- Intelligent real-time customer question answering
- Adaptive demo flow (can jump to requested features)
- Pause/resume/stop demo controls
- Sentiment analysis and priority detection
- Customer interest tracking for analytics
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
  - ElevenLabs (for voice)

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Required environment variables:
```bash
ANTHROPIC_API_KEY=your-anthropic-api-key-here
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
```

### 3. Run the Application

**Option A: Simple startup script (recommended)**

```bash
# From project root
python run_server.py
```

**Option B: Manual startup**

```bash
# Terminal 1: Backend
python -m backend.api.main

# Terminal 2: Frontend (in separate terminal)
cd frontend
npm run dev
```

**Access the application:**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Next.js Frontend (TypeScript)               │
│       Demo Selection + Live Demo Viewer + Q&A            │
└──────────────────────┬──────────────────────────────────┘
                       │ WebSocket + REST API
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

## Question Handler Capabilities

The intelligent question handler uses Claude AI to:

1. **Understand Intent**
   - Clarification requests
   - Feature requests
   - Pricing questions
   - Comparisons
   - Technical inquiries

2. **Analyze Sentiment**
   - Positive, neutral, negative, confused
   - Adjusts response tone accordingly

3. **Prioritize Questions**
   - Low, normal, high, critical
   - Routes complex questions to human sales engineers

4. **Adapt Demo Flow**
   - Continue current flow
   - Jump to requested feature
   - Deep dive into current topic
   - Schedule human follow-up

5. **Track Customer Interests**
   - Extract topics of interest
   - Log for analytics and follow-up

## API Documentation

### Start Demo

```bash
POST /api/demo/start
{
  "demo_type": "insign",
  "customer_name": "Sarah Johnson",
  "customer_email": "sarah@company.com",
  "customer_company": "Acme Corp",
  "demo_duration": "standard"
}
```

Response:
```json
{
  "session_id": "uuid-here",
  "status": "started",
  "demo_type": "insign",
  "websocket_url": "ws://localhost:8000/ws/demo/{session_id}",
  "estimated_duration_minutes": 10
}
```

### Ask Question

```bash
POST /api/demo/{session_id}/question
{
  "session_id": "uuid",
  "question": "Can you show me the mobile app?"
}
```

Response includes:
- Natural language answer
- Action to take (continue, jump_to_feature, etc.)
- Intent classification
- Sentiment analysis
- Priority level

### Control Demo

```bash
POST /api/demo/{session_id}/control
{
  "session_id": "uuid",
  "action": "pause"  # or "resume", "stop"
}
```

### Get Demo Status

```bash
GET /api/demo/{session_id}/status
```

Returns current step, progress, messages, etc.

### WebSocket Streaming

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/demo/{session_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch(data.type) {
    case 'video_frame':
      // Display browser screenshot
      break;
    case 'status_update':
      // Update progress bar
      break;
    case 'message':
      // Display conversation message
      break;
  }
};
```

## Project Structure

```
demo-copilot/
├── backend/
│   ├── agents/
│   │   ├── demo_copilot.py          # Main orchestrator
│   │   ├── browser_controller.py    # Playwright wrapper
│   │   ├── voice_engine.py          # ElevenLabs TTS
│   │   ├── question_handler.py      # Claude Q&A with intent analysis
│   │   └── demo_scripts/
│   │       └── insign_demo.py       # InSign demo flow
│   ├── api/
│   │   └── main.py                  # FastAPI server
│   └── database/
│       ├── models.py                # SQLAlchemy models
│       ├── crud.py                  # Database operations
│       └── connection.py            # DB connection
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # Home page (demo selection)
│   │   ├── demo/[sessionId]/
│   │   │   └── page.tsx             # Demo viewer
│   │   ├── layout.tsx               # Root layout
│   │   └── globals.css              # Global styles
│   ├── components/
│   │   └── ui/                      # Reusable UI components
│   ├── package.json
│   └── tsconfig.json
├── run_server.py                    # Simple server startup script
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template
└── README.md
```

## Demo Scripts

Demo scripts define the flow, narration, and interactions for each product.

Located at `backend/agents/demo_scripts/`

Each script includes:
- Step-by-step actions
- Natural voice narration
- Browser interactions
- Feature highlights
- Customization options

## Development

### Adding a New Product Demo

1. Create new script in `backend/agents/demo_scripts/`
2. Define demo steps and narration
3. Add product context to `question_handler.py`
4. Register script in `demo_copilot.py`
5. Add product card to frontend `page.tsx`

### Testing

```bash
# Test question handler
cd backend
python -m agents.question_handler

# Test API endpoints
curl -X GET http://localhost:8000/health

# Test demo creation
curl -X POST http://localhost:8000/api/demo/start \
  -H "Content-Type: application/json" \
  -d '{"demo_type": "insign", "customer_email": "test@example.com"}'
```

## Roadmap

### Phase 1: MVP ✅
- ✅ InSign demo script
- ✅ Browser automation
- ✅ Voice narration
- ✅ Intelligent question handling with Claude
- ✅ REST API
- ✅ Next.js frontend
- ✅ WebSocket streaming
- ✅ Intent analysis and sentiment detection

### Phase 2: Enhancement 🔄
- [ ] Recording and playback
- [ ] Demo analytics dashboard
- [ ] A/B testing for demo scripts
- [ ] Voice input for questions
- [ ] Multi-language support

### Phase 3: Scale
- [ ] Additional product demos (Crew Intelligence)
- [ ] Custom demo builder UI
- [ ] Lead scoring integration
- [ ] CRM integration (Salesforce, HubSpot)

### Phase 4: Production
- [ ] Cloud deployment (AWS/GCP)
- [ ] CDN for video streaming
- [ ] Load testing and optimization
- [ ] Security audit
- [ ] Rate limiting and abuse prevention

## Troubleshooting

### ModuleNotFoundError

Make sure you're running from the project root:
```bash
cd /path/to/demo-pilot
python run_server.py
```

### Playwright browsers not found

```bash
playwright install chromium
```

### API keys not working

Check your `.env` file and make sure keys are set:
```bash
cat .env
# Should show ANTHROPIC_API_KEY and ELEVENLABS_API_KEY
```

### Frontend can't connect to backend

Make sure backend is running on port 8000:
```bash
curl http://localhost:8000/health
```

## Contributing

This is an internal Number Labs project. For questions or contributions, contact the AI team.

## License

Proprietary - Number Labs

## Support

For issues or questions:
- Slack: #ai-demos
- Email: ai-team@numberlabs.ai
