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
    actual_size = 0
    try:
        # Open the file and write in binary mode
        with open(output_file, "wb") as file:
            while True:
                chunk = await websocket.recv()
                if not chunk:
                    print("EOF")
                    break
                file.write(chunk)
                actual_size += len(chunk)
                iteration = (actual_size//len(chunk))
                print(f"Wrote {iteration} chunk(s)")
        if actual_size != expected_size:
            raise ValueError(
                f"File size mismatch! Expected: {expected_size}, but go: {actual_size}"
            )

        print(f"File saved as {output_file}")
    except ValueError as e:
        print(f"ERROR: {e}")
    except Exception as e:
        print(f"Error saving the file: {e}")


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
