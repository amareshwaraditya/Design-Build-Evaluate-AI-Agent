from dataclasses import dataclass
import os
from pathlib import Path

# Windows sometimes links two OpenMP runtimes (numpy + faiss-cpu); this avoids a hard crash.
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

# Always load from .env with override=True so the project key takes precedence
# over stale or empty values inherited from the process environment (common with
# IDE launchers and Streamlit Cloud).
load_dotenv(ENV_FILE, override=True)

try:  # pragma: no cover - only relevant when running under Streamlit Cloud
    import streamlit as st

    for _key, _value in st.secrets.items():
        os.environ.setdefault(_key, str(_value))
except Exception:
    pass

@dataclass(frozen=True)
class Settings:
    mode: str = os.getenv("AGENT_MODE", "live")
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    temperature: float = float(os.getenv("AGENT_TEMPERATURE", "0.3"))
    max_tool_iterations: int = int(os.getenv("AGENT_MAX_TOOL_ITERATIONS", "3"))
    langsmith_project: str = os.getenv("LANGCHAIN_PROJECT", "customer-support-resolution-agent")

    @property
    def has_api_key(self) -> bool:
        key = os.getenv("OPENAI_API_KEY", "")
        return bool(key.strip())

settings = Settings()
