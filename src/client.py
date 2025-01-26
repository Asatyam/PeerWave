import websockets
import asyncio
import httpx
import json
import ssl
import pathlib
import hashlib
import argparse
from utils.shared import generate_checksum, get_file_metadata

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
    api_url = "http://localhost:8000/peers"  # Tracker URL

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url)
            print(f"Active peers: {response.json()}")
        except Exception as e:
            print(f"Error Getting the peers: {e}")


async def ws_client(address, port, filepath, chunk_size):
    print("WebScoket: Client Connected")
    peers = await get_peers()
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

if __name__=="__main__":
    asyncio.run(ws_client("127.0.0.1", 7890, "test.txt", 10))
