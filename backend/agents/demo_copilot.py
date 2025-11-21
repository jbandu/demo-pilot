import asyncio
import logging
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from anthropic import Anthropic
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor

from .browser_controller import BrowserController
from .voice_engine import VoiceEngine, AudioSynchronizer
from .question_handler import QuestionHandler
from .demo_scripts.insign_demo import InSignDemoScript

logger = logging.getLogger(__name__)


class DemoCopilotState(dict):
    """State for Demo Copilot agent"""
    session_id: str
    demo_type: str
    current_step: int
    status: str  # 'initialized', 'running', 'paused', 'completed', 'error'
    customer_context: Dict[str, Any]
    demo_script: List[Dict[str, Any]]
    messages: List[Dict[str, str]]
    errors: List[str]
    metadata: Dict[str, Any]


class DemoCopilot:
    """
    Main orchestrator for autonomous product demonstrations.

    This agent:
    1. Controls browser to navigate product
    2. Narrates actions with natural voice
    3. Responds to customer questions
    4. Adapts demo based on customer interests
    5. Tracks engagement and analytics
    """

    def __init__(self, database_session=None):
        self.session_id = str(uuid.uuid4())
        self.anthropic = Anthropic()

        # Components
        self.browser = BrowserController(headless=False, slow_mo=500)
        self.voice = VoiceEngine()
        self.synchronizer = AudioSynchronizer(self.voice)
        self.question_handler = QuestionHandler(self.anthropic)

        # Demo scripts
        self.scripts = {
            'insign': InSignDemoScript(
                demo_url=os.getenv('INSIGN_DEMO_URL', 'https://demo.insign.io'),
                demo_email=os.getenv('INSIGN_DEMO_EMAIL', 'demo@numberlabs.ai'),
                demo_password=os.getenv('INSIGN_DEMO_PASSWORD', 'DemoPass123!')
            ),
            # Future: 'crew_intelligence': CrewIntelligenceDemoScript(),
        }

        # State
        self.state: Optional[DemoCopilotState] = None
        self.db = database_session

        # Build LangGraph workflow
        self.graph = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for demo execution"""

        workflow = StateGraph(DemoCopilotState)

        # Define nodes
        workflow.add_node("initialize", self._initialize_demo)
        workflow.add_node("execute_step", self._execute_step)
        workflow.add_node("check_questions", self._check_for_questions)
        workflow.add_node("handle_question", self._handle_question)
        workflow.add_node("next_step", self._advance_to_next_step)
        workflow.add_node("complete", self._complete_demo)
        workflow.add_node("error_handler", self._handle_error)

        # Define edges
        workflow.set_entry_point("initialize")

        workflow.add_edge("initialize", "execute_step")
        workflow.add_edge("execute_step", "check_questions")

        workflow.add_conditional_edges(
            "check_questions",
            self._should_handle_question,
            {
                "handle_question": "handle_question",
                "next_step": "next_step"
            }
        )

        workflow.add_edge("handle_question", "check_questions")

        workflow.add_conditional_edges(
            "next_step",
            self._should_continue,
            {
                "execute_step": "execute_step",
                "complete": "complete",
                "error": "error_handler"
            }
        )

        workflow.add_edge("complete", END)
        workflow.add_edge("error_handler", END)

        return workflow.compile()

    async def start_demo(
        self,
        demo_type: str,
        customer_context: Optional[Dict[str, Any]] = None,
        custom_script: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Start a new demo session.

        Args:
            demo_type: Type of demo ('insign', 'crew_intelligence', etc.)
            customer_context: Customer info for personalization
            custom_script: Optional custom demo script

        Returns:
            Session ID
        """
        logger.info(f"Starting {demo_type} demo, session: {self.session_id}")

        # Get demo script
        if custom_script:
            demo_script = custom_script
        else:
            demo_script = self.scripts[demo_type].get_full_demo()

        # Initialize state
        self.state = DemoCopilotState(
            session_id=self.session_id,
            demo_type=demo_type,
            current_step=0,
            status='initialized',
            customer_context=customer_context or {},
            demo_script=demo_script,
            messages=[],
            errors=[],
            metadata={
                'started_at': datetime.utcnow().isoformat(),
                'total_steps': len(demo_script)
            }
        )

        # Initialize browser
        await self.browser.start()

        # Save to database
        if self.db:
            await self._save_session_to_db()

        # Start workflow
        asyncio.create_task(self._run_workflow())

        return self.session_id

    async def _run_workflow(self):
        """Execute the demo workflow"""
        try:
            self.state['status'] = 'running'
            result = await self.graph.ainvoke(self.state)
            logger.info(f"Demo completed: {result['status']}")

        except Exception as e:
            logger.error(f"Demo error: {e}", exc_info=True)
            self.state['status'] = 'error'
            self.state['errors'].append(str(e))

        finally:
            await self.cleanup()

    async def _initialize_demo(self, state: DemoCopilotState) -> DemoCopilotState:
        """Initialize demo - node 1"""
        logger.info("Initializing demo...")

        # Personalize greeting if we have customer context
        if state['customer_context'].get('name'):
            greeting = f"Hi {state['customer_context']['name']}! "
        else:
            greeting = "Hi! "

        greeting += "I'm Demo Copilot, your AI-powered sales engineer from Number Labs."

        # Generate and play greeting
        await self.voice.text_to_speech(greeting)

        state['metadata']['initialized_at'] = datetime.utcnow().isoformat()
        return state

    async def _execute_step(self, state: DemoCopilotState) -> DemoCopilotState:
        """Execute current demo step - node 2"""
        current_step = state['current_step']
        step_data = state['demo_script'][current_step]

        logger.info(f"Executing step {current_step + 1}/{len(state['demo_script'])}: {step_data['name']}")

        try:
            # Synchronize narration with browser actions
            narration = step_data['narration'].strip()
            actions = step_data['browser_actions']

            audio_result = await self.synchronizer.sync_narrate_and_act(
                narration=narration,
                browser_actions=actions,
                browser_controller=self.browser
            )

            # Record action in database
            if self.db:
                await self._save_action_to_db(step_data, audio_result)

            state['messages'].append({
                'role': 'assistant',
                'content': narration,
                'step': current_step,
                'timestamp': datetime.utcnow().isoformat()
            })

        except Exception as e:
            logger.error(f"Error executing step: {e}", exc_info=True)
            state['errors'].append(f"Step {current_step}: {str(e)}")

        return state

    async def _check_for_questions(self, state: DemoCopilotState) -> DemoCopilotState:
        """Check if customer has asked a question - node 3"""
        # In real implementation, this would check:
        # - WebSocket messages
        # - Voice input
        # - Button clicks

        # For now, simulate no questions
        state['metadata']['has_pending_question'] = False
        return state

    def _should_handle_question(self, state: DemoCopilotState) -> str:
        """Routing function"""
        if state['metadata'].get('has_pending_question'):
            return "handle_question"
        return "next_step"

    async def _handle_question(self, state: DemoCopilotState) -> DemoCopilotState:
        """Handle customer question - node 4"""
        question = state['metadata'].get('pending_question', '')
        logger.info(f"Handling question: {question}")

        # Use Claude to understand question and generate response
        response = await self.question_handler.handle_question(
            question=question,
            demo_context=state,
            current_step=state['current_step']
        )

        # Narrate response
        await self.voice.text_to_speech(response['answer'])

        # Take action based on response
        if response.get('action') == 'jump_to_feature':
            # Find and jump to relevant step
            feature = response.get('feature')
            new_step = self._find_step_for_feature(feature, state)
            if new_step:
                state['current_step'] = new_step

        state['messages'].append({
            'role': 'user',
            'content': question,
            'timestamp': datetime.utcnow().isoformat()
        })
        state['messages'].append({
            'role': 'assistant',
            'content': response['answer'],
            'timestamp': datetime.utcnow().isoformat()
        })

        # Clear question
        state['metadata']['has_pending_question'] = False
        state['metadata'].pop('pending_question', None)

        return state

    async def _advance_to_next_step(self, state: DemoCopilotState) -> DemoCopilotState:
        """Move to next step - node 5"""
        state['current_step'] += 1
        logger.info(f"Advancing to step {state['current_step'] + 1}")
        return state

    def _should_continue(self, state: DemoCopilotState) -> str:
        """Routing function - continue or complete?"""
        if state['errors']:
            return "error"
        if state['current_step'] >= len(state['demo_script']):
            return "complete"
        return "execute_step"

    async def _complete_demo(self, state: DemoCopilotState) -> DemoCopilotState:
        """Complete demo - node 6"""
        logger.info("Demo completed successfully")
        state['status'] = 'completed'
        state['metadata']['completed_at'] = datetime.utcnow().isoformat()

        # Calculate duration
        started = datetime.fromisoformat(state['metadata']['started_at'])
        completed = datetime.fromisoformat(state['metadata']['completed_at'])
        duration = (completed - started).total_seconds()
        state['metadata']['duration_seconds'] = duration

        # Update database
        if self.db:
            await self._update_session_in_db(state)

        return state

    async def _handle_error(self, state: DemoCopilotState) -> DemoCopilotState:
        """Handle errors - node 7"""
        logger.error(f"Demo error handler triggered: {state['errors']}")
        state['status'] = 'error'
        return state

    def _find_step_for_feature(self, feature: str, state: DemoCopilotState) -> Optional[int]:
        """Find step index that demonstrates a specific feature"""
        for i, step in enumerate(state['demo_script']):
            if feature.lower() in step['name'].lower():
                return i
        return None

    async def pause_demo(self):
        """Pause the demo"""
        if self.state:
            self.state['status'] = 'paused'
            logger.info("Demo paused")

    async def resume_demo(self):
        """Resume paused demo"""
        if self.state and self.state['status'] == 'paused':
            self.state['status'] = 'running'
            logger.info("Demo resumed")

    async def ask_question(self, question: str):
        """Inject a customer question"""
        if self.state:
            self.state['metadata']['has_pending_question'] = True
            self.state['metadata']['pending_question'] = question

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up demo resources...")
        await self.browser.stop()
        self.voice.clear_cache()

    async def _save_session_to_db(self):
        """Save session to database"""
        # Implementation depends on your database layer
        pass

    async def _save_action_to_db(self, step_data, audio_result):
        """Save action to database"""
        # Implementation depends on your database layer
        pass

    async def _update_session_in_db(self, state):
        """Update session in database"""
        # Implementation depends on your database layer
        pass


# Example usage
if __name__ == "__main__":
    async def test_demo_copilot():
        copilot = DemoCopilot()

        # Start InSign demo
        session_id = await copilot.start_demo(
            demo_type='insign',
            customer_context={
                'name': 'Jayaprakash',
                'company': 'Number Labs',
                'interests': ['audit_trail', 'pricing']
            }
        )

        print(f"Demo started: {session_id}")

        # Let it run for a bit
        await asyncio.sleep(60)

        # Ask a question
        await copilot.ask_question("Can you show me the mobile experience?")

        # Wait for completion
        while copilot.state and copilot.state['status'] == 'running':
            await asyncio.sleep(5)

        print(f"Demo completed with status: {copilot.state['status']}")

    asyncio.run(test_demo_copilot())
