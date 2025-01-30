import websockets
import asyncio
import ssl
import pathlib
import json
from utils.shared import verify_checksum, get_file_metadata
import os
from pathlib import Path

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


dir_name_send = ""
avalbl_files = []


def get_files_to_send(dir_name):

    files_dir = os.getcwd() + "/" + dir_name
    files = [
        f for f in os.listdir(files_dir) if os.path.isfile(os.path.join(files_dir, f))
    ]
    return files


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


async def ws_server2(websocket):
    client_address = websocket.remote_address
    print(f"New Client Connected: {client_address}")
    try:
        requested_file = await websocket.recv()
        if requested_file in avalbl_files:
            filepath = Path.joinpath(
                Path(__file__).parent, dir_name_send, requested_file
            )
            metadata = get_file_metadata(filepath)
            await websocket.send(json.dumps(metadata, indent=4))
            await send_file(websocket, filepath, chunk_size=10)
        print("Task finished")
    except Exception as e:
        print(f"Error server: {e}")


async def start_server(port, send_dir):
    async with websockets.serve(ws_server2, "localhost", port, ssl=ssl_context):
        print(f"Started Server on port:{port})")
        global dir_name_send, avalbl_files
        dir_name_send = send_dir
        avalbl_files = get_files_to_send(dir_name_send)
        await asyncio.Future()
    # async with websockets.serve(ws_server, "localhost", port, ssl=ssl_context):
    #     print(f"Started Server on port:{port})")
    #     await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(start_server(7890))
