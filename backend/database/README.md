# Demo Copilot Database

Complete database schema and utilities for tracking demo sessions, customer interactions, and analytics.

## Database Schema

### Tables

**demo_sessions** - Tracks individual demo sessions
- Customer information (email, name, company, industry)
- Demo configuration (type, duration preference, voice settings)
- Session state (status, current step, timing)
- Analytics (engagement score, questions asked, features shown)

**demo_actions** - Records every action during demos
- Action details (type, description, step number)
- Technical details (selector, value)
- Narration (text, audio URL, duration)
- Timing and status tracking

**customer_questions** - Customer questions and AI responses
- Question text and classification (intent, sentiment)
- AI-generated responses
- Response time and action taken
- Priority tracking

**demo_scripts** - Reusable demo scripts for products
- Script steps and estimated duration
- Product information for Q&A context
- Feature lists and pricing info
- Version control

**demo_analytics** - Aggregated performance metrics
- Daily volume metrics
- Engagement statistics
- Top features requested
- Conversion tracking

## Setup

### 1. Database Connection

Update `backend/.env` with your database URL:

```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname?sslmode=require
```

For Neon PostgreSQL:
```bash
DATABASE_URL=postgresql://neondb_owner:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### 2. Initialize Database

Run the initialization script:

```bash
cd demo-pilot
python scripts/init_database.py
```

This will:
- Create all tables
- Set up indexes
- Seed initial demo scripts

### 3. Run SQL Migration (Alternative)

If you prefer manual SQL migration:

```bash
psql $DATABASE_URL -f backend/database/migrations/001_initial_schema.sql
```

## Usage

### In Python Code

```python
from backend.database import (
    get_db_session,
    create_demo_session,
    DemoSessionCreate
)

# Create a session
db = get_db_session()

# Create demo session
session_data = DemoSessionCreate(
    demo_type="insign",
    customer_name="John Doe",
    customer_email="john@example.com",
    voice_id="Rachel"
)

session = create_demo_session(db, session_data)
print(f"Created session: {session.id}")

db.close()
```

### In FastAPI Endpoints

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.database import get_db, create_demo_session

@app.post("/demo/create")
async def create_demo(
    session_data: DemoSessionCreate,
    db: Session = Depends(get_db)
):
    session = create_demo_session(db, session_data)
    return session
```

## CRUD Operations

### Demo Sessions

```python
from backend.database import crud

# Create
session = crud.create_demo_session(db, session_data)

# Get
session = crud.get_demo_session(db, session_id)

# Update
session = crud.update_demo_session(db, session_id, status="running")

# Start/Complete
session = crud.start_demo_session(db, session_id)
session = crud.complete_demo_session(db, session_id, duration=600)

# Query
active = crud.get_active_sessions(db, limit=10)
customer_sessions = crud.get_sessions_by_customer(db, "user@example.com")
```

### Demo Actions

```python
# Create action
action = crud.create_demo_action(db, session_id, action_data)

# Track action lifecycle
action = crud.start_demo_action(db, action.id)
action = crud.complete_demo_action(db, action.id, duration_ms=500)

# Get all actions for session
actions = crud.get_session_actions(db, session_id)
```

### Customer Questions

```python
# Create question
question = crud.create_customer_question(db, session_id, question_data)

# Add answer
question = crud.answer_customer_question(
    db,
    question.id,
    response_text="Great question! ...",
    response_time_ms=850,
    intent="pricing",
    sentiment="positive"
)

# Get all questions for session
questions = crud.get_session_questions(db, session_id)
```

### Analytics

```python
# Get dashboard stats (last 7 days)
stats = crud.get_dashboard_stats(db, days=7)

# Update daily analytics
analytics = crud.update_daily_analytics(db, datetime.now(), "insign")

# Get analytics range
analytics = crud.get_analytics_range(
    db,
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now(),
    product_name="insign"
)
```

## Models

### Enums

- **DemoStatus**: initialized, running, paused, completed, abandoned, failed
- **ActionType**: click, type, upload, navigate, narrate, scroll, hover, wait
- **QuestionIntent**: clarification, feature_request, pricing, comparison, technical, integration, general
- **Sentiment**: positive, neutral, negative, confused

### Pydantic Schemas

All models have corresponding Pydantic schemas for API validation:
- `DemoSessionCreate`, `DemoSessionResponse`
- `DemoActionCreate`, `DemoActionResponse`
- `CustomerQuestionCreate`, `CustomerQuestionResponse`
- `DemoScriptCreate`, `DemoScriptResponse`
- `DemoAnalyticsResponse`

## Utilities

### Connection Management

```python
from backend.database import check_db_connection, close_db_connection

# Check connection
if check_db_connection():
    print("Connected!")

# Close on shutdown
close_db_connection()
```

### Cleanup

```python
# Delete old sessions (older than 90 days)
deleted_count = crud.delete_old_sessions(db, days=90)
```

## Indexes

The following indexes are created for optimal performance:

- `demo_sessions`: status, demo_type, created_at, customer_email
- `demo_actions`: session_id, (session_id, step_number)
- `customer_questions`: session_id, intent, sentiment
- `demo_scripts`: (product_name, is_active), (script_type, is_active)
- `demo_analytics`: date, (product_name, date)

## Migrations

Future schema changes should be added as numbered migrations:

```
backend/database/migrations/
├── 001_initial_schema.sql
├── 002_add_user_feedback.sql
└── 003_add_recording_metadata.sql
```

## Best Practices

1. **Always use connection pooling** - Handled automatically by SQLAlchemy
2. **Use Depends(get_db)** in FastAPI for automatic cleanup
3. **Commit transactions** after writes
4. **Close sessions** when done (automatic with `get_db()`)
5. **Use indexes** for frequently queried fields
6. **Run analytics updates** asynchronously (background tasks)
7. **Archive old data** regularly using cleanup utilities

## Troubleshooting

### Connection Issues

```python
from backend.database import check_db_connection

if not check_db_connection():
    print("Connection failed - check DATABASE_URL in .env")
```

### Table Creation Fails

```bash
# Drop all tables and recreate
psql $DATABASE_URL -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
python scripts/init_database.py
```

### Performance Issues

- Check indexes: `\di` in psql
- Analyze query plans: `EXPLAIN ANALYZE SELECT ...`
- Monitor connection pool: Check active connections in Neon dashboard

## Schema Diagram

```
demo_sessions
├── id (PK)
├── customer info
├── demo config
└── analytics

demo_actions
├── id (PK)
├── session_id (FK → demo_sessions)
├── action details
└── narration

customer_questions
├── id (PK)
├── session_id (FK → demo_sessions)
├── question/response
└── classification

demo_scripts
├── id (PK)
├── product info
└── steps

demo_analytics
├── id (PK)
├── date
└── metrics
```
