import asyncio

async def helloWorld():
    return "Hello World!"

async def main():
    s = await helloWorld()
    print(s)

asyncio.run(main())
