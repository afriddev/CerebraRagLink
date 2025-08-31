import cerebras.cloud.sdk
from cerebras.cloud.sdk import AsyncCerebras
from fastapi.responses import StreamingResponse
from aiservices.chat.enums import ChatServiceResponseStatusEnum
from aiservices.chat.implementations import ChatServiceImpl
from aiservices.chat.models import (
    ChatServiceRequestModel,
    ChatServiceResponseModel,
    ChatServiceDataResponseModel,
    ChatServiceUsageModel,
    ChatServiceChoiceModel,
    ChatServiceChoiceMessageModel,
)
from cerebras.cloud.sdk import DefaultAioHttpClient
from typing import Any, cast
from aiservices.chat.workers import GetCerebrasApiKey

client = AsyncCerebras(
    api_key=GetCerebrasApiKey(),
    http_client=DefaultAioHttpClient(),
)


class ChatService(ChatServiceImpl):

    def HandleApiStatusError(self, statusCode: int) -> ChatServiceResponseModel:
        errorCodes = {
            400: ChatServiceResponseStatusEnum.BAD_REQUEST,
            401: ChatServiceResponseStatusEnum.UNAUTHROZIED,
            403: ChatServiceResponseStatusEnum.PERMISSION_DENIED,
            404: ChatServiceResponseStatusEnum.NOT_FOUND,
        }
        message = errorCodes.get(statusCode, ChatServiceResponseStatusEnum.SERVER_ERROR)
        return ChatServiceResponseModel(status=message)

    async def Chat(
        self, modelParams: ChatServiceRequestModel
    ) -> ChatServiceResponseModel | StreamingResponse:
        try:
            client.api_key = modelParams.apiKey
            create_call = client.chat.completions.create(
                messages=cast(Any, modelParams.messages),
                model=modelParams.model,
                max_completion_tokens=modelParams.maxCompletionTokens,
                stream=modelParams.stream,
                temperature=modelParams.temperature,
                top_p=modelParams.topP,
                seed=modelParams.seed,
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

            if modelParams.stream:
                chatCompletion: Any = await create_call

                async def eventGenerator():
                    buffer = ""
                    try:
                        async for chunk in chatCompletion:
                            if getattr(chunk, "choices", None):
                                delta = getattr(chunk.choices[0], "delta", None)
                                content = getattr(delta, "content", None)
                                if content:
                                    buffer += content
                                    if "\n" in buffer:
                                        yield f"data: {buffer}\n\n"
                                        buffer = ""
                        if buffer:
                            yield f"data: {buffer}\n\n"
                    except Exception as e:
                        yield f"event: error\ndata: {str(e)}\n\n"

                return StreamingResponse(
                    eventGenerator(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                    },
                )

            chatCompletion: Any = await create_call

            choices: list[ChatServiceChoiceModel] = []
            for ch in chatCompletion.choices:
                choices.append(
                    ChatServiceChoiceModel(
                        index=ch.index,
                        message=ChatServiceChoiceMessageModel(
                            role=ch.message.role,
                            content=ch.message.content,
                        ),
                    )
                )

            LLMData = ChatServiceDataResponseModel(
                id=chatCompletion.id,
                choices=choices,
                created=chatCompletion.created,
                model=chatCompletion.model,
                totalTime=chatCompletion.time_info.total_time,
                usage=ChatServiceUsageModel(
                    promptTokens=chatCompletion.usage.prompt_tokens,
                    completionTokens=chatCompletion.usage.completion_tokens,
                    totalTokens=chatCompletion.usage.total_tokens,
                ),
            )

            return ChatServiceResponseModel(
                status=ChatServiceResponseStatusEnum.SUCCESS, LLMData=LLMData
            )

        except cerebras.cloud.sdk.APIConnectionError as e:
            print(e)
            return ChatServiceResponseModel(
                status=ChatServiceResponseStatusEnum.SERVER_ERROR
            )
        except cerebras.cloud.sdk.RateLimitError as e:
            print(e)
            return ChatServiceResponseModel(
                status=ChatServiceResponseStatusEnum.RATE_LIMIT
            )
        except cerebras.cloud.sdk.APIStatusError as e:
            print(e)
            return self.HandleApiStatusError(e.status_code)
        except Exception as e:
            print(e)
            return ChatServiceResponseModel(status=ChatServiceResponseStatusEnum.ERROR)
