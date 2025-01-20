import websockets
import asyncio
import ssl
import pathlib
import json
import os
import hashlib

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
ssl_context.load_cert_chain(localhost_pem)


def verify_checksum(file_path, expected_checksum):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as file:
            while chunk := file.read(4096):
                sha256_hash.update(chunk)

        actual_checksum = sha256_hash.hexdigest()
        return actual_checksum == expected_checksum

    except Exception as e:
        print(f"Error calculating checksum for {file_path}: {e}")
        return False


async def validate_file(actual_size, output_file, metadata):
    expected_size = metadata["file_size"]
    expected_checksum = metadata["checksum"]
    if actual_size != expected_size:
        return False
    if not verify_checksum(output_file, expected_checksum):
        return False
    return True


async def receive_file(websocket, metadata: dict):
    print(metadata)
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
    except:
        print("Internal Server Error")


async def main():
    async with websockets.serve(ws_server, "localhost", 7890, ssl=ssl_context):
        print("Started Server :)")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
