from graphrag import FileChunkGragService
import time

a = FileChunkGragService()


async def main():

    await a.HandleGraphBuildingProcess("opd_manual.pdf")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
