import re
from typing import Any, Tuple, cast
import unicodedata
from uuid import uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter
from ragservices.implementations import RagUtilServiceImpl_Rag
from ragservices.services.ExtractTextFromDocService_Rag import ExtractTextFromDocService


import base64
import firebase_admin
from firebase_admin import credentials, storage

cred = credentials.Certificate("./others/firebaseCred.json")
cast(Any, firebase_admin).initialize_app(
    cred, {"storageBucket": "testproject-b1efd.appspot.com"}
)


class RagUtilService_Rag(RagUtilServiceImpl_Rag):

    def __init__(self):
        self.ExtarctTextFromDoc = ExtractTextFromDocService()

    def ExtractChunksFromDoc_Rag(
        self, file: str, chunkSize: int, chunkOLSize: int | None = 0
    ) -> Tuple[list[str], list[str]]:
        _PAGE_RE = re.compile(r"\bpage\s+\d+\s+of\s+\d+\b", re.IGNORECASE)
        _IMAGE_RE = re.compile(r"\s*(<<IMAGE-\d+>>)\s*", re.IGNORECASE)
        _BULLET_LINE_RE = re.compile(r"^[\s•\-\*\u2022\uf0b7FÞ]+(?=\S)", re.MULTILINE)
        _SOFT_HYPHEN_RE = re.compile(r"\u00AD")
        _HYPHEN_BREAK_RE = re.compile(r"(\w)-\n(\w)")
        _MULTI_NL_RE = re.compile(r"\n{3,}")
        _WS_NL_RE = re.compile(r"[ \t]+\n")
        _WS_RUN_RE = re.compile(r"[ \t]{2,}")

        def _normalizeText(raw: str) -> str:
            t = unicodedata.normalize("NFKC", raw)
            t = _SOFT_HYPHEN_RE.sub("", t)
            t = _PAGE_RE.sub(" ", t)
            t = _BULLET_LINE_RE.sub("", t)
            t = _HYPHEN_BREAK_RE.sub(r"\1\2", t)
            t = _IMAGE_RE.sub(r" \1 ", t)
            t = _WS_NL_RE.sub("\n", t)
            t = _MULTI_NL_RE.sub("\n\n", t)
            t = _WS_RUN_RE.sub(" ", t)
            t = re.sub(r"\s+", " ", t)
            return t.strip()

        def _mergeTinyChunks(chunks: list[str], minChars: int) -> list[str]:
            merged: list[str] = []
            carry = ""
            for ch in chunks:
                chs = ch.strip()
                if not chs:
                    continue
                if _IMAGE_RE.fullmatch(chs) or len(chs) < minChars:
                    if merged:
                        merged[-1] = (merged[-1].rstrip() + " " + chs).strip()
                    else:
                        carry = (carry + " " + chs).strip()
                else:
                    if carry:
                        chs = (carry + " " + chs).strip()
                        carry = ""
                    merged.append(chs)
            if carry:
                if merged:
                    merged[-1] = (merged[-1].rstrip() + " " + carry).strip()
                else:
                    merged = [carry]
            return merged

        text, images = self.ExtarctTextFromDoc.ExtractTextFromDoc_Rag(file)
        text = _normalizeText(text)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunkSize,
            chunk_overlap=chunkOLSize or 0,
            separators=["\n\n", "\n", " "],
            is_separator_regex=False,
            length_function=len,
        )
        chunks = splitter.split_text(text)
        chunks = _mergeTinyChunks(chunks, minChars=max(200, chunkSize // 3))
        return (
            chunks,
            images,
        )

    async def UploadImagesFromDocToFirebase_Rag(
        self, base64Str: str, folder: str
    ) -> str:
        imageBytes: bytes = base64.b64decode(base64Str)
        filename: str = f"{folder}/{uuid4()}.png"
        bucket: Any = cast(Any, storage).bucket()
        blob: Any = bucket.blob(filename)
        blob.upload_from_string(imageBytes, content_type="image/png")
        blob.make_public()
        publicUrl: str = cast(str, blob.public_url)
        return publicUrl
