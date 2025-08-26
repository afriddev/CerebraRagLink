from graphrag import FileChunkGragService

a = FileChunkGragService()


async def main():

    response = await a.HandleChunksGraphBuildingProcess("opd_manual.pdf")
    for i in response.chunkTexts:
        print(i.id)
        print(i.text)
        print(i.questions)
        print(i.matchedNodes)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
