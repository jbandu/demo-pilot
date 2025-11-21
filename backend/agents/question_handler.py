import logging
from typing import Dict, Any, Optional, List
from anthropic import Anthropic
import json

logger = logging.getLogger(__name__)


class QuestionHandler:
    """
    Handles customer questions during demos using Claude.

    Capabilities:
    - Understand question intent
    - Generate natural responses
    - Decide whether to continue demo or jump to feature
    - Classify question sentiment and priority
    - Extract customer interests
    """

    def __init__(self, anthropic_client: Anthropic):
        self.anthropic = anthropic_client
        self.model = "claude-sonnet-4-20250514"

    async def handle_question(
        self,
        question: str,
        demo_context: Dict[str, Any],
        current_step: int
    ) -> Dict[str, Any]:
        """
        Process customer question and generate response.

        Args:
            question: Customer's question text
            demo_context: Current demo state and context
            current_step: Current step number in demo

        Returns:
            Dict containing:
                - answer: Natural language response
                - action: 'continue', 'jump_to_feature', 'deep_dive', 'schedule_human'
                - feature: Feature to jump to (if applicable)
                - intent: Question intent classification
                - sentiment: Customer sentiment
                - priority: Question priority
        """
        logger.info(f"Processing question: {question}")

        # Build context for Claude
        demo_type = demo_context.get('demo_type', 'unknown')
        customer_info = demo_context.get('customer_context', {})
        steps_completed = current_step
        total_steps = len(demo_context.get('demo_script', []))

        # Get available features from demo script
        available_features = self._extract_available_features(demo_context.get('demo_script', []))

        prompt = self._build_prompt(
            question=question,
            demo_type=demo_type,
            customer_info=customer_info,
            steps_completed=steps_completed,
            total_steps=total_steps,
            available_features=available_features
        )

        # Call Claude
        try:
            response = self.anthropic.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=self._get_system_prompt(demo_type),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse response
            response_text = response.content[0].text
            result = self._parse_response(response_text)

            logger.info(f"Generated response - Action: {result['action']}, Sentiment: {result['sentiment']}")

            return result

        except Exception as e:
            logger.error(f"Error processing question: {e}", exc_info=True)
            return self._get_fallback_response()

    def _get_system_prompt(self, demo_type: str) -> str:
        """Get system prompt for Claude based on demo type"""

        base_prompt = """You are Demo Copilot, an AI sales engineer from Number Labs giving product demonstrations.

You are currently giving a live demo and a customer has asked you a question. Your goals:

1. **Answer naturally and conversationally** - You're having a dialogue, not giving a speech
2. **Be helpful and enthusiastic** - You're excited about the product
3. **Stay concise** - Keep responses under 100 words unless deep dive is requested
4. **Adapt the demo** - If they ask about a feature, offer to show it
5. **Build rapport** - Use their name if you know it, acknowledge their interests

Your personality:
- Professional but friendly
- Technically knowledgeable but not condescending
- Enthusiastic about the product
- Patient with questions
- Focused on customer needs

When responding, you should also decide:
- **continue**: Answer and continue current demo flow
- **jump_to_feature**: Jump directly to demonstrate the feature they asked about
- **deep_dive**: Go deeper into current topic
- **schedule_human**: Complex question requiring human sales engineer"""

        product_specific = {
            'insign': """
The product is InSign - a DocuSign alternative with:
- Electronic signatures (draw, type, or upload)
- Document sending with multiple signers
- Signing order control
- Audit trails (FREE, unlike DocuSign's $20/user/month)
- Templates and bulk sending
- API integration
- Mobile apps
- Custom branding
- 50-70% cheaper than DocuSign
- Unlimited users model

Key differentiators to emphasize:
1. Cost savings vs DocuSign
2. Unlimited users
3. Free audit trails
4. All features included (no upsells)
5. Simple, modern interface""",

            'crew_intelligence': """
The product is Number Labs Crew Intelligence for airlines:
- Automated crew pay calculations
- Proactive error detection (30% reduction in claims)
- Voice AI assistant for crew inquiries
- FAA Part 117 compliance monitoring
- Real-time schedule optimization
- Integration with legacy crew systems
- 8-agent AI system working together

Key differentiators:
1. Prevents errors before they happen
2. Voice interface for busy crew members
3. Saves millions in claims and admin time
4. Works with existing airline systems"""
        }

        return base_prompt + "\n\n" + product_specific.get(demo_type, "")

    def _build_prompt(
        self,
        question: str,
        demo_type: str,
        customer_info: Dict[str, Any],
        steps_completed: int,
        total_steps: int,
        available_features: List[str]
    ) -> str:
        """Build prompt for Claude"""

        customer_context = ""
        if customer_info.get('name'):
            customer_context += f"Customer name: {customer_info['name']}\n"
        if customer_info.get('company'):
            customer_context += f"Company: {customer_info['company']}\n"
        if customer_info.get('industry'):
            customer_context += f"Industry: {customer_info['industry']}\n"
        if customer_info.get('interests'):
            customer_context += f"Expressed interests: {', '.join(customer_info['interests'])}\n"

        prompt = f"""CUSTOMER QUESTION: "{question}"

DEMO CONTEXT:
{customer_context}
Demo progress: Step {steps_completed + 1} of {total_steps}
Product: {demo_type}

AVAILABLE FEATURES TO DEMONSTRATE:
{chr(10).join(f"- {feature}" for feature in available_features)}

RESPOND WITH A JSON OBJECT:
{{
    "answer": "Your natural, conversational response to the customer (100 words max)",
    "action": "continue|jump_to_feature|deep_dive|schedule_human",
    "feature": "name of feature to jump to (if action is jump_to_feature)",
    "intent": "clarification|feature_request|pricing|comparison|technical|general",
    "sentiment": "positive|neutral|negative|confused",
    "priority": "low|normal|high|critical",
    "customer_interests": ["list", "of", "topics", "customer", "is", "interested", "in"]
}}

GUIDELINES:
- If they ask "can you show me X", set action to "jump_to_feature" and feature to X
- If they seem confused or negative, be extra helpful
- If question requires detailed product knowledge you don't have, set action to "schedule_human"
- If they're asking about pricing in detail, offer to connect with sales
- Track what they're interested in for analytics

REMEMBER: You're having a conversation, not reading a script. Be natural!"""

        return prompt

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's JSON response"""
        try:
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text.strip()

            result = json.loads(json_text)

            # Validate required fields
            required_fields = ['answer', 'action', 'intent', 'sentiment', 'priority']
            for field in required_fields:
                if field not in result:
                    result[field] = self._get_default_value(field)

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            return self._get_fallback_response()

    def _get_default_value(self, field: str) -> Any:
        """Get default value for missing field"""
        defaults = {
            'answer': "Let me help you with that.",
            'action': 'continue',
            'feature': None,
            'intent': 'general',
            'sentiment': 'neutral',
            'priority': 'normal',
            'customer_interests': []
        }
        return defaults.get(field)

    def _get_fallback_response(self) -> Dict[str, Any]:
        """Fallback response if Claude fails"""
        return {
            'answer': "That's a great question. Let me make sure I give you the most accurate information. Could you rephrase that, or would you like me to connect you with a specialist?",
            'action': 'continue',
            'feature': None,
            'intent': 'general',
            'sentiment': 'neutral',
            'priority': 'normal',
            'customer_interests': []
        }

    def _extract_available_features(self, demo_script: List[Dict[str, Any]]) -> List[str]:
        """Extract list of features that can be demonstrated"""
        features = []
        for step in demo_script:
            if step.get('name'):
                features.append(step['name'])
        return features

    async def classify_question_batch(self, questions: List[str]) -> List[Dict[str, Any]]:
        """Classify multiple questions for analytics"""
        classifications = []

        for question in questions:
            prompt = f"""Classify this customer question from a product demo:

QUESTION: "{question}"

Respond with JSON:
{{
    "intent": "clarification|feature_request|pricing|comparison|technical|objection|general",
    "sentiment": "positive|neutral|negative|confused",
    "priority": "low|normal|high|critical",
    "topics": ["list", "of", "topics"],
    "indicates_interest": true/false
}}"""

            try:
                response = self.anthropic.messages.create(
                    model=self.model,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )

                result = self._parse_response(response.content[0].text)
                result['question'] = question
                classifications.append(result)

            except Exception as e:
                logger.error(f"Error classifying question: {e}")
                classifications.append({
                    'question': question,
                    'intent': 'unknown',
                    'sentiment': 'neutral',
                    'priority': 'normal',
                    'topics': [],
                    'indicates_interest': False
                })

        return classifications


# Example usage
if __name__ == "__main__":
    import asyncio
    import os

    async def test_question_handler():
        anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        handler = QuestionHandler(anthropic)

        # Test questions
        test_questions = [
            "Can you show me the mobile app?",
            "How much does this cost compared to DocuSign?",
            "Wait, what was that audit trail feature?",
            "Does this integrate with Salesforce?",
            "This looks great! Can I try it today?"
        ]

        demo_context = {
            'demo_type': 'insign',
            'customer_context': {
                'name': 'Jayaprakash',
                'company': 'Number Labs',
                'industry': 'AI/Aviation'
            },
            'demo_script': [
                {'name': 'Login'},
                {'name': 'Dashboard'},
                {'name': 'Sign Document'},
                {'name': 'Send Document'},
                {'name': 'Audit Trail'},
                {'name': 'Mobile App'},
                {'name': 'API Integration'}
            ]
        }

        for question in test_questions:
            print(f"\n{'='*60}")
            print(f"Q: {question}")

            result = await handler.handle_question(
                question=question,
                demo_context=demo_context,
                current_step=3
            )

            print(f"A: {result['answer']}")
            print(f"Action: {result['action']}")
            if result.get('feature'):
                print(f"Jump to: {result['feature']}")
            print(f"Intent: {result['intent']} | Sentiment: {result['sentiment']} | Priority: {result['priority']}")

    asyncio.run(test_question_handler())
