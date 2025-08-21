from graphrag import FileChunkGragService
a = FileChunkGragService()




async def main():
    await a.handleEntitiesProcess("opd_manual.pdf")
    
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 