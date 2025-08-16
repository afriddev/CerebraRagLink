import cerebras.cloud.sdk
from cerebras.cloud.sdk import AsyncCerebras
from clientservices.cerebras.enums import LLMResponseEnum
from clientservices.cerebras.implementations import LLMServiceImpl
from clientservices.cerebras.models import (
    LLMRequestModel,
    LLMResponseModel,
    LLMDataModel,
    LLMDataUsageModel,
    LLMDataChoiceModel,
    LLMDataChoiceMessageModel,
)
from cerebras.cloud.sdk import DefaultAioHttpClient
from typing import Any, cast


class LLMService(LLMServiceImpl):

    def HandleApiStatusError(self, statusCode: int) -> LLMResponseModel:
        errorCodes = {
            400: LLMResponseEnum.BAD_REQUEST,
            401: LLMResponseEnum.UNAUTHROZIED,
            403: LLMResponseEnum.PERMISSION_DENIED,
            404: LLMResponseEnum.NOT_FOUND,
        }
        message = errorCodes.get(statusCode, LLMResponseEnum.SERVER_ERROR)
        return LLMResponseModel(status=message)

    async def Chat(self, modelParams: LLMRequestModel) -> LLMResponseModel:
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

                choices: list[LLMDataChoiceModel] = []
                for ch in chatCompletion.choices:
                    choice: Any = ch
                    choices.append(
                        LLMDataChoiceModel(
                            index=choice.index,
                            message=LLMDataChoiceMessageModel(
                                role=choice.message.role,
                                content=choice.message.content,
                            ),
                        )
                    )

                LLMData = LLMDataModel(
                    id=chatCompletion.id,
                    choices=choices,
                    created=chatCompletion.created,
                    model=chatCompletion.model,
                    totalTime=chatCompletion.time_info.total_time,
                    usage=LLMDataUsageModel(
                        promptTokens=chatCompletion.usage.prompt_tokens,
                        completionTokens=chatCompletion.usage.completion_tokens,
                        totalTokens=chatCompletion.usage.total_tokens,
                    ),
                )

                return LLMResponseModel(status=LLMResponseEnum.SUCCESS, LLMData=LLMData)
        except cerebras.cloud.sdk.APIConnectionError as e:
            print(e)
            return LLMResponseModel(status=LLMResponseEnum.SERVER_ERROR)

        except cerebras.cloud.sdk.RateLimitError as e:
            print(e)
            return LLMResponseModel(status=LLMResponseEnum.RATE_LIMIT)
        except cerebras.cloud.sdk.APIStatusError as e:
            print(e)
            return self.HandleApiStatusError(e.status_code)
