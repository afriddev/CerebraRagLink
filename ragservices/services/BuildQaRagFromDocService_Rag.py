from ragservices.implementations import BuildQaRagFromDocImpl_Rag
from ragservices.models import ExtarctQuestionAndAnswersFromDocResponse_Rag


import re


class BuildQaRagFromDocService_Rag(BuildQaRagFromDocImpl_Rag):

    def ExtarctQuesionAndAnsersFromDocText_Rag(
        self, text: str
    ) -> ExtarctQuestionAndAnswersFromDocResponse_Rag:
        questionList = re.findall(r"<<R1-START>>(.*?)<<R1-END>>", text, re.DOTALL)
        answersList = re.findall(r"<<R2-START>>(.*?)<<R2-END>>", text, re.DOTALL)
