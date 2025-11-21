"""
InSign Demo Script
Complete demonstration flow for InSign (DocuSign alternative)

Demo Flow:
1. Login to InSign
2. Dashboard Overview
3. Sign a Document
4. Send Document for Signature
5. Audit Trail Review
"""
import asyncio
import os
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class InSignDemoScript:
    """
    InSign product demonstration script
    Defines all steps, narration, and interactions
    """

    def __init__(self, browser_controller, voice_engine):
        self.browser = browser_controller
        self.voice = voice_engine

        # Demo configuration from environment
        self.demo_url = os.getenv("INSIGN_DEMO_URL", "https://demo.insign.io")
        self.demo_email = os.getenv("INSIGN_DEMO_EMAIL", "demo@numberlabs.ai")
        self.demo_password = os.getenv("INSIGN_DEMO_PASSWORD", "")

        # Demo progress tracking
        self.current_step = 0
        self.total_steps = 5

        # Define demo sections
        self.sections = [
            "login",
            "dashboard_overview",
            "sign_document",
            "send_document",
            "audit_trail"
        ]

    async def run_full_demo(self, customer_name: Optional[str] = None):
        """
        Execute complete InSign demonstration

        Args:
            customer_name: Optional customer name for personalization
        """
        logger.info("Starting InSign demo...")

        try:
            # Opening
            await self._opening_greeting(customer_name)

            # Step 1: Login
            await self._step_login()

            # Step 2: Dashboard Overview
            await self._step_dashboard_overview()

            # Step 3: Sign a Document
            await self._step_sign_document()

            # Step 4: Send Document for Signature
            await self._step_send_document()

            # Step 5: Audit Trail
            await self._step_audit_trail()

            # Closing
            await self._closing_remarks()

            logger.info("InSign demo completed successfully")

        except Exception as e:
            logger.error(f"Demo failed: {e}")
            raise

    async def _opening_greeting(self, customer_name: Optional[str] = None):
        """Opening greeting and introduction"""
        logger.info("Step: Opening greeting")

        greeting = (
            f"Hello{' ' + customer_name if customer_name else ''}! "
            "Welcome to this live demonstration of InSign, "
            "our modern electronic signature platform. "
            "Over the next 10 minutes, I'll walk you through how InSign "
            "simplifies document signing and management for your team. "
            "Let's get started!"
        )

        await self.voice.speak(greeting, stream=False)
        await asyncio.sleep(1)

    async def _step_login(self):
        """Step 1: Login to InSign"""
        self.current_step = 1
        logger.info(f"Step {self.current_step}/{self.total_steps}: Login")

        # Narrate
        await self.voice.speak(
            "First, I'll log into our InSign demo account. "
            "InSign supports multiple authentication methods including "
            "single sign-on, two-factor authentication, and social logins.",
            stream=False
        )

        # Navigate to login page
        await self.browser.navigate(self.demo_url)
        await self.browser.wait(2)

        # Fill in credentials
        await self.voice.speak("I'm entering the login credentials now.", stream=False)

        await self.browser.type_text("#email", self.demo_email)
        await self.browser.type_text("#password", self.demo_password)

        await self.voice.speak("And clicking sign in.", stream=False)
        await self.browser.click("#login-button", "Login button")

        # Wait for dashboard
        await self.browser.wait_for_navigation()
        await self.browser.wait(2)

        await self.voice.speak(
            "Great! We're now logged in and ready to explore the platform.",
            stream=False
        )

    async def _step_dashboard_overview(self):
        """Step 2: Dashboard Overview"""
        self.current_step = 2
        logger.info(f"Step {self.current_step}/{self.total_steps}: Dashboard Overview")

        await self.voice.speak(
            "Here we are on the InSign dashboard. "
            "This is your central hub for managing all document activities.",
            stream=False
        )

        await self.browser.wait(2)

        # Highlight key areas
        await self.voice.speak(
            "On the left sidebar, you can access your documents, templates, "
            "contacts, and settings. The main area shows your recent activity "
            "and pending actions.",
            stream=False
        )

        await self.browser.scroll("down", 300)
        await self.browser.wait(2)

        await self.voice.speak(
            "You can see at a glance which documents are waiting for signatures, "
            "which have been completed, and any that require your attention.",
            stream=False
        )

        await self.browser.wait(1)

    async def _step_sign_document(self):
        """Step 3: Sign a Document"""
        self.current_step = 3
        logger.info(f"Step {self.current_step}/{self.total_steps}: Sign Document")

        await self.voice.speak(
            "Now, let me show you how easy it is to sign a document. "
            "I'll click on this pending document that requires my signature.",
            stream=False
        )

        # Click on a pending document
        await self.browser.click(".document-item:first-child", "First pending document")
        await self.browser.wait(2)

        await self.voice.speak(
            "The document opens in our intuitive signing interface. "
            "InSign automatically highlights where you need to sign, "
            "initial, or fill in information.",
            stream=False
        )

        await self.browser.wait(2)

        # Navigate to signature field
        await self.voice.speak(
            "I can see the signature field is highlighted here. "
            "Let me click on it to add my signature.",
            stream=False
        )

        await self.browser.click(".signature-field", "Signature field")
        await self.browser.wait(1)

        await self.voice.speak(
            "InSign offers multiple signature options: you can draw your signature, "
            "type it, upload an image, or use a pre-saved signature. "
            "I'll use a pre-saved signature for speed.",
            stream=False
        )

        await self.browser.click("#use-saved-signature", "Use saved signature")
        await self.browser.wait(1)

        await self.voice.speak(
            "And now I'll click continue to finalize the signature.",
            stream=False
        )

        await self.browser.click("#continue-button", "Continue button")
        await self.browser.wait(2)

        await self.voice.speak(
            "Perfect! The document is now signed. InSign automatically generates "
            "a certificate of completion with timestamp and audit trail. "
            "All parties receive a fully executed copy via email.",
            stream=False
        )

    async def _step_send_document(self):
        """Step 4: Send Document for Signature"""
        self.current_step = 4
        logger.info(f"Step {self.current_step}/{self.total_steps}: Send Document")

        await self.voice.speak(
            "Next, let me demonstrate how to send a document for others to sign. "
            "I'll click on the 'New Document' button.",
            stream=False
        )

        await self.browser.click("#new-document-button", "New document button")
        await self.browser.wait(2)

        await self.voice.speak(
            "I can either upload a new document or choose from our template library. "
            "For this demo, I'll select an NDA template.",
            stream=False
        )

        await self.browser.click("#templates-tab", "Templates tab")
        await self.browser.wait(1)

        await self.browser.click(".template-item:first-child", "NDA template")
        await self.browser.wait(2)

        await self.voice.speak(
            "Now I'll add the recipient who needs to sign this document. "
            "I'll enter their email address and assign them the role of 'Signer'.",
            stream=False
        )

        await self.browser.type_text("#recipient-email", "client@example.com")
        await self.browser.click("#add-recipient", "Add recipient")
        await self.browser.wait(1)

        await self.voice.speak(
            "InSign's smart field detection automatically identifies where "
            "signatures and other information are needed. I can also drag and drop "
            "fields manually if needed.",
            stream=False
        )

        await self.browser.wait(2)

        await self.voice.speak(
            "I'll add a personal message to the recipient, "
            "and then send the document.",
            stream=False
        )

        await self.browser.type_text(
            "#message",
            "Please review and sign this NDA at your earliest convenience."
        )
        await self.browser.wait(1)

        await self.browser.click("#send-button", "Send button")
        await self.browser.wait(2)

        await self.voice.speak(
            "Done! The recipient will receive an email notification with a secure link "
            "to review and sign the document. They don't need an InSign account to sign.",
            stream=False
        )

    async def _step_audit_trail(self):
        """Step 5: Audit Trail Review"""
        self.current_step = 5
        logger.info(f"Step {self.current_step}/{self.total_steps}: Audit Trail")

        await self.voice.speak(
            "Finally, let me show you InSign's comprehensive audit trail. "
            "This is critical for compliance and legal requirements.",
            stream=False
        )

        # Navigate back to a completed document
        await self.browser.click("#documents-nav", "Documents navigation")
        await self.browser.wait(1)

        await self.browser.click("#completed-filter", "Completed filter")
        await self.browser.wait(1)

        await self.browser.click(".document-item:first-child", "First completed document")
        await self.browser.wait(2)

        await self.voice.speak(
            "I'll open the audit trail for this completed document.",
            stream=False
        )

        await self.browser.click("#audit-trail-button", "Audit trail button")
        await self.browser.wait(2)

        await self.voice.speak(
            "As you can see, InSign tracks every action taken on the document: "
            "when it was sent, when it was opened, when each page was viewed, "
            "when signatures were added, and when it was completed. "
            "Each action is timestamped and includes IP address information.",
            stream=False
        )

        await self.browser.scroll("down", 300)
        await self.browser.wait(2)

        await self.voice.speak(
            "This level of detail ensures legal enforceability and meets "
            "compliance requirements for industries like finance, healthcare, and legal services.",
            stream=False
        )

    async def _closing_remarks(self):
        """Closing remarks"""
        logger.info("Step: Closing remarks")

        await self.voice.speak(
            "That completes our demonstration of InSign. "
            "As you've seen, InSign makes it incredibly simple to send, sign, "
            "and manage documents securely. "
            "With features like templates, bulk send, mobile apps, and integrations "
            "with tools like Salesforce and Google Drive, "
            "InSign can transform how your team handles document workflows.",
            stream=False
        )

        await asyncio.sleep(1)

        await self.voice.speak(
            "Thank you for your time today! "
            "Do you have any questions about what we covered, "
            "or would you like me to dive deeper into any specific feature?",
            stream=False
        )

    def get_current_progress(self) -> Dict[str, Any]:
        """Get current demo progress"""
        return {
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "progress_percentage": (self.current_step / self.total_steps) * 100,
            "current_section": self.sections[self.current_step - 1] if self.current_step > 0 else "intro"
        }

    async def skip_to_section(self, section_name: str):
        """Skip to a specific section"""
        if section_name in self.sections:
            section_index = self.sections.index(section_name)
            self.current_step = section_index

            await self.voice.speak(
                f"Skipping to the {section_name.replace('_', ' ')} section.",
                stream=False
            )

            # Execute the section
            section_method = getattr(self, f"_step_{section_name}", None)
            if section_method:
                await section_method()
        else:
            logger.warning(f"Section not found: {section_name}")


# Example usage
async def demo_example():
    """Example of running the InSign demo"""
    from ..browser_controller import BrowserController
    from ..voice_engine import VoiceEngine

    browser = BrowserController(headless=False)
    voice = VoiceEngine(voice_id="Rachel")

    demo = InSignDemoScript(browser, voice)

    try:
        await browser.start()
        await demo.run_full_demo(customer_name="Sarah")
    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(demo_example())
