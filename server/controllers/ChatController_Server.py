from fastapi import APIRouter
from server.models import ChatServiceRequestModel_Server
from server.services import  ChatService_Server


ChatRouter = APIRouter()
ChatServiceServer = ChatService_Server()


@ChatRouter.post("/chat/public")
async def HandlePublicChat(request: ChatServiceRequestModel_Server):
    response = await ChatServiceServer.ChatService_Server(request=request)
    return response
