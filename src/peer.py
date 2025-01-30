import argparse
from server import start_server
from client import ws_client
import asyncio
import httpx
from utils.shared import get_files_to_send
import sys


def parse_cmd_line_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-sp",
        "--server-port",
        dest="server_port",
        default=7890,
        help="Specify the port of the server;Default=7890",
        type=int,
    )
    parser.add_argument(
        "--addr",
        dest="address",
        default="127.0.0.1",
        help="Specify the ip address of the server;Default=127.0.0.1",
    )
    parser.add_argument(
        "--chunk-size",
        dest="chunk_size",
        default=1024,
        help="Specify the size of single chunk of file to transfer of the server(in Bytes);Default=1024B; Maximum Allowed=1048576",
        type=int,
    )
    parser.add_argument(
        "--role",
        dest="role",
        type=str,
        choices=["server", "client", "dual"],
        default="server",
    )
    parser.add_argument("--file-dir", dest="dir", type=str, default="files_send")
    parser.add_argument("--search-file", dest="filename", type=str, default="file1.txt")

    args = parser.parse_args()
    return args


async def client_with_retries(  filename, max_retries=10, delay=2
):
    retries = 0
    while retries < max_retries:
        try:
            print(
                f"Attempting to connect to server. (try {retries + 1}/{max_retries})"
            )
            await ws_client(filename)
            print("Connected successfully!")
            return
        except ConnectionRefusedError:
            retries += 1
            print(f"Connection failed. Retrying in {delay} seconds...")
            await asyncio.sleep(delay)

    print("Max retries reached. Could not connect to the server.")


async def register_peer_with_tracker(ip, port, dir_name):
    api_url = "http://localhost:8000/register" 
    files = get_files_to_send(dir_name)
    peer_data = {"ip": ip, "port": port, "metadata": [], "files": files}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(api_url, json=peer_data)
            print(f"Registered with tracker: {response.json()}")
        except Exception as e:
            print(f"Error registering with tracker: {e}")


async def dual_role_mode(server_port, filename, chunk_size, send_dir):
    server_task = asyncio.create_task(start_server(server_port, send_dir, chunk_size))
    await asyncio.sleep(2)
    client_task = asyncio.create_task(
        client_with_retries(filename)
    )
    await asyncio.gather(server_task, client_task)


async def main(args):

    await register_peer_with_tracker(args.address, args.server_port, args.dir)

    if args.role == "server":
        await start_server(args.server_port)
    elif args.role == "client":
        await ws_client(args.address, args.client_port, args.filename)
    elif args.role == "dual":
        await dual_role_mode(
            args.server_port,
            args.filename,
            args.chunk_size,
            args.dir
        )


if __name__ == "__main__":
    args = parse_cmd_line_args()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("Program interrupted, exiting gracefully.")
        sys.exit(0)
