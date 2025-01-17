import websockets
import asyncio

async def ws_client():
    print("WebScoket: Client Connected")
    url = "ws://127.0.0.1:7890"
    async with websockets.connect(url) as ws:
        name = input("Your name (type 'exit'to quit): ")

        if name == "exit":
            exit()
        age = input("Your Age: ")
        await ws.send(f"{name}")
        await ws.send(f"{age}")

        while True:
            msg = await ws.recv()
            print(msg)

asyncio.run(ws_client())

