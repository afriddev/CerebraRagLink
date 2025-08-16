import os
from typing import Any, cast
from dotenv import load_dotenv
load_dotenv()


MISRAL_API_KEY = cast(Any, os.getenv("MISTRAL_API_KEY"))


def GetMistralApiKey() ->str:
    return MISRAL_API_KEY