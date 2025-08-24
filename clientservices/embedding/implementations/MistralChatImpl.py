from abc import ABC, abstractmethod
from clientservices.embedding.models import (
    MistralChatResponseModel,
    MistralChatRequestModel,
)


class MistralChatImpl(ABC):

    @abstractmethod
    async def Chat(
        self, modelParams: MistralChatRequestModel
    ) -> MistralChatResponseModel:
        pass
