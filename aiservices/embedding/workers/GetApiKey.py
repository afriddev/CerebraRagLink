import os
from typing import Any, cast
from dotenv import load_dotenv

load_dotenv()


MISTRAL_API_KEY = cast(Any, os.getenv("MISTRAL_API_KEY"))
JINA_API_KEY = cast(Any, os.getenv("JINA_API_KEY"))


def GetMistralApiKey() -> str:
    return MISTRAL_API_KEY


def GetJinaApiKey() -> str:
    return JINA_API_KEY
