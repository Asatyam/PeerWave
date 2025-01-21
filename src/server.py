import websockets
import asyncio
import ssl
import pathlib
import json
from utils.shared import verify_checksum

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
ssl_context.load_cert_chain(localhost_pem)



async def validate_file(actual_size, output_file, metadata):
    expected_size = metadata["file_size"]
    expected_checksum = metadata["checksum"]
    if actual_size != expected_size:
        return False
    if not verify_checksum(output_file, expected_checksum):
        return False
    return True


async def receive_file(websocket, metadata: dict):

    output_file = metadata["file_name"]
    retries = 0
    max_retries = 3
    while retries < max_retries:
        try:
            actual_size = await receive_chunk(websocket, output_file)
            if not await validate_file(actual_size, output_file, metadata):
                retries += 1
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


async def receive_chunk(websocket, output_file):
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
    return actual_size


async def ws_server(websocket):

    client_address = websocket.remote_address
    print(f"New client connected: {client_address}")

    try:
        while True:
            metadata = await websocket.recv()
            metadata: dict = json.loads(metadata)
            await receive_file(websocket, metadata)
    except websockets.exceptions.ConnectionClosed:
        print(f"Client @ {client_address} closed the connection")
    except Exception as e:
        print(f"Error: {e}")


async def start_server(port):
    async with websockets.serve(ws_server, "localhost", port, ssl=ssl_context):
        print(f"Started Server on port:{port})")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(start_server(7890))
