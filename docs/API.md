# Demo Copilot API Documentation

Base URL: `http://localhost:8000` (development)

## Authentication

Currently no authentication required for MVP. Will implement API keys in production.

## REST API Endpoints

### Health Check

#### GET `/`

Health check endpoint

**Response:**
```json
{
  "service": "Demo Copilot API",
  "status": "running",
  "version": "1.0.0",
  "active_sessions": 3
}
```

#### GET `/health`

Detailed health check

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "active_sessions": 3,
  "active_connections": 2
}
```

---

### Demo Management

#### POST `/demo/create`

Create a new demo session

**Request Body:**
```json
{
  "product": "insign",
  "customer_name": "Sarah Johnson",
  "customer_email": "sarah@example.com",
  "voice_id": "Rachel",
  "headless": true
}
```

**Parameters:**
- `product` (required): Product to demo ("insign", "crew")
- `customer_name` (optional): Customer's name for personalization
- `customer_email` (optional): Customer's email
- `voice_id` (optional): ElevenLabs voice ID (default: "Rachel")
- `headless` (optional): Run browser in headless mode (default: true)

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "product": "insign",
  "state": "idle",
  "customer_name": "Sarah Johnson",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Session created successfully
- `500 Internal Server Error` - Failed to create session

---

#### POST `/demo/{session_id}/start`

Start the demo presentation

**Path Parameters:**
- `session_id`: Demo session ID

**Response:**
```json
{
  "status": "started",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Status Codes:**
- `200 OK` - Demo started
- `404 Not Found` - Session not found
- `500 Internal Server Error` - Failed to start demo

**Note:** Demo runs in background. Use WebSocket or status endpoint to monitor progress.

---

#### POST `/demo/{session_id}/control`

Control demo playback (pause, resume, skip)

**Path Parameters:**
- `session_id`: Demo session ID

**Request Body:**
```json
{
  "action": "pause",
  "section": null
}
```

**Actions:**
- `pause` - Pause the demo
- `resume` - Resume from pause
- `skip` - Skip to a specific section (requires `section` parameter)

**Request Body (Skip):**
```json
{
  "action": "skip",
  "section": "dashboard_overview"
}
```

**Available Sections (InSign):**
- `login`
- `dashboard_overview`
- `sign_document`
- `send_document`
- `audit_trail`

**Response:**
```json
{
  "status": "success",
  "action": "pause",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Status Codes:**
- `200 OK` - Control action successful
- `400 Bad Request` - Invalid action
- `404 Not Found` - Session not found
- `500 Internal Server Error` - Action failed

---

#### POST `/demo/{session_id}/question`

Ask a question during the demo

**Path Parameters:**
- `session_id`: Demo session ID

**Request Body:**
```json
{
  "question": "How does InSign compare to DocuSign in terms of pricing?"
}
```

**Response:**
```json
{
  "question": "How does InSign compare to DocuSign in terms of pricing?",
  "answer": "Great question. InSign is typically 50% more affordable than DocuSign. Our Pro plan starts at just $10 per user per month, compared to DocuSign's $20-25 per user. You get unlimited signatures, templates, and all core features at that price point.",
  "response_time_ms": 872,
  "timestamp": "2024-01-15T10:35:00Z"
}
```

**Status Codes:**
- `200 OK` - Question answered
- `404 Not Found` - Session not found
- `500 Internal Server Error` - Question handling failed

---

#### GET `/demo/{session_id}/status`

Get current demo status

**Path Parameters:**
- `session_id`: Demo session ID

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "state": "running",
  "duration_seconds": 245,
  "questions_asked": 3,
  "pauses_count": 1,
  "customer_name": "Sarah Johnson",
  "progress": {
    "current_step": 3,
    "total_steps": 5,
    "progress_percentage": 60.0,
    "current_section": "sign_document"
  }
}
```

**States:**
- `idle` - Session created but not started
- `starting` - Initializing demo
- `running` - Demo in progress
- `paused` - Demo paused by user
- `answering_question` - Answering customer question
- `completed` - Demo finished successfully
- `failed` - Demo encountered an error

**Status Codes:**
- `200 OK` - Status retrieved
- `404 Not Found` - Session not found

---

#### DELETE `/demo/{session_id}`

Stop and delete a demo session

**Path Parameters:**
- `session_id`: Demo session ID

**Response:**
```json
{
  "status": "stopped",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Status Codes:**
- `200 OK` - Session stopped
- `404 Not Found` - Session not found
- `500 Internal Server Error` - Stop failed

---

#### GET `/demo/sessions`

List all active demo sessions

**Response:**
```json
{
  "total": 2,
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "state": "running",
      "duration_seconds": 245,
      "questions_asked": 3,
      "pauses_count": 1,
      "customer_name": "Sarah Johnson",
      "progress": {
        "current_step": 3,
        "total_steps": 5,
        "progress_percentage": 60.0,
        "current_section": "sign_document"
      }
    },
    {
      "session_id": "660f9511-f30c-52e5-b827-557766551111",
      "state": "paused",
      "duration_seconds": 180,
      "questions_asked": 1,
      "pauses_count": 1,
      "customer_name": "John Doe",
      "progress": {
        "current_step": 2,
        "total_steps": 5,
        "progress_percentage": 40.0,
        "current_section": "dashboard_overview"
      }
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Sessions listed

---

## WebSocket API

### WS `/ws/demo/{session_id}`

Real-time streaming endpoint for demo video, audio, and updates

#### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/demo/{session_id}');

ws.onopen = () => {
  console.log('Connected to demo stream');
};

ws.onmessage = (event) => {
  if (event.data instanceof Blob) {
    // Audio chunk
    handleAudioChunk(event.data);
  } else {
    // JSON message
    const message = JSON.parse(event.data);
    handleMessage(message);
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket closed');
};
```

#### Message Types

**1. Screenshot**
```json
{
  "type": "screenshot",
  "data": "base64_encoded_image...",
  "timestamp": "2024-01-15T10:35:00Z"
}
```

**2. State Change**
```json
{
  "type": "state_change",
  "state": "running",
  "timestamp": "2024-01-15T10:35:00Z"
}
```

**3. Progress Update**
```json
{
  "type": "progress_update",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "state": "running",
    "duration_seconds": 245,
    "questions_asked": 3,
    "progress": {
      "current_step": 3,
      "total_steps": 5,
      "progress_percentage": 60.0,
      "current_section": "sign_document"
    }
  },
  "timestamp": "2024-01-15T10:35:00Z"
}
```

**4. Demo Completed**
```json
{
  "type": "demo_completed",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "duration_seconds": 612,
    "questions_asked": 5,
    "pauses_count": 2
  }
}
```

**5. Answer (Response to Question)**
```json
{
  "type": "answer",
  "data": {
    "question": "How does pricing work?",
    "answer": "Great question...",
    "response_time_ms": 872,
    "timestamp": "2024-01-15T10:35:00Z"
  }
}
```

**6. Error**
```json
{
  "type": "error",
  "message": "Session not found"
}
```

#### Client Messages

**Ping (Keep-alive)**
```json
{
  "type": "ping"
}
```

**Response:**
```json
{
  "type": "pong"
}
```

**Ask Question**
```json
{
  "type": "question",
  "question": "How does this compare to DocuSign?"
}
```

---

## Example Workflows

### Complete Demo Flow

```bash
# 1. Create session
SESSION=$(curl -X POST http://localhost:8000/demo/create \
  -H "Content-Type: application/json" \
  -d '{
    "product": "insign",
    "customer_name": "Sarah",
    "voice_id": "Rachel"
  }' | jq -r '.session_id')

echo "Session ID: $SESSION"

# 2. Connect WebSocket (in browser or separate script)
# ws://localhost:8000/ws/demo/$SESSION

# 3. Start demo
curl -X POST http://localhost:8000/demo/$SESSION/start

# 4. Monitor progress
watch -n 2 "curl -s http://localhost:8000/demo/$SESSION/status | jq"

# 5. Ask question (optional)
curl -X POST http://localhost:8000/demo/$SESSION/question \
  -H "Content-Type: application/json" \
  -d '{"question": "How much does this cost?"}'

# 6. Pause demo (optional)
curl -X POST http://localhost:8000/demo/$SESSION/control \
  -H "Content-Type: application/json" \
  -d '{"action": "pause"}'

# 7. Resume demo
curl -X POST http://localhost:8000/demo/$SESSION/control \
  -H "Content-Type: application/json" \
  -d '{"action": "resume"}'

# 8. Stop and cleanup (when done)
curl -X DELETE http://localhost:8000/demo/$SESSION
```

### JavaScript Client Example

```javascript
class DemoCopilotClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.sessionId = null;
    this.ws = null;
  }

  async createDemo(options) {
    const response = await fetch(`${this.baseUrl}/demo/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(options)
    });
    const data = await response.json();
    this.sessionId = data.session_id;
    return data;
  }

  connectWebSocket(onMessage) {
    this.ws = new WebSocket(`${this.baseUrl.replace('http', 'ws')}/ws/demo/${this.sessionId}`);
    this.ws.onmessage = onMessage;
    return this.ws;
  }

  async startDemo() {
    return fetch(`${this.baseUrl}/demo/${this.sessionId}/start`, {
      method: 'POST'
    }).then(r => r.json());
  }

  async askQuestion(question) {
    return fetch(`${this.baseUrl}/demo/${this.sessionId}/question`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    }).then(r => r.json());
  }

  async pause() {
    return this.control('pause');
  }

  async resume() {
    return this.control('resume');
  }

  async control(action, section = null) {
    return fetch(`${this.baseUrl}/demo/${this.sessionId}/control`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, section })
    }).then(r => r.json());
  }

  async getStatus() {
    return fetch(`${this.baseUrl}/demo/${this.sessionId}/status`)
      .then(r => r.json());
  }

  async stop() {
    return fetch(`${this.baseUrl}/demo/${this.sessionId}`, {
      method: 'DELETE'
    }).then(r => r.json());
  }
}

// Usage
const client = new DemoCopilotClient();

// Create and start demo
await client.createDemo({
  product: 'insign',
  customer_name: 'Sarah',
  voice_id: 'Rachel'
});

// Connect WebSocket
client.connectWebSocket((event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data.type);

  if (data.type === 'screenshot') {
    updateVideoFrame(data.data);
  } else if (data.type === 'progress_update') {
    updateProgress(data.data.progress);
  }
});

// Start demo
await client.startDemo();

// Ask question later
await client.askQuestion('How does pricing work?');
```

---

## Error Handling

All endpoints return standard HTTP error responses:

**400 Bad Request**
```json
{
  "detail": "Invalid action"
}
```

**404 Not Found**
```json
{
  "detail": "Session not found"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Demo failed: Connection timeout"
}
```

---

## Rate Limits

Currently no rate limits in MVP. Production will implement:

- 10 concurrent sessions per IP
- 100 API requests per minute
- 50 questions per demo

---

## API Versioning

Current version: `v1.0.0`

Future versions will use URL prefix: `/v2/demo/create`
