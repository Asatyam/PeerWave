import websockets
import asyncio
import os
import json


async def send_file(ws):
    file_contents = None
    with open("./test.txt", "rb") as file:
        file_contents = file.read()
    await ws.send(file_contents)
    print("File sent successfully")

async def ws_client():
    print("WebScoket: Client Connected")
    url = "ws://127.0.0.1:7890"
    async with websockets.connect(url) as ws:
        filepath = 'test.txt'
        file_name = os.path.basename(filepath)
        file_size = os.path.getsize(filepath)
        metadata = {
            "file_name": file_name,
            "file_size": file_size
        }
        to_send_metadata = input("Do you wish to send the metadata(y/n)?")
        if to_send_metadata == "y":
            await ws.send(json.dumps(metadata))
            msg = await ws.recv()
            if msg == "Yes":
                await send_file(ws)
                print("File Transferred successfully!")


asyncio.run(ws_client())
