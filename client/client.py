import websockets
import asyncio
import os
import json
import ssl
import pathlib
import hashlib

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
ssl_context.load_verify_locations(localhost_pem)

def generate_checksum(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        while chunk:= file.read(4096):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

async def wait_for_transfer_ack(ws):
    msg = await ws.recv()
    if msg == "1":
        return True
    return False

async def send_file(ws, file_path, chunk_size=1024):
    success = False
    retries = 0
    max_retries = 3
    retry_delay = 2
    while not success and retries<max_retries:
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

def get_file_metadata(file_path: str) -> dict:
    # TODO: Handle scenario if the file does not exist
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    checksum = generate_checksum(file_path)
    return {"file_name": file_name, "file_size": file_size,"checksum": checksum}


async def ws_client():
    print("WebScoket: Client Connected")
    url = "wss://127.0.0.1:7890"
    async with websockets.connect(url, ssl=ssl_context) as ws:
        filepath = "test.txt"
        metadata = get_file_metadata(file_path=filepath)

        to_send_metadata = input("Do you wish to send the metadata(y/n)?")
        if to_send_metadata == "y":
            await ws.send(json.dumps(metadata))
        await send_file(ws, filepath, chunk_size=10)


asyncio.run(ws_client())
