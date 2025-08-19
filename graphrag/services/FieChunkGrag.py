from graphrag.implementations import FileChunkGragImpl

from utils import ExtarctTextFromFile, ExtractTextFromDoc


class FileChunkGragService(FileChunkGragImpl):

    def ExatrctChunkFromText(self, file: str, chunkLength: int) -> list[str]:
        text = ExtarctTextFromFile(file)

        return []
