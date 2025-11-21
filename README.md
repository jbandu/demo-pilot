# 🤖 Demo Copilot

> An AI-powered autonomous sales engineer that gives product demonstrations through natural voice conversations and live browser automation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)

---

## 🎯 Overview

Demo Copilot is Number Labs' proof-of-concept for autonomous AI agents. It demonstrates our capability to build intelligent agents that can:

- 🎭 **Give complete product demos autonomously**
- 🌐 **Control web browsers with human-like behavior**
- 🎙️ **Narrate actions in natural voice** (ElevenLabs)
- 🤝 **Answer customer questions interactively** (Claude Sonnet 4)
- 🎯 **Adapt demos based on customer interests**
- 📊 **Track engagement analytics**

**Why we built this:** Before selling AI agents to airlines for crew operations, baggage handling, and flight planning, we're proving we can build agents that work autonomously by automating our own sales process.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Customer Browser                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Video Stream │  │ Voice Audio  │  │ Chat Panel   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          │             WebSocket               │
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────────┐
│                    FastAPI Backend                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            Demo Copilot Orchestrator                   │  │
│  │              (LangGraph + Claude)                      │  │
│  └────┬─────────────┬─────────────┬─────────────┬────────┘  │
│       │             │             │             │            │
│  ┌────▼────┐  ┌────▼────┐  ┌────▼────┐  ┌────▼────┐       │
│  │ Browser │  │  Voice  │  │Question │  │  Demo   │       │
│  │Controller│  │ Engine  │  │ Handler │  │ Scripts │       │
│  │(Playwright)│(ElevenLabs)│(Claude)  │  │         │       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
└──────────────────────────────────────────────────────────────┘
          │                                      │
          │                                      │
┌─────────▼──────────┐                 ┌────────▼──────────┐
│  Product Instance  │                 │   PostgreSQL      │
│  (InSign Demo)     │                 │  (Sessions,       │
│                    │                 │   Analytics)      │
└────────────────────┘                 └───────────────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

---

## ✨ Features

### 🎬 Autonomous Demos
- Full product walkthroughs without human intervention
- Natural mouse movements and typing
- Realistic pauses and pacing
- Error recovery and retry logic

### 🗣️ Natural Voice Narration
- Multiple voice options (Rachel, Drew, Paul)
- Contextual explanations
- Adjustable speed and tone
- Synchronized with browser actions

### 💬 Intelligent Q&A
- Real-time question answering
- Intent classification (pricing, features, technical, etc.)
- Sentiment analysis (positive, negative, confused)
- Priority detection (low, normal, high, critical)
- Adaptive responses based on customer mood

### 🎯 Demo Adaptation
- Jump to requested features
- Deep dive into topics of interest
- Skip or repeat sections
- Personalized based on customer profile

### 📊 Analytics
- Demo completion rates
- Question tracking
- Feature interest heatmaps
- Customer sentiment trends
- Engagement scoring

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/numberlabs/demo-copilot.git
cd demo-copilot

# Run automated setup
./scripts/setup.sh
```

This installs all dependencies, sets up virtual environments, and creates configuration files.

### 2. Configure API Keys

```bash
# Edit .env file
nano .env
```

Add your API keys:
```bash
ANTHROPIC_API_KEY=your-anthropic-key-here
ELEVENLABS_API_KEY=your-elevenlabs-key-here
```

### 3. Start Development

```bash
# Start both backend and frontend
./scripts/start-dev.sh

# Or start backend only
python run_server.py
```

**Access points:**
- 🌐 Frontend: http://localhost:3000
- 📦 Backend API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

### 4. Verify Health

```bash
./scripts/check-health.sh
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [API Documentation](docs/API.md) | REST API endpoints and WebSocket protocol |
| [Architecture Guide](docs/ARCHITECTURE.md) | System design and component details |
| [Demo Scripts](docs/DEMO_SCRIPTS.md) | How to create custom demo flows |
| [Deployment Guide](docs/DEPLOYMENT.md) | Production deployment instructions |
| [Contributing](CONTRIBUTING.md) | Guidelines for contributors |

---

## 🎮 Usage Examples

### Start a Demo via API

```bash
curl -X POST http://localhost:8000/api/demo/start \
  -H "Content-Type: application/json" \
  -d '{
    "demo_type": "insign",
    "customer_name": "Sarah Johnson",
    "customer_email": "sarah@acme.com",
    "demo_duration": "standard"
  }'
```

### Ask a Question

```bash
curl -X POST http://localhost:8000/api/demo/{session_id}/question \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Can you show me the mobile app?"
  }'
```

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/demo/{session_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch(data.type) {
    case 'video_frame':
      // Display video frame
      break;
    case 'status_update':
      // Update progress
      break;
    case 'message':
      // Show conversation message
      break;
  }
};
```

---

## 🛠️ Development

### Available Scripts

```bash
./scripts/setup.sh           # Initial setup
./scripts/start-dev.sh        # Start development servers
./scripts/stop-dev.sh         # Stop all servers
./scripts/check-health.sh     # Check system health
./scripts/reset-demo-env.sh   # Reset environment
./scripts/test.sh             # Run tests
```

### Project Structure

```
demo-copilot/
├── backend/
│   ├── agents/
│   │   ├── demo_copilot.py          # Main orchestrator
│   │   ├── browser_controller.py    # Browser automation
│   │   ├── voice_engine.py          # Text-to-speech
│   │   ├── question_handler.py      # Q&A with Claude
│   │   └── demo_scripts/
│   │       └── insign_demo.py       # InSign demo flow
│   ├── api/
│   │   └── main.py                  # FastAPI server
│   └── database/
│       ├── models.py                # Database models
│       ├── crud.py                  # CRUD operations
│       └── connection.py            # DB connection
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # Home page
│   │   └── demo/[sessionId]/
│   │       └── page.tsx             # Demo viewer
│   └── components/
│       └── ui/                      # UI components
├── scripts/                         # Automation scripts
├── docs/                            # Documentation
├── run_server.py                    # Server launcher
├── requirements.txt                 # Python dependencies
└── .env.example                     # Environment template
```

### Adding a New Product Demo

1. Create script in `backend/agents/demo_scripts/`
2. Define demo steps and narration
3. Add product context to `question_handler.py`
4. Register in `demo_copilot.py`
5. Add product card to frontend

See [docs/DEMO_SCRIPTS.md](docs/DEMO_SCRIPTS.md) for detailed guide.

---

## 🧪 Testing

```bash
# Run all tests
./scripts/test.sh

# Backend tests only
cd backend
pytest tests/ -v

# Frontend tests only
cd frontend
npm test

# Check health
./scripts/check-health.sh
```

---

## 📊 Current Demos

### InSign (Electronic Signatures)
- **Duration:** 10 minutes
- **Features:** Document signing, sending, audit trails
- **Differentiator:** 50-70% cheaper than DocuSign
- **Demo Script:** `backend/agents/demo_scripts/insign_demo.py`

### Crew Intelligence (Coming Soon)
- **Duration:** 15 minutes
- **Features:** Crew pay, FAA compliance, voice AI
- **Differentiator:** 30% reduction in pay claims
- **Status:** In development

---

## 🗺️ Roadmap

### Phase 1: MVP ✅
- ✅ InSign demo script
- ✅ Browser automation with Playwright
- ✅ Voice narration with ElevenLabs
- ✅ Intelligent Q&A with Claude
- ✅ REST API and WebSocket streaming
- ✅ Next.js frontend
- ✅ Intent analysis and sentiment detection

### Phase 2: Enhancement 🚧
- ⏳ Recording and playback
- ⏳ Demo analytics dashboard
- ⏳ A/B testing for demo scripts
- ⏳ Voice input for questions
- ⏳ Multi-language support

### Phase 3: Scale
- [ ] Crew Intelligence demo
- [ ] Custom demo builder UI
- [ ] Lead scoring integration
- [ ] CRM integration (Salesforce, HubSpot)

### Phase 4: Production
- [ ] Cloud deployment (AWS/GCP)
- [ ] CDN for video streaming
- [ ] Load testing & optimization
- [ ] Security audit
- [ ] Rate limiting

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'backend'"

Make sure you're running from the project root:
```bash
cd /path/to/demo-copilot
python run_server.py
```

### "Playwright browsers not found"

Install browsers:
```bash
playwright install chromium
```

### "Port already in use"

Stop existing servers:
```bash
./scripts/stop-dev.sh
```

### Database errors

Reset the database:
```bash
./scripts/reset-demo-env.sh
```

### More help

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) or check logs:
```bash
tail -f logs/backend.log
tail -f logs/frontend.log
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Code style guidelines
- Development workflow
- Pull request process
- Testing requirements

---

## 📝 License

Proprietary - Number Labs

Internal use only. Not for distribution.

---

## 🙏 Acknowledgments

Built by the Number Labs AI team:
- **AI/ML:** Claude Sonnet 4 (Anthropic)
- **Voice:** ElevenLabs TTS
- **Browser:** Playwright
- **Framework:** FastAPI + Next.js

---

## 📧 Support

For questions or issues:
- 💬 Slack: #ai-demos
- ✉️ Email: ai-team@numberlabs.ai
- 📚 Docs: [docs/](docs/)

---

<div align="center">

**[Documentation](docs/) • [API Reference](docs/API.md) • [Architecture](docs/ARCHITECTURE.md)**

Made with ❤️ by Number Labs AI Team

</div>
