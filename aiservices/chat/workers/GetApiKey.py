import os
from typing import Any, cast
from dotenv import load_dotenv
load_dotenv()


CEREBRAS_API_KEY = cast(Any, os.getenv("CEREBRAS_API_KEY"))


def GetCerebrasApiKey() ->str:
    return CEREBRAS_API_KEY