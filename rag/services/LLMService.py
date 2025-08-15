import cerebras.cloud.sdk
from cerebras.cloud.sdk import AsyncCerebras
from rag.enums import LLMChatResponseStatusEnum
from rag.implementations import LLMServiceImpl
from rag.models import (
    LLMChatModel,
    LLMChatResponseModel,
    LLMChatDataModel,
    LLMChatDataUsageModel,
    LLMChatDataChoiseModel,
    LLMChatDataChoiseMessageModel,
)
from cerebras.cloud.sdk import DefaultAioHttpClient
from typing import Any, cast

# os.environ.get("CEREBRAS_API_KEY")


class LLMService(LLMServiceImpl):

    def HandleApiStatusError(self, statusCode: int) -> LLMChatResponseModel:
        errorCodes = {
            400: LLMChatResponseStatusEnum.BAD_REQUEST,
            401: LLMChatResponseStatusEnum.UNAUTHROZIED,
            403: LLMChatResponseStatusEnum.PERMISSION_DENIED,
            404: LLMChatResponseStatusEnum.NOT_FOUND,
        }
        message = errorCodes.get(statusCode, LLMChatResponseStatusEnum.SERVER_ERROR)
        return LLMChatResponseModel(status=message)

    async def Chat(self, modelParams: LLMChatModel) -> LLMChatResponseModel:
        try:
            async with AsyncCerebras(
                api_key=modelParams.apiKey,
                http_client=DefaultAioHttpClient(),
            ) as client:
                chatCompletion: Any = await client.chat.completions.create(  # type: ignore
                    messages=cast(Any, modelParams.messages),
                    model=modelParams.model,
                    max_completion_tokens=modelParams.maxCompletionTokens,
                    stream=modelParams.stream,
                    temperature=modelParams.temperature,
                    response_format=cast(
                        Any,
                        (
                            None
                            if modelParams.responseFormat is None
                            else {
                                "type": modelParams.responseFormat.type,
                                "json_schema": {
                                    "name": modelParams.responseFormat.jsonSchema.name,
                                    "strict": modelParams.responseFormat.jsonSchema.strict,
                                    "schema": modelParams.responseFormat.jsonSchema.jsonSchema,
                                },
                            }
                        ),
                    ),
                )

                choices: list[LLMChatDataChoiseModel] = []
                for ch in chatCompletion.choices:
                    choice: Any = ch
                    choices.append(
                        LLMChatDataChoiseModel(
                            index=choice.index,
                            message=LLMChatDataChoiseMessageModel(
                                role=choice.message.role,
                                content=choice.message.content,
                            ),
                        )
                    )

                LLMData = LLMChatDataModel(
                    id=chatCompletion.id,
                    choices=choices,
                    created=chatCompletion.created,
                    model=chatCompletion.model,
                    totalTime=chatCompletion.time_info.total_time,
                    usage=LLMChatDataUsageModel(
                        promptTokens=chatCompletion.usage.prompt_tokens,
                        completionTokens=chatCompletion.usage.completion_tokens,
                        totalTokens=chatCompletion.usage.total_tokens,
                    ),
                )

                return LLMChatResponseModel(
                    status=LLMChatResponseStatusEnum.SUCCESS, LLMData=LLMData
                )
        except cerebras.cloud.sdk.APIConnectionError as e:
            print(e)
            return LLMChatResponseModel(status=LLMChatResponseStatusEnum.SERVER_ERROR)

        except cerebras.cloud.sdk.RateLimitError as e:
            print(e)
            return LLMChatResponseModel(status=LLMChatResponseStatusEnum.RATE_LIMIT)
        except cerebras.cloud.sdk.APIStatusError as e:
            print(e)
            return self.HandleApiStatusError(e.status_code)
