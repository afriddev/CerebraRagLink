import os
from typing import Any, cast
from dotenv import load_dotenv
load_dotenv()


Mistral_API_KEY = cast(Any, os.getenv("MISTRAL_API_KEY"))


def GetMistralApiKey() ->str:
    return Mistral_API_KEY