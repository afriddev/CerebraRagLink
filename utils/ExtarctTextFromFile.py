import os
from typing import Any
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredExcelLoader



def ExtractTextFromDoc(file: str) -> str:
        ext = os.path.splitext(file)[1]  
        loader:Any = ""
        if(ext == ".pdf"):
            loader = PyPDFLoader(file)
        elif(ext == ".xlsx" or ext == ".xls"):
            loader = UnstructuredExcelLoader(file, mode="elements")
        
        documents = loader.load()
        fullText = "\n".join(doc.page_content for doc in documents)
        return fullText