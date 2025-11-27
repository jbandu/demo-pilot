from typing import List, Dict, Any
from pathlib import Path


class InSignDemoScript:
    """
    Complete demo script for InSign product demonstration.
    Defines all steps, narration, and browser actions.
    """

    def __init__(
        self,
        demo_url: str = "https://insign-pi.vercel.app",
        demo_email: str = "jbandu@gmail.com",
        demo_password: str = "Memphis123",
    ):
        self.demo_url = demo_url
        self.demo_email = demo_email
        self.demo_password = demo_password

        # Sample documents for demo
        self.sample_docs = {
            "nda": Path("./demo-environments/insign/test-data/NDA_Template.pdf"),
            "employment": Path(
                "./demo-environments/insign/test-data/Employment_Agreement.pdf"
            ),
        }

    def get_full_demo(self) -> List[Dict[str, Any]]:
        """Get complete 10-minute demo script"""
        return [
            self._step_1_greeting(),
            self._step_2_login(),
            self._step_3_dashboard(),
            self._step_4_view_pending_document(),
            self._step_5_sign_document(),
            self._step_6_upload_new_document(),
            self._step_7_add_signature_fields(),
            self._step_8_add_signers(),
            self._step_9_send_document(),
            self._step_10_audit_trail(),
            self._step_11_pricing_comparison(),
            self._step_12_closing(),
        ]

    def get_quick_demo(self) -> List[Dict[str, Any]]:
        """Get 5-minute quick demo (core features only)"""
        return [
            self._step_1_greeting(),
            self._step_2_login(),
            self._step_3_dashboard(),
            self._step_5_sign_document(),
            self._step_9_send_document(),
            self._step_12_closing(),
        ]

    def _step_1_greeting(self) -> Dict[str, Any]:
        return {
            "step_number": 1,
            "name": "Greeting",
            "duration_estimate_seconds": 15,
            "narration": """
                Hi! I'm Demo Copilot, your AI-powered product specialist from Number Labs.
                I'll give you a complete demonstration of InSign in about 10 minutes.

                You can interrupt me anytime to ask questions or dive deeper into any feature.
                Just click the question button or speak up if you're on voice.

                Ready to begin? Great! Let me show you how InSign works.
            """,
            "browser_actions": [{"type": "wait", "duration": 2}],
            "visual_highlights": [],
        }

    def _step_2_login(self) -> Dict[str, Any]:
        return {
            "step_number": 2,
            "name": "Login",
            "duration_estimate_seconds": 20,
            "narration": """
                Let me log into InSign as a typical user.
                I'll use our demo account to show you the platform.

                Notice the clean, modern interface. InSign focuses on simplicity
                while providing enterprise-grade security.
            """,
            "browser_actions": [
                {"type": "navigate", "url": f"{self.demo_url}/login"},
                {"type": "wait", "duration": 1},
                {"type": "highlight", "selector": "#email", "duration": 1000},
                {"type": "click", "selector": "#email"},
                {"type": "type", "selector": "#email", "text": self.demo_email},
                {"type": "wait", "duration": 0.5},
                {"type": "highlight", "selector": "#password", "duration": 1000},
                {"type": "click", "selector": "#password"},
                {"type": "type", "selector": "#password", "text": self.demo_password},
                {"type": "wait", "duration": 0.5},
                {
                    "type": "highlight",
                    "selector": "button[type='submit']",
                    "duration": 1000,
                },
                {"type": "click", "selector": "button[type='submit']"},
                {"type": "wait", "duration": 2},
            ],
            "visual_highlights": ["#email", "#password", "button[type='submit']"],
        }

    def _step_3_dashboard(self) -> Dict[str, Any]:
        return {
            "step_number": 3,
            "name": "Dashboard Overview",
            "duration_estimate_seconds": 30,
            "narration": """
                Here's the main dashboard. You'll see three key sections:

                First, documents pending YOUR signature - these are documents others
                have sent to you. Notice you have 4 documents waiting.

                Second, documents YOU'VE sent to others - you can track their status
                in real-time. See that 2 documents are pending signatures.

                And third, recently completed documents with full audit trails.

                Everything is organized intuitively so you can find what you need instantly.
            """,
            "browser_actions": [
                {"type": "wait", "duration": 1},
                {
                    "type": "highlight",
                    "selector": ".pending-your-signature",
                    "duration": 2000,
                },
                {"type": "wait", "duration": 1},
                {
                    "type": "highlight",
                    "selector": ".pending-others-signature",
                    "duration": 2000,
                },
                {"type": "wait", "duration": 1},
                {
                    "type": "highlight",
                    "selector": ".recently-completed",
                    "duration": 2000,
                },
                {"type": "wait", "duration": 1},
            ],
            "visual_highlights": [".dashboard-section"],
        }

    def _step_4_view_pending_document(self) -> Dict[str, Any]:
        return {
            "step_number": 4,
            "name": "View Pending Document",
            "duration_estimate_seconds": 20,
            "narration": """
                Let me show you how simple it is to sign a document.
                I'll click on this employment agreement that needs my signature.

                The document opens instantly with signature fields already highlighted
                in yellow. InSign automatically detected where signatures are needed
                when the document was uploaded.
            """,
            "browser_actions": [
                {"type": "click", "selector": ".document-item:first-child"},
                {"type": "wait", "duration": 2},
                {"type": "highlight", "selector": ".signature-field", "duration": 2000},
            ],
            "visual_highlights": [".signature-field"],
        }

    def _step_5_sign_document(self) -> Dict[str, Any]:
        return {
            "step_number": 5,
            "name": "Sign Document",
            "duration_estimate_seconds": 40,
            "narration": """
                Now I'll sign the document. I'll click on the signature field.

                InSign gives you three options: draw your signature with your mouse
                or touchscreen, type your name and we'll create a signature, or upload
                an image of your handwritten signature.

                I'll draw my signature here... and done!

                Notice the document is now marked as complete. All parties receive
                instant email notifications, and the document is automatically archived
                with a tamper-proof seal and full audit trail.

                That's it - signing takes literally seconds!
            """,
            "browser_actions": [
                {"type": "click", "selector": ".signature-field:first-child"},
                {"type": "wait", "duration": 1},
                {"type": "highlight", "selector": ".signature-modal", "duration": 2000},
                # Simulate drawing signature
                {"type": "click", "selector": ".draw-signature-tab"},
                {"type": "wait", "duration": 2},  # Drawing animation
                {"type": "click", "selector": ".apply-signature-button"},
                {"type": "wait", "duration": 1},
                {
                    "type": "highlight",
                    "selector": ".completion-message",
                    "duration": 2000,
                },
            ],
            "visual_highlights": [".signature-modal", ".completion-badge"],
        }

    def _step_6_upload_new_document(self) -> Dict[str, Any]:
        return {
            "step_number": 6,
            "name": "Upload New Document",
            "duration_estimate_seconds": 30,
            "narration": """
                Now let me show you the sender side - how you'd send a document
                for signature.

                I'll click 'Upload Document' in the main navigation.

                I'll upload this NDA template from my computer.

                InSign automatically detects this is a PDF and shows a preview.
                You can also upload Word documents, images, and other formats -
                InSign handles them all.
            """,
            "browser_actions": [
                {"type": "click", "selector": "a[href='/upload']"},
                {"type": "wait", "duration": 1},
                {
                    "type": "upload",
                    "selector": "input[type='file']",
                    "file_path": "./demo-environments/insign/test-data/NDA_Template.pdf",
                },
                {"type": "wait", "duration": 2},
                {
                    "type": "highlight",
                    "selector": ".document-preview",
                    "duration": 2000,
                },
            ],
            "visual_highlights": [".upload-area", ".document-preview"],
        }

    def _step_7_add_signature_fields(self) -> Dict[str, Any]:
        return {
            "step_number": 7,
            "name": "Add Signature Fields",
            "duration_estimate_seconds": 35,
            "narration": """
                Now I'll add signature fields. Watch how easy this is.

                I can drag and drop signature fields exactly where I need them on the document.
                See how it snaps into place? Very intuitive.

                I can also add date fields, text fields, checkboxes, and initials -
                whatever you need. Each field can be assigned to specific signers.

                Let me add one more signature field at the bottom of the page.
            """,
            "browser_actions": [
                {"type": "click", "selector": ".add-signature-field-button"},
                {"type": "wait", "duration": 1},
                # Simulate drag-and-drop
                {
                    "type": "highlight",
                    "selector": ".document-preview",
                    "duration": 1000,
                },
                {"type": "wait", "duration": 2},  # Dragging animation
                {"type": "scroll", "selector": ".page-2"},
                {"type": "wait", "duration": 1},
                {"type": "click", "selector": ".add-signature-field-button"},
                {"type": "wait", "duration": 2},
            ],
            "visual_highlights": [".signature-field-placed"],
        }

    def _step_8_add_signers(self) -> Dict[str, Any]:
        return {
            "step_number": 8,
            "name": "Add Signers",
            "duration_estimate_seconds": 45,
            "narration": """
                Now I'll add the signers. I can add multiple people and set a signing order.

                First, I'll add our legal team member - they must sign first.
                Email: legal@company.com

                Then I'll add the vendor contact - they'll sign second.
                Email: vendor@suppliercompany.com

                Notice I can also set a deadline for signatures, add a custom message,
                and require additional authentication like SMS verification if needed.

                InSign also supports advanced features like carbon copies, access codes,
                and even in-person signing.

                For this demo, I'll keep it simple and just click Send.
            """,
            "browser_actions": [
                {"type": "click", "selector": ".add-signer-button"},
                {"type": "wait", "duration": 0.5},
                {
                    "type": "type",
                    "selector": "input[name='signer-email-1']",
                    "text": "legal@company.com",
                },
                {
                    "type": "type",
                    "selector": "input[name='signer-name-1']",
                    "text": "Legal Team",
                },
                {"type": "wait", "duration": 1},
                {"type": "click", "selector": ".add-signer-button"},
                {"type": "wait", "duration": 0.5},
                {
                    "type": "type",
                    "selector": "input[name='signer-email-2']",
                    "text": "vendor@suppliercompany.com",
                },
                {
                    "type": "type",
                    "selector": "input[name='signer-name-2']",
                    "text": "Vendor Contact",
                },
                {"type": "wait", "duration": 1},
                {
                    "type": "highlight",
                    "selector": ".signing-order-options",
                    "duration": 2000,
                },
                {
                    "type": "highlight",
                    "selector": ".advanced-options",
                    "duration": 2000,
                },
            ],
            "visual_highlights": [".signer-list", ".signing-order"],
        }

    def _step_9_send_document(self) -> Dict[str, Any]:
        return {
            "step_number": 9,
            "name": "Send Document",
            "duration_estimate_seconds": 20,
            "narration": """
                And... sent! The document is on its way to the signers.

                They'll receive professional emails with a secure link to sign.
                You can track opens, views, and signatures in real-time from your dashboard.

                InSign also sends automatic reminders to signers who haven't completed
                their signatures - no more manual follow-ups!
            """,
            "browser_actions": [
                {"type": "highlight", "selector": ".send-button", "duration": 1000},
                {"type": "click", "selector": ".send-button"},
                {"type": "wait", "duration": 2},
                {"type": "highlight", "selector": ".success-message", "duration": 2000},
            ],
            "visual_highlights": [".success-message"],
        }

    def _step_10_audit_trail(self) -> Dict[str, Any]:
        return {
            "step_number": 10,
            "name": "Audit Trail",
            "duration_estimate_seconds": 35,
            "narration": """
                Now let me show you something that DocuSign charges EXTRA for -
                the audit trail.

                InSign includes complete audit trails for every document at no additional cost.

                Look at this - every action is logged with timestamps, IP addresses,
                and device information: when the document was sent, when each person
                opened it, how long they viewed it, when they signed, and even if they
                declined or requested changes.

                This is critical for compliance and legal requirements. InSign's audit
                trails are court-admissible and meet all major regulatory standards.

                DocuSign charges $20 per user per month for this feature.
                With InSign, it's included free.
            """,
            "browser_actions": [
                {"type": "click", "selector": ".view-audit-trail-link"},
                {"type": "wait", "duration": 2},
                {"type": "scroll", "selector": ".audit-event:first-child"},
                {
                    "type": "highlight",
                    "selector": ".audit-event:nth-child(1)",
                    "duration": 1500,
                },
                {
                    "type": "highlight",
                    "selector": ".audit-event:nth-child(2)",
                    "duration": 1500,
                },
                {
                    "type": "highlight",
                    "selector": ".audit-event:nth-child(3)",
                    "duration": 1500,
                },
                {
                    "type": "highlight",
                    "selector": ".timestamp-and-ip",
                    "duration": 2000,
                },
            ],
            "visual_highlights": [".audit-trail-panel"],
        }

    def _step_11_pricing_comparison(self) -> Dict[str, Any]:
        return {
            "step_number": 11,
            "name": "Pricing Comparison",
            "duration_estimate_seconds": 30,
            "narration": """
                Before we wrap up, let me show you InSign's pricing advantage.

                DocuSign charges $45 per user per month for their business plan,
                with additional fees for audit trails, advanced authentication,
                and bulk sending.

                InSign offers unlimited users, unlimited documents, and all advanced
                features for one flat enterprise price - typically 50 to 70 percent
                less than DocuSign.

                Plus, we include features like custom branding, API access, and
                dedicated support that DocuSign charges extra for.

                You're essentially getting enterprise features at small business prices.
            """,
            "browser_actions": [
                {"type": "navigate", "url": f"{self.demo_url}/pricing"},
                {"type": "wait", "duration": 2},
                {
                    "type": "highlight",
                    "selector": ".pricing-comparison-table",
                    "duration": 3000,
                },
                {"type": "scroll", "selector": ".feature-comparison"},
            ],
            "visual_highlights": [".cost-savings-highlight"],
        }

    def _step_12_closing(self) -> Dict[str, Any]:
        return {
            "step_number": 12,
            "name": "Closing & Next Steps",
            "duration_estimate_seconds": 25,
            "narration": """
                And that's InSign! In just 10 minutes, you've seen how easy it is to:
                sign documents, send documents for signature, add multiple signers,
                and access complete audit trails - all at a fraction of DocuSign's cost.

                Would you like to dive deeper into any specific feature? I can show you:
                templates and bulk sending, API integration for developers,
                mobile app features, or custom branding options.

                Or if you're ready, I can connect you with a sales specialist to discuss
                your specific needs and pricing.

                Just let me know how I can help!
            """,
            "browser_actions": [
                {"type": "navigate", "url": f"{self.demo_url}/dashboard"},
                {"type": "wait", "duration": 2},
            ],
            "visual_highlights": [],
        }

    def get_custom_demo(self, features: List[str]) -> List[Dict[str, Any]]:
        """
        Generate custom demo based on customer interests.

        Args:
            features: List of features to focus on
                     (e.g., ['api', 'templates', 'mobile', 'branding'])
        """
        base_steps = [
            self._step_1_greeting(),
            self._step_2_login(),
            self._step_3_dashboard(),
        ]

        feature_steps = {
            "signing": [
                self._step_4_view_pending_document(),
                self._step_5_sign_document(),
            ],
            "sending": [
                self._step_6_upload_new_document(),
                self._step_7_add_signature_fields(),
                self._step_8_add_signers(),
                self._step_9_send_document(),
            ],
            "audit": [self._step_10_audit_trail()],
            "pricing": [self._step_11_pricing_comparison()],
        }

        custom_steps = base_steps.copy()
        for feature in features:
            if feature in feature_steps:
                custom_steps.extend(feature_steps[feature])

        custom_steps.append(self._step_12_closing())

        return custom_steps


# Example usage
if __name__ == "__main__":
    script = InSignDemoScript()

    # Get full demo
    full_demo = script.get_full_demo()
    print(f"Full demo has {len(full_demo)} steps")
    print(
        f"Estimated duration: {sum(s['duration_estimate_seconds'] for s in full_demo)} seconds"
    )

    # Print first step
    print("\nStep 1:")
    print(f"Name: {full_demo[0]['name']}")
    print(f"Narration: {full_demo[0]['narration'][:100]}...")
