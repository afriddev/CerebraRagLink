from graphrag import FileChunkGragService

a = FileChunkGragService()


async def main():

    response = await a.HandleChunksGraphBuildingProcess("./others/opd_manual.pdf")
    for i in response.chunkTexts:
        print(i.text)
        print(i.images)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
