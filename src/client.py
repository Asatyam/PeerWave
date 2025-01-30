import websockets
import asyncio
import httpx
import json
import ssl
import pathlib
from utils.shared import  verify_checksum


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
ssl_context.load_verify_locations(localhost_pem)


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


async def ws_client(filename):
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



if __name__ == "__main__":
    asyncio.run(ws_client("test.txt"))
