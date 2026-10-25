"""Chat service orchestrating conversation flow, title generation, and message persistence."""

import re
from datetime import datetime
from typing import Dict, Any, Optional
from app.extensions import db
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.preference import UserPreference
from app.services.ai_provider import (
    get_ai_provider,
    AIProviderError,
    AIConfigurationError,
    AIServiceUnavailableError
)

VALID_CATEGORIES = {'All', 'Study', 'Coding', 'Career', 'General'}


class ChatService:
    """Service handling conversation management and AI message dispatch."""

    @staticmethod
    def generate_title(text: str) -> str:
        """Derive an intelligent, concise conversation title from initial prompt."""
        cleaned = re.sub(r'[\r\n\t]+', ' ', text).strip()
        cleaned = re.sub(r'[#*`_~>\-+=?]', '', cleaned).strip()

        # Remove common chat starter prefixes iteratively
        prefix_pattern = r'^(can you|could you|please|tell me about|explain|what is|what are|how do i|how does|how to|how the|how|why is|why does|write a|help me with|give me)\s+'
        for _ in range(3):
            match = re.search(prefix_pattern, cleaned, flags=re.IGNORECASE)
            if match:
                cleaned = cleaned[match.end():].strip()
            else:
                break

        if not cleaned:
            return "New Exploration"

        # Truncate to reasonable word count and length
        words = cleaned.split()
        title_candidate = " ".join(words[:6])
        if len(title_candidate) > 40:
            title_candidate = title_candidate[:37] + "..."

        # Capitalize first letter
        return title_candidate[0].upper() + title_candidate[1:]

    @classmethod
    def get_system_prompt(cls, category: str = 'General') -> str:
        """Construct context-aware system instructions for academic and dev success."""
        tone_pref = UserPreference.get('system_tone', 'balanced')
        
        base_instruction = (
            "You are AskSpace AI, a minimalist, high-precision technical assistant for students and software engineers. "
            "Provide clean, well-formatted Markdown with syntax-highlighted code blocks, precise definitions, "
            "and time/space complexity analysis where relevant. "
            "Be direct, insightful, and avoid unnecessary filler."
        )

        if tone_pref == 'concise':
            base_instruction += " Keep answers very concise, bulleted, and immediately actionable."
        elif tone_pref == 'academic':
            base_instruction += " Provide thorough academic explanations, formal definitions, and reference standard theorems."

        if category == 'Coding':
            base_instruction += " Emphasize clean code, error handling, edge cases, and modern standard library conventions."
        elif category == 'Study':
            base_instruction += " Relate concepts to standard Computer Science syllabus topics (OS, DBMS, CN, DSA)."
        elif category == 'Career':
            base_instruction += " Offer practical advice for technical interviews, resumes, and portfolio reviews."

        return base_instruction

    @classmethod
    def process_chat_message(
        cls,
        message_content: str,
        conversation_id: Optional[int] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process user message, persist to DB, invoke provider, and save response."""
        content = message_content.strip() if message_content else ""
        if not content:
            raise ValueError("Message content cannot be empty.")

        if len(content) > 8000:
            raise ValueError("Message exceeds maximum allowed length (8,000 characters).")

        category_clean = category.capitalize() if category and category.capitalize() in VALID_CATEGORIES else 'General'
        if category_clean == 'All':
            category_clean = 'General'

        # Fetch or create conversation
        conversation = None
        is_new_conversation = False
        if conversation_id:
            conversation = db.session.get(Conversation, conversation_id)
            if not conversation:
                raise ValueError(f"Conversation with id {conversation_id} not found.")
        
        if not conversation:
            is_new_conversation = True
            initial_title = cls.generate_title(content)
            conversation = Conversation(
                title=initial_title,
                category=category_clean
            )
            db.session.add(conversation)
            db.session.flush()
        else:
            # If still has default title and only 0-1 messages, auto-title it
            if conversation.title in ('New Chat', 'New Exploration') and len(conversation.messages) <= 1:
                conversation.title = cls.generate_title(content)

        # Persist user message
        user_msg = Message(
            conversation_id=conversation.id,
            role='user',
            content=content
        )
        db.session.add(user_msg)
        db.session.commit()

        # Build message history for provider context (limit last 12 messages for efficiency)
        recent_messages = (
            Message.query.filter_by(conversation_id=conversation.id)
            .order_by(Message.created_at.asc())
            .all()
        )
        context_payload = [{'role': m.role, 'content': m.content} for m in recent_messages[-12:]]

        system_prompt = cls.get_system_prompt(conversation.category)
        provider = get_ai_provider()

        try:
            ai_result = provider.generate_reply(
                messages=context_payload,
                system_prompt=system_prompt,
                category=conversation.category
            )
            assistant_content = ai_result.get('content', '')
            is_demo = ai_result.get('is_demo', False)
            provider_name = ai_result.get('provider', 'demo')
            model_name = ai_result.get('model', 'AskSpace Engine')
        except AIConfigurationError as e:
            assistant_content = (
                f"### Configuration Error: {provider.provider_name.capitalize()}\n\n"
                f"{str(e)}\n\n"
                "> [!TIP]\n"
                "> You can switch to **Demo Mode** or verify your API credentials in the **Settings** tab."
            )
            is_demo = False
            provider_name = provider.provider_name
            model_name = provider.model_name
        except AIServiceUnavailableError as e:
            assistant_content = (
                f"### AI Provider Unavailable\n\n"
                f"{str(e)}\n\n"
                "> [!NOTE]\n"
                "> The remote provider could not complete your request. Please retry in a moment, "
                "or switch to offline **Demo Mode** in Settings."
            )
            is_demo = False
            provider_name = provider.provider_name
            model_name = provider.model_name
        except Exception as e:
            assistant_content = (
                f"### Unexpected Error\n\n"
                f"An error occurred while generating a response: `{str(e)}`."
            )
            is_demo = False
            provider_name = 'unknown'
            model_name = 'unknown'

        # Persist assistant reply
        assistant_msg = Message(
            conversation_id=conversation.id,
            role='assistant',
            content=assistant_content
        )
        db.session.add(assistant_msg)
        conversation.updated_at = datetime.utcnow()
        db.session.commit()

        return {
            'conversation_id': conversation.id,
            'conversation_title': conversation.title,
            'category': conversation.category,
            'is_new': is_new_conversation,
            'user_message': user_msg.to_dict(),
            'assistant_message': assistant_msg.to_dict(),
            'meta': {
                'provider': provider_name,
                'model': model_name,
                'is_demo': is_demo,
            }
        }
