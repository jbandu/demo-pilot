# Demo Copilot Architecture

## System Overview

Demo Copilot is an autonomous AI agent that conducts product demonstrations by orchestrating multiple specialized components:

```
                    ┌─────────────────────┐
                    │   Customer/Client   │
                    │   (Web Browser)     │
                    └──────────┬──────────┘
                               │ HTTP/WebSocket
                    ┌──────────▼──────────┐
                    │   Frontend Layer    │
                    │  (React + Next.js)  │
                    │  - Video Player     │
                    │  - Controls         │
                    │  - Question Input   │
                    └──────────┬──────────┘
                               │ WebSocket/REST
┌──────────────────────────────▼──────────────────────────────┐
│                      Backend Layer                            │
│                     (FastAPI Server)                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              REST API Endpoints                      │    │
│  │  - POST /demo/create                                 │    │
│  │  - POST /demo/{id}/start                             │    │
│  │  - POST /demo/{id}/question                          │    │
│  │  - POST /demo/{id}/control (pause/resume/skip)      │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           WebSocket Streaming                        │    │
│  │  - Real-time screenshots                             │    │
│  │  - Audio chunks                                      │    │
│  │  - State updates                                     │    │
│  │  - Progress tracking                                 │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                   Demo Copilot Agent                          │
│                  (Main Orchestrator)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  State Machine:                                       │   │
│  │  IDLE → STARTING → RUNNING ⇄ PAUSED                  │   │
│  │                            ⇄ ANSWERING_QUESTION      │   │
│  │                            → COMPLETED/FAILED        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌────────┐  ┌───────┐  ┌─────────┐  ┌──────────────┐     │
│  │Browser │  │Voice  │  │Question │  │Demo Scripts  │     │
│  │Control │  │Engine │  │Handler  │  │(InSign, etc) │     │
│  └────┬───┘  └───┬───┘  └────┬────┘  └──────┬───────┘     │
└───────┼──────────┼───────────┼───────────────┼─────────────┘
        │          │           │               │
        ▼          ▼           ▼               ▼
   Playwright  ElevenLabs  Anthropic      Product Logic
   (Browser)   (TTS)       (Claude)       (Demo Steps)
```

## Core Components

### 1. Demo Copilot (Main Orchestrator)

**File:** `backend/agents/demo_copilot.py`

**Responsibilities:**
- Session management and state tracking
- Component coordination
- Event handling and callbacks
- Progress monitoring

**Key Methods:**
- `initialize(product, customer_name)` - Set up demo for a product
- `start_demo()` - Begin autonomous demonstration
- `pause_demo()` / `resume_demo()` - Demo control
- `ask_question(question)` - Handle customer questions
- `get_status()` - Get current demo state

**State Machine:**
```
IDLE
  ↓ initialize()
STARTING
  ↓ start_demo()
RUNNING ←→ PAUSED
  ↓        ↓ pause_demo()
  ↓        ↓ resume_demo()
  ↓
  ↔ ANSWERING_QUESTION
  ↓ ask_question()
  ↓
COMPLETED / FAILED
```

### 2. Browser Controller

**File:** `backend/agents/browser_controller.py`

**Responsibilities:**
- Launch and manage Playwright browser
- Execute navigation and interactions
- Capture screenshots and recordings
- Highlight elements for visual emphasis

**Key Features:**
- Headless or headed mode
- Video recording
- Screenshot streaming
- Action logging
- Smart waits and error handling

**API:**
```python
await browser.start()
await browser.navigate("https://example.com")
await browser.click("#submit-button", "Submit")
await browser.type_text("#email", "user@example.com")
await browser.screenshot()  # Returns bytes
await browser.stop()
```

### 3. Voice Engine

**File:** `backend/agents/voice_engine.py`

**Responsibilities:**
- Text-to-speech using ElevenLabs
- Natural narration generation
- Audio streaming
- Voice customization

**Features:**
- Multiple voice options (Rachel, Adam, Bella, etc.)
- Streaming and non-streaming modes
- Voice settings (stability, similarity, style)
- Pre-built narrator for common phrases

**API:**
```python
voice = VoiceEngine(voice_id="Rachel")
narrator = DemoNarrator(voice)

await narrator.greet("Sarah")
await narrator.introduce_section("Dashboard")
await voice.speak("Now I'll click the submit button")
```

### 4. Question Handler

**File:** `backend/agents/question_handler.py`

**Responsibilities:**
- Answer customer questions using Claude
- Maintain conversation context
- Suggest follow-up questions
- Track interaction history

**Context Management:**
- Product context (features, pricing, differentiators)
- Demo context (current step, progress)
- Conversation history (last 20 exchanges)

**API:**
```python
handler = QuestionHandler()
handler.set_product_context(INSIGN_PRODUCT_CONTEXT)
handler.set_demo_context({"current_step": "Dashboard", "progress": 40})

result = await handler.answer_question("How does pricing work?")
# Returns: {question, answer, response_time_ms, confidence, timestamp}
```

### 5. Demo Scripts

**File:** `backend/agents/demo_scripts/insign_demo.py`

**Responsibilities:**
- Define product-specific demo flow
- Provide step-by-step narration
- Coordinate browser actions with voice
- Track demo progress

**Structure:**
```python
class InSignDemoScript:
    async def run_full_demo(self, customer_name):
        await self._opening_greeting(customer_name)
        await self._step_login()
        await self._step_dashboard_overview()
        await self._step_sign_document()
        await self._step_send_document()
        await self._step_audit_trail()
        await self._closing_remarks()
```

## Data Flow

### Starting a Demo

```
1. Client → POST /demo/create
   └→ FastAPI creates DemoCopilot instance
      └→ DemoCopilot.initialize(product="insign")
         ├→ BrowserController.start()
         ├→ Load InSignDemoScript
         └→ QuestionHandler.set_product_context()

2. Client → POST /demo/{id}/start
   └→ FastAPI triggers DemoCopilot.start_demo() in background
      └→ InSignDemoScript.run_full_demo()
         ├→ For each step:
         │  ├→ Voice.speak(narration)
         │  │  └→ Callback: on_audio_chunk → WebSocket
         │  └→ Browser.navigate/click/type()
         │     └→ Callback: on_screenshot → WebSocket
         └→ Update progress → WebSocket
```

### Answering a Question

```
Client → POST /demo/{id}/question {"question": "..."}
  └→ DemoCopilot.ask_question()
     ├→ State: RUNNING → ANSWERING_QUESTION
     ├→ QuestionHandler.answer_question()
     │  └→ Claude API (with product + demo context)
     ├→ Voice.speak(answer)
     │  └→ Stream audio → WebSocket
     └→ State: ANSWERING_QUESTION → RUNNING
```

### Real-time Streaming (WebSocket)

```
Client → WebSocket /ws/demo/{id}
  └→ FastAPI accepts connection
     └→ Register callbacks on DemoCopilot:
        ├→ on_screenshot → send_json({type: "screenshot", data: base64})
        ├→ on_audio → send_bytes(audio_chunk)
        ├→ on_state_change → send_json({type: "state_change", state: "..."})
        └→ on_progress_update → send_json({type: "progress", data: {...}})
```

## Database Schema

**File:** `backend/database/models.py`

### Tables

**demo_sessions**
- Tracks each demo session
- Status, timing, customer info
- Progress and metrics

**demo_interactions**
- Customer questions and answers
- Timestamps and response times
- Confidence scores

**demo_recordings**
- Video recordings metadata
- Storage URLs
- Duration and file size

**demo_analytics**
- Aggregated metrics by product/date
- Completion rates, avg duration
- Engagement scores

## Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│            User's Browser                        │
└──────────────┬──────────────────────────────────┘
               │ HTTPS/WSS
┌──────────────▼──────────────────────────────────┐
│           Railway (Frontend)                     │
│   Next.js App (Docker Container)                │
└──────────────┬──────────────────────────────────┘
               │ WSS/HTTPS
┌──────────────▼──────────────────────────────────┐
│           Railway (Backend)                      │
│   - FastAPI Server                               │
│   - Demo Copilot Agents                          │
│   - Playwright Browser (Chromium)                │
│   Auto-scaling: 0-10 instances                   │
└──────────────┬──────────────────────────────────┘
               │
      ┌────────┴────────┬────────────────┐
      ▼                 ▼                ▼
┌───────────┐   ┌──────────────┐  ┌──────────┐
│  Neon     │   │  Redis       │  │  GCS     │
│PostgreSQL │   │  (Sessions)  │  │(Videos)  │
│(Analytics)│   │              │  │          │
└───────────┘   └──────────────┘  └──────────┘
```

## Security Considerations

### Browser Isolation
- Each demo runs in isolated browser context
- Credentials stored securely in environment variables
- Automatic cleanup on session end

### API Security
- Rate limiting on endpoints
- Session authentication
- CORS configuration
- Input validation

### Data Privacy
- Customer questions logged with consent
- PII handled per GDPR requirements
- Recordings stored encrypted

## Performance Optimization

### Browser Performance
- Headless mode for production
- Viewport optimization (1920x1080)
- Network request filtering
- Resource caching

### Voice Generation
- Use `eleven_turbo_v2_5` (fastest model)
- Stream audio chunks
- Pre-generate common phrases

### API Response Times
- Claude: ~500-1000ms per question
- ElevenLabs: ~200-500ms per sentence
- Browser actions: ~100-500ms each

### Scaling
- Horizontal scaling via Cloud Run
- Session affinity via sticky sessions
- Redis for session state
- CDN for video streaming

## Monitoring & Observability

### Metrics to Track
- Demo completion rate
- Average demo duration
- Questions per demo
- Error rates
- Response times (API, voice, browser)

### Logging
- Structured logging (JSON)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Correlation IDs for request tracing
- Separate logs per component

### Alerts
- Demo failure rate > 5%
- API response time > 2s
- Browser crashes
- Voice/LLM API errors

## Extension Points

### Adding New Products
1. Create demo script: `backend/agents/demo_scripts/new_product_demo.py`
2. Define product context in `question_handler.py`
3. Register in `demo_copilot.py`

### Custom Voice Personalities
1. Add voice ID to `VoiceEngine.VOICES`
2. Adjust voice settings (stability, similarity, style)
3. Test with different narration styles

### Advanced Browser Interactions
1. Extend `BrowserController` with new methods
2. Add element highlighting, annotations
3. Implement smart scrolling, zoom

### Analytics & Insights
1. Add custom metrics to `demo_analytics` table
2. Implement aggregation queries
3. Build dashboard for demo performance
