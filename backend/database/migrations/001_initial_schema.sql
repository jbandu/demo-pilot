-- Demo Copilot Initial Database Schema
-- Run this in your Neon PostgreSQL database

-- Demo Sessions
CREATE TABLE IF NOT EXISTS demo_sessions (
    id VARCHAR(36) PRIMARY KEY,
    customer_email VARCHAR(255),
    customer_name VARCHAR(255),
    customer_company VARCHAR(255),
    customer_industry VARCHAR(100),
    demo_type VARCHAR(50) NOT NULL,
    demo_duration_preference VARCHAR(20) DEFAULT 'standard',
    demo_customization JSONB,
    voice_id VARCHAR(50) DEFAULT 'Rachel',
    voice_speed FLOAT DEFAULT 1.0,
    status VARCHAR(20) DEFAULT 'initialized',
    current_step INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    browser_session_id VARCHAR(100),
    recording_url TEXT,
    engagement_score FLOAT,
    questions_asked INTEGER DEFAULT 0,
    pauses_count INTEGER DEFAULT 0,
    features_shown JSONB DEFAULT '[]',
    customer_interests JSONB DEFAULT '[]',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Demo Actions
CREATE TABLE IF NOT EXISTS demo_actions (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) REFERENCES demo_sessions(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    action_description TEXT NOT NULL,
    selector VARCHAR(500),
    value TEXT,
    narration_text TEXT,
    narration_audio_url TEXT,
    narration_duration_ms INTEGER,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT
);

-- Customer Questions
CREATE TABLE IF NOT EXISTS customer_questions (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) REFERENCES demo_sessions(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_audio_url TEXT,
    asked_at_step INTEGER NOT NULL,
    response_text TEXT,
    response_audio_url TEXT,
    response_action VARCHAR(50),
    intent VARCHAR(50),
    sentiment VARCHAR(20),
    priority VARCHAR(20) DEFAULT 'normal',
    created_at TIMESTAMP DEFAULT NOW(),
    response_time_ms INTEGER
);

-- Demo Scripts
CREATE TABLE IF NOT EXISTS demo_scripts (
    id VARCHAR(36) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    script_version VARCHAR(20) DEFAULT '1.0',
    script_type VARCHAR(20) DEFAULT 'standard',
    steps JSONB NOT NULL,
    total_duration_estimate_minutes INTEGER NOT NULL,
    product_description TEXT,
    key_features JSONB DEFAULT '[]',
    pricing_info TEXT,
    target_customers JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Demo Analytics
CREATE TABLE IF NOT EXISTS demo_analytics (
    id VARCHAR(36) PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    product_name VARCHAR(100),
    total_demos_started INTEGER DEFAULT 0,
    total_demos_completed INTEGER DEFAULT 0,
    total_demos_abandoned INTEGER DEFAULT 0,
    avg_duration_seconds FLOAT,
    avg_completion_rate FLOAT,
    avg_questions_per_demo FLOAT,
    avg_engagement_score FLOAT,
    top_features_requested JSONB DEFAULT '[]',
    top_customer_concerns JSONB DEFAULT '[]',
    demos_leading_to_signup INTEGER DEFAULT 0,
    conversion_rate FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_demo_sessions_status ON demo_sessions(status);
CREATE INDEX IF NOT EXISTS idx_demo_sessions_demo_type ON demo_sessions(demo_type);
CREATE INDEX IF NOT EXISTS idx_demo_sessions_created_at ON demo_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_demo_sessions_customer_email ON demo_sessions(customer_email);

CREATE INDEX IF NOT EXISTS idx_demo_actions_session_id ON demo_actions(session_id);
CREATE INDEX IF NOT EXISTS idx_demo_actions_step_number ON demo_actions(session_id, step_number);

CREATE INDEX IF NOT EXISTS idx_customer_questions_session_id ON customer_questions(session_id);
CREATE INDEX IF NOT EXISTS idx_customer_questions_intent ON customer_questions(intent);
CREATE INDEX IF NOT EXISTS idx_customer_questions_sentiment ON customer_questions(sentiment);

CREATE INDEX IF NOT EXISTS idx_demo_scripts_product ON demo_scripts(product_name, is_active);
CREATE INDEX IF NOT EXISTS idx_demo_scripts_type ON demo_scripts(script_type, is_active);

CREATE INDEX IF NOT EXISTS idx_demo_analytics_date ON demo_analytics(date);
CREATE INDEX IF NOT EXISTS idx_demo_analytics_product ON demo_analytics(product_name, date);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for demo_sessions
CREATE TRIGGER update_demo_sessions_updated_at BEFORE UPDATE ON demo_sessions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for demo_scripts
CREATE TRIGGER update_demo_scripts_updated_at BEFORE UPDATE ON demo_scripts
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE demo_sessions IS 'Tracks individual demo sessions with customer info and analytics';
COMMENT ON TABLE demo_actions IS 'Records every action taken during a demo (clicks, navigation, narration)';
COMMENT ON TABLE customer_questions IS 'Stores customer questions and AI-generated responses during demos';
COMMENT ON TABLE demo_scripts IS 'Stores reusable demo scripts for different products and types';
COMMENT ON TABLE demo_analytics IS 'Aggregated analytics for tracking demo performance over time';

-- Insert sample demo script for InSign
INSERT INTO demo_scripts (
    id,
    product_name,
    script_version,
    script_type,
    steps,
    total_duration_estimate_minutes,
    product_description,
    key_features,
    pricing_info,
    is_active
) VALUES (
    'insign-standard-v1',
    'insign',
    '1.0',
    'standard',
    '[
        {"step": 1, "name": "login", "description": "Login to InSign platform"},
        {"step": 2, "name": "dashboard", "description": "Overview of dashboard features"},
        {"step": 3, "name": "sign_document", "description": "Sign a document demo"},
        {"step": 4, "name": "send_document", "description": "Send document for signature"},
        {"step": 5, "name": "audit_trail", "description": "Review audit trail and compliance"}
    ]'::jsonb,
    10,
    'InSign is a modern electronic signature platform that simplifies document signing and management.',
    '["Unlimited signatures", "Template library", "Bulk send", "Mobile apps", "API access", "Audit trails"]'::jsonb,
    'Starting at $10/user/month for Pro plan',
    TRUE
) ON CONFLICT (id) DO NOTHING;
