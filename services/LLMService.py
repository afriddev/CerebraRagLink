import cerebras.cloud.sdk
from cerebras.cloud.sdk import AsyncCerebras
from enums.LLMServiceEnums import LLMChatResponseStatusEnum
from implementations.LLMServiceImplementation import  LLMServiceImpl
from models.LLMServiceModels import LLMChatModel, LLMChatResponseModel
from cerebras.cloud.sdk import DefaultAioHttpClient
from typing import Any,cast


#os.environ.get("CEREBRAS_API_KEY")

class LLM(LLMServiceImpl):
    
    def HandleApiStatusError(self,statusCode:int) -> LLMChatResponseModel:
        errorCodes = {
            400 : LLMChatResponseStatusEnum.BAD_REQUEST,
            401 : LLMChatResponseStatusEnum.UNAUTHROZIED,
            403 : LLMChatResponseStatusEnum.PERMISSION_DENIED,
            404 : LLMChatResponseStatusEnum.NOT_FOUND
        }
        message = errorCodes.get(statusCode,LLMChatResponseStatusEnum.SERVER_ERROR)
        return LLMChatResponseModel(
                status=message
            )
            
    async def Chat(self,modelParams: LLMChatModel) -> LLMChatResponseModel:
            try:
                async with AsyncCerebras(
                api_key=modelParams.apiKey,
                http_client=DefaultAioHttpClient(),
                ) as client:
                chat_completion = await client.chat.completions.create( # type: ignore
                messages=cast(Any,modelParams.messages),
                model=modelParams.model,
                max_completion_tokens=modelParams.maxCompletionTokens,
                stream=modelParams.stream,
                reasoning_effort=modelParams.reasoningEffort.value,
                temperature= modelParams.temperature
                    )
                return LLMChatResponseModel(
                    status=LLMChatResponseStatusEnum.SUCCESS
                )
            except cerebras.cloud.sdk.APIConnectionError as e:
                print(e)
                return LLMChatResponseModel(
                    status=LLMChatResponseStatusEnum.SERVER_ERROR
                )
                
            except cerebras.cloud.sdk.RateLimitError as e:
                print(e)
                return LLMChatResponseModel(
                    status=LLMChatResponseStatusEnum.RATE_LIMIT
                )
            except cerebras.cloud.sdk.APIStatusError as e:
                print(e)
                return self.HandleApiStatusError(e.status_code)
                
                
            
                
            
                
    
        
        
