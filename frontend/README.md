# Demo Copilot Frontend

Next.js frontend for the Demo Copilot system.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Run development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000)

## Features

- **Home Page**: Select demo type and provide customer information
- **Demo Viewer**: Real-time demo streaming with WebSocket connection
- **Interactive Q&A**: Ask questions during the demo
- **Progress Tracking**: Visual progress bar and step indicators

## Tech Stack

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Radix UI components
- Lucide icons

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`:

- `POST /api/demo/start` - Start a new demo
- `GET /api/demo/{session_id}/status` - Get demo status
- `POST /api/demo/{session_id}/question` - Ask a question
- `POST /api/demo/{session_id}/control` - Control demo (pause/resume/stop)
- `WS /ws/demo/{session_id}` - WebSocket for real-time updates

## Development

The app uses:
- Server Components by default
- Client Components for interactive features (`'use client'` directive)
- TypeScript for type safety
- CSS variables for theming
