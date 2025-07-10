"""
class for build prompt template 
it is just for testing and it simple prompt need to improve
"""

from typing import List
from src.schema import ChatMessage


class PromptBuilder:
    """"""
    def __init__(self) -> None:
        self.system_prompt =(
            """
You are a legal assistant chatbot specialized in Canada’s Express Entry immigration program. Answer user questions by retrieving accurate and up-to-date information from official sources such as the Immigration, Refugees and Citizenship Canada (IRCC) website.

Your role is to:

Help users understand Express Entry eligibility, the CRS system, and document requirements.

Provide accurate guidance using only retrieved content from trusted legal/governmental sources.

Never offer personal legal advice or guarantees. When in doubt, refer users to an immigration lawyer or consultant.

Use clear, neutral, and professional language. Prioritize factual, referenced responses based on retrieved IRCC information.
            """
        )

    def build_simple_prompt(
            self,
            query:str,
            context: str,
            history: List[ChatMessage],
            max_history: int =5
        )-> str :
        """Build a structures RAG prompt with converstion history"""

        #format history messages
        history_str = "\n".join(
            f"{msg.role.upper()}: {msg.content}"
            for msg in history[-max_history:]
        )

        return (
            f"SYSTEM: {self.system_prompt}\n\n"
            f"CONVERSATION HISTORY:\n{history_str}\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"QUERY: {query}\n\n"
            "ANSWER:"
        )