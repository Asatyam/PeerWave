import websockets
import asyncio
import httpx
import json
import ssl
import pathlib
from utils.shared import get_file_metadata, verify_checksum
from pathlib import Path
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
ssl_context.load_verify_locations(localhost_pem)


async def wait_for_transfer_ack(ws):
    msg = await ws.recv()
    print(msg)
    if msg == "1":
        return True
    return False


async def send_file(ws, file_path, chunk_size=1024):
    success = False
    retries = 0
    max_retries = 3
    retry_delay = 2
    while not success and retries < max_retries:
        try:
            await read_and_send_chunks(ws, file_path, chunk_size)
            success = await wait_for_transfer_ack(ws)

            if not success:
                print(f"File not tranferred. Retrying...{retries}/{max_retries}")
                retries += 1
                await asyncio.sleep(retry_delay)

            else:
                print("File transferred successfully")

        except FileNotFoundError:
            print(f"Error: The file '{file_path}' does not exist.")
            break
        except Exception as e:
            print(f"Error sending file: {e}")
            break
    if not success:
        print("Something went wrong. File Transfer Failed!")


async def read_and_send_chunks(ws, file_path, chunk_size):
    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            await ws.send(chunk)
    await ws.send(b"")


async def get_peers():
    api_url = f"http://localhost:8000/peers"  # Tracker URL
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url)
            print(f"Active peers: {json.dumps(response.json(), indent=4)}")
        except Exception as e:
            print(f"Error Getting the peers: {e}")


async def search_file(filename):
    api_url = f"http://localhost:8000/search?file={filename}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url)
            print(
                f"Peers having the requested file {filename}: {json.dumps(response.json(), indent=4)}"
            )
            return response.json()
        except Exception as e:
            print(f"Error searching file: {e}")
            return []


async def receive_file(websocket, metadata: dict):

    output_file = f"{recv_dir}/{metadata['file_name']}"
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


async def validate_file(actual_size, output_file, metadata):
    expected_size = metadata["file_size"]
    expected_checksum = metadata["checksum"]
    if actual_size != expected_size:
        return False
    if not verify_checksum(output_file, expected_checksum):
        return False
    return True


recv_dir = (
    "/Users/satyamagrawal/Desktop/WebDev/Projects/p2p-file-sharing/src/received_files"
)


async def ws_client2(address, port, filepath, chunk_size, filename):
    print("Websocket: Client Connected")
    searched_peers = await search_file(filename)
    for peer in searched_peers:
        address, port = peer["ip"], peer["port"]
        url = f"wss://{address}:{port}"
        async with websockets.connect(url, ssl=ssl_context) as ws:
            try:
                await ws.send(filename)
                metadata = await ws.recv()
                metadata: dict = json.loads(metadata)
                print(metadata)
                await receive_file(ws, metadata)

            except Exception as e:
                print(f"Error Client : {e}")


async def ws_client(address, port, filepath, chunk_size, filename):
    print("WebScoket: Client Connected")
    peers = await get_peers()
    searched_peers = await search_file(filename)
    url = f"wss://{address}:{port}"
    async with websockets.connect(url, ssl=ssl_context) as ws:
        try:
            metadata = get_file_metadata(file_path=filepath)
            await ws.send(json.dumps(metadata))
            await send_file(ws, filepath, chunk_size=chunk_size)
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Something went wrong: {e}")


if __name__ == "__main__":
    asyncio.run(ws_client2("127.0.0.1", 7890, "test.txt", 10))
    # asyncio.run(ws_client("127.0.0.1", 7890, "test.txt", 10))
