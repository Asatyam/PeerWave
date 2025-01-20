import websockets
import asyncio
import ssl
import pathlib
import json
import os

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
ssl_context.load_cert_chain(localhost_pem)


async def receive_file(websocket, metadata: dict):

    output_file = metadata["file_name"]
    expected_size = metadata["file_size"]

    retries = 0
    max_retries = 3
    while retries < max_retries:
        print(retries)
        try:
            # Open the file and write in binary mode
            actual_size = 0
            chunk_count = 0
            with open(output_file, "wb") as file:
                while True:
                    chunk = await websocket.recv()
                    if chunk == b"":
                        print("EOF")
                        break
                    file.write(chunk)
                    actual_size += len(chunk)
                    chunk_count += 1
                    print(f"{chunk_count}: {actual_size}bytes received")
            if actual_size != expected_size:
                await websocket.send("0")
                retries += 1
                print(
                    f"File size mismatch! Expected: {expected_size}, but got: {actual_size}"
                )
                continue

            print(f"File saved as {output_file}")
            await websocket.send("1")
            break
        except Exception as e:
            print(f"Error saving the file: {e}")
            retries += 1
        if retries < max_retries:
            await asyncio.sleep(2)
    if retries == max_retries:
        print(f"Max retries reached. File could not be saved after {max_retries}")
        await websocket.send("0")


async def ws_server(websocket):

    client_address = websocket.remote_address
    print(f"New client connected: {client_address}")

    try:
        while True:
            metadata = await websocket.recv()
            metadata: dict = json.loads(metadata)
            await receive_file(websocket, metadata)
    except:
        print("Internal Server Error")


async def main():
    async with websockets.serve(ws_server, "localhost", 7890, ssl=ssl_context):
        print("Started Server :)")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
