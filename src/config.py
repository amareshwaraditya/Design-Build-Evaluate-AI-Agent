from dataclasses import dataclass
import os
from pathlib import Path

# Windows sometimes links two OpenMP runtimes (numpy + faiss-cpu); this avoids a hard crash.
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

# Force-load every variable from the project .env directly into os.environ.
# We bypass load_dotenv because it has known quirks with Windows + Streamlit
# where override=True silently fails depending on process inheritance.
if ENV_FILE.exists():
    for _line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _key, _, _value = _line.partition("=")
        _value = _value.strip()
        # Strip surrounding quotes (single or double) that .env files commonly use
        if len(_value) >= 2 and _value[0] == _value[-1] and _value[0] in ('"', "'"):
            _value = _value[1:-1]
        os.environ[_key.strip()] = _value

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
