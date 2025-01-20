import websockets
import asyncio
import os
import json
import ssl
import pathlib

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
ssl_context.load_verify_locations(localhost_pem)

async def send_file(ws, file_path):
    file_contents = None
    try:
        with open(file_path, "rb") as file:
            file_contents = file.read()
        await ws.send(file_contents)
        print("File sent successfully")
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")


def get_file_metadata(file_path: str) -> dict:
    # TODO: Handle scenario if the file does not exist
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    return {"file_name": file_name, "file_size": file_size}


async def ws_client():
    print("WebScoket: Client Connected")
    url = "wss://127.0.0.1:7890"
    async with websockets.connect(url, ssl=ssl_context) as ws:
        filepath = "test.txt"
        metadata = get_file_metadata(file_path=filepath)

        to_send_metadata = input("Do you wish to send the metadata(y/n)?")
        if to_send_metadata == "y":
            await ws.send(json.dumps(metadata))
            msg = await ws.recv()
            if msg == "Yes":
                await send_file(ws, filepath)
                print("File Transferred successfully!")


asyncio.run(ws_client())
