"""Base agent class for AI Company."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from src.config import get_settings
from src.context.state import CompanyState


class BaseAgent(ABC):
    """Base class for all agents in the company."""

    def __init__(
        self,
        agent_id: str,
        role_name: str,
        model: Optional[str] = None
    ):
        self.agent_id = agent_id
        self.role_name = role_name
        settings = get_settings()
        self.model_name = model or settings.default_model

        self.llm = ChatAnthropic(
            model=self.model_name,
            api_key=settings.anthropic_api_key,
            max_tokens=4096,
        )

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass

    @abstractmethod
    async def process(self, state: CompanyState) -> dict[str, Any]:
        """
        Process the current state and return updates.

        Args:
            state: Current company state

        Returns:
            Dictionary of state updates
        """
        pass

    async def invoke_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """Invoke the LLM with a prompt."""
        messages = []

        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        else:
            messages.append(SystemMessage(content=self.get_system_prompt()))

        messages.append(HumanMessage(content=prompt))

        response = await self.llm.ainvoke(messages)
        return response.content

    async def invoke_llm_with_structured_output(
        self,
        prompt: str,
        output_schema: type,
        system_prompt: Optional[str] = None
    ) -> Any:
        """Invoke LLM and parse output to structured format."""
        structured_llm = self.llm.with_structured_output(output_schema)

        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        else:
            messages.append(SystemMessage(content=self.get_system_prompt()))

        messages.append(HumanMessage(content=prompt))

        return await structured_llm.ainvoke(messages)
