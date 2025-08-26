from typing import Any, cast
from aiservices.embedding.implementations import MistralChatImpl
from mistralai import Mistral, models
from aiservices.embedding.models import (
    MistralChatResponseModel,
    MistralChatResponseUsageModel,
    MistralChatResponseChoiceModel,
    MistralChatResponseMessageModel,
    MistralChatRequestModel,
)
from aiservices.embedding.enums import MistralChatResponseStatusEnum
from aiservices.embedding.workers import GetMistralApiKey


"""
--------------------- MISTRAL OEPN MDOELS -------------------------
Mistral Small 3.2   -> mistral-small-2506 -> 128k context -> 24B
Mistral Small 3.1   -> mistral-small-2503 -> 128k Context -> 24B
Mistral Nemo 12B    -> open-mistral-nemo  -> 128k Context -> 12b
------------------------------------------------------------------
"""

mistral = Mistral(api_key=GetMistralApiKey())


class MistralChatService(MistralChatImpl):

    async def Chat(
        self, modelParams: MistralChatRequestModel
    ) -> MistralChatResponseModel:

        try:
            messages: Any = []

            for message in modelParams.messages:
                messages.append(
                    {"role": message.role.value, "content": message.content}
                )

            mistralResponse =  await  mistral.chat.parse_async(
                messages=messages,
                model=modelParams.model,
                temperature=modelParams.temperature,
                max_tokens=modelParams.maxTokens,
                stream=modelParams.stream,
                response_format=cast(Any, modelParams.responseFormat),
            )

            usage = MistralChatResponseUsageModel(
                promptTokens=mistralResponse.usage.prompt_tokens,
                completionToken=mistralResponse.usage.completion_tokens,
                totalTokens=mistralResponse.usage.total_tokens,
            )
            choices: list[MistralChatResponseChoiceModel] = []
            for index, choice in enumerate(mistralResponse.choices):
                choices.append(
                    MistralChatResponseChoiceModel(
                        index=index,
                        message=MistralChatResponseMessageModel(
                            content=cast(Any, choice.message.content),
                            role=choice.message.role,
                        ),
                    )
                )
            return MistralChatResponseModel(
                id=mistralResponse.id,
                model=mistralResponse.model,
                usgae=usage,
                created=mistralResponse.created,
                choices=choices,
                status=MistralChatResponseStatusEnum.SUCCESS,
            )
        except models.HTTPValidationError as e:
            print(e)
            return MistralChatResponseModel(
                status=MistralChatResponseStatusEnum.VALIDATION_ERROR
            )

        except models.SDKError as e:
            print(e)
            return MistralChatResponseModel(status=MistralChatResponseStatusEnum.ERROR)
        except Exception as e:
            print(e)
            return MistralChatResponseModel(
                status=MistralChatResponseStatusEnum.SERVER_ERROR
            )
