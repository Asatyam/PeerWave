import websockets
import asyncio
import ssl
import json
from utils.shared import get_file_metadata, get_files_to_send
from pathlib import Path

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
localhost_pem = Path(__file__).with_name("localhost.pem")
ssl_context.load_cert_chain(localhost_pem)


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


async def ws_server(websocket, send_dir, chunk_size):
    avalbl_files = get_files_to_send(send_dir)
    client_address = websocket.remote_address
    print(f"New Client Connected: {client_address}")
    try:
        requested_file = await websocket.recv()
        if requested_file in avalbl_files:
            filepath = Path.joinpath(Path(__file__).parent, send_dir, requested_file)
            metadata = get_file_metadata(filepath)
            print(f"Transferring file: {requested_file}")
            await websocket.send(json.dumps(metadata, indent=4))
            await send_file(websocket, filepath, chunk_size)
        print(f"Task finished for {client_address}")
    except FileNotFoundError:
        print("Requested file does not exist or has been deleted from the server!!")
    except websockets.exceptions.ConnectionClosed:
        print(f"Client {client_address} disconnected.")
    except Exception as e:
        print(f"Error server: {e}")


async def start_server(port, send_dir, chunk_size):

    async def ws_server_wrapper(websocket):
        task = asyncio.create_task(ws_server(websocket, send_dir, chunk_size))
        await task

    async with websockets.serve(ws_server_wrapper, "localhost", port, ssl=ssl_context):
        print(f"Started Server on port:{port}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(start_server(7890))
