from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    mode: str = os.getenv("AGENT_MODE", "evidence")
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    langsmith_project: str = os.getenv("LANGCHAIN_PROJECT", "customer-support-resolution-agent")

settings = Settings()
