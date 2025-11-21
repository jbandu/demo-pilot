"""
Question Handler - AI-powered customer question answering
Uses Claude to answer customer questions during demos
"""
import asyncio
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)


class QuestionHandler:
    """
    Handles customer questions during demos using Claude
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929"
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError("Anthropic API key required")

        self.client = AsyncAnthropic(api_key=self.api_key)
        self.model = model

        # Context management
        self.product_context: Dict[str, Any] = {}
        self.demo_context: Dict[str, Any] = {}
        self.conversation_history: List[Dict[str, str]] = []

    def set_product_context(self, context: Dict[str, Any]):
        """
        Set product-specific context for answering questions

        Args:
            context: Dict with product info, features, pricing, etc.
        """
        self.product_context = context
        logger.info(f"Product context set: {context.get('name', 'Unknown')}")

    def set_demo_context(self, context: Dict[str, Any]):
        """
        Set current demo context (what's happening now)

        Args:
            context: Current demo state, step, etc.
        """
        self.demo_context = context

    async def answer_question(
        self,
        question: str,
        include_demo_context: bool = True
    ) -> Dict[str, Any]:
        """
        Answer a customer question using Claude

        Args:
            question: Customer's question
            include_demo_context: Whether to include current demo state

        Returns:
            Dict with answer, confidence, and metadata
        """
        logger.info(f"Answering question: {question}")

        start_time = datetime.now()

        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(include_demo_context)

            # Build conversation messages
            messages = self.conversation_history + [
                {"role": "user", "content": question}
            ]

            # Call Claude
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=messages
            )

            answer = response.content[0].text

            # Track conversation
            self.conversation_history.append({"role": "user", "content": question})
            self.conversation_history.append({"role": "assistant", "content": answer})

            # Keep conversation history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            response_time = (datetime.now() - start_time).total_seconds() * 1000

            logger.info(f"Question answered in {response_time:.0f}ms")

            return {
                "question": question,
                "answer": answer,
                "response_time_ms": int(response_time),
                "confidence": 0.9,  # Could analyze response to determine confidence
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            raise

    def _build_system_prompt(self, include_demo_context: bool) -> str:
        """Build system prompt with product and demo context"""

        product_name = self.product_context.get("name", "our product")
        product_description = self.product_context.get("description", "")

        prompt = f"""You are an expert sales engineer conducting a live product demonstration for {product_name}.

Product Overview:
{product_description}

Key Features:
"""

        # Add features
        if "features" in self.product_context:
            for feature in self.product_context["features"]:
                prompt += f"- {feature}\n"

        # Add pricing if available
        if "pricing" in self.product_context:
            prompt += f"\nPricing: {self.product_context['pricing']}\n"

        # Add demo context if requested
        if include_demo_context and self.demo_context:
            prompt += f"""
Current Demo Context:
- Current Step: {self.demo_context.get('current_step', 'Unknown')}
- Progress: {self.demo_context.get('progress', '0')}%
- What we just showed: {self.demo_context.get('last_action', 'N/A')}
"""

        prompt += """
Your role:
1. Answer questions clearly and concisely (2-3 sentences)
2. Reference what we've shown in the demo when relevant
3. Be enthusiastic but professional
4. If you don't know something, be honest and offer to follow up
5. Always relate answers back to customer benefits
6. Keep answers conversational and natural for text-to-speech

Guidelines:
- Avoid technical jargon unless the customer uses it first
- Focus on business value, not just features
- Use specific examples from the demo when possible
- Be concise - this will be spoken aloud
"""

        return prompt

    async def suggest_follow_up_questions(self) -> List[str]:
        """
        Suggest relevant follow-up questions based on current context

        Returns:
            List of suggested questions
        """
        try:
            prompt = f"""Based on the current demo context and conversation, suggest 3 relevant questions a customer might ask about {self.product_context.get('name', 'the product')}.

Current Context:
- Step: {self.demo_context.get('current_step', 'Unknown')}
- Recent conversation: {len(self.conversation_history)} exchanges

Return only the questions, one per line, without numbering."""

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}]
            )

            questions_text = response.content[0].text
            questions = [q.strip() for q in questions_text.split("\n") if q.strip()]

            return questions[:3]

        except Exception as e:
            logger.error(f"Failed to suggest questions: {e}")
            return []

    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")

    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation"""
        if not self.conversation_history:
            return "No questions asked yet."

        questions = [
            msg["content"]
            for msg in self.conversation_history
            if msg["role"] == "user"
        ]

        return f"Customer asked {len(questions)} questions: " + "; ".join(questions[:3])


# InSign-specific product context
INSIGN_PRODUCT_CONTEXT = {
    "name": "InSign",
    "description": "InSign is a modern electronic signature platform that simplifies document signing and management. It's a powerful alternative to DocuSign with better pricing and user experience.",
    "features": [
        "Unlimited document signing",
        "Template library with smart field detection",
        "Bulk send capabilities",
        "Real-time notifications and reminders",
        "Comprehensive audit trails for compliance",
        "Mobile apps for iOS and Android",
        "Integrations with Salesforce, Google Drive, Dropbox, and more",
        "Advanced authentication options (SSO, 2FA)",
        "Custom branding and white-labeling",
        "API access for custom integrations"
    ],
    "pricing": "Starting at $10/user/month for Pro plan, with Enterprise options available",
    "key_differentiators": [
        "50% more affordable than DocuSign",
        "More intuitive user interface",
        "Better mobile experience",
        "Faster document preparation with AI-powered field detection"
    ],
    "ideal_customers": [
        "SMBs needing 5-100 users",
        "Sales teams sending contracts",
        "HR departments for onboarding",
        "Real estate agencies",
        "Legal firms",
        "Financial services"
    ],
    "security": "SOC 2 Type II certified, GDPR compliant, bank-level encryption"
}


# Example usage
async def demo_example():
    """Example of question handler usage"""
    handler = QuestionHandler()

    # Set context
    handler.set_product_context(INSIGN_PRODUCT_CONTEXT)
    handler.set_demo_context({
        "current_step": "Dashboard Overview",
        "progress": 40,
        "last_action": "Showed pending documents and activity feed"
    })

    # Answer questions
    result = await handler.answer_question(
        "How does InSign compare to DocuSign in terms of pricing?"
    )

    print(f"Q: {result['question']}")
    print(f"A: {result['answer']}")
    print(f"Response time: {result['response_time_ms']}ms")

    # Suggest follow-ups
    suggestions = await handler.suggest_follow_up_questions()
    print(f"\nSuggested questions: {suggestions}")


if __name__ == "__main__":
    asyncio.run(demo_example())
