import argparse
from server import start_server
from client import ws_client
import asyncio


def parse_cmd_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file", dest="filepath", default="test.txt", help="name of file to transfer"
    )
    parser.add_argument(
        "-cp",
        "--client-port",
        dest="client_port",
        default=7891,
        help="Configure the port for client ;Default=7891",
        type=int,
    )
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

    args = parser.parse_args()
    return args



#FOR TESTING: As the second instance will be run after a time, the
# client retries to connect to the server at different port
async def client_with_retries(
    address, port, file_path, chunk_size, max_retries=10, delay=2
):
    retries = 0
    while retries < max_retries:
        try:
            print(
                f"Attempting to connect to server at {address}:{port} (try {retries + 1}/{max_retries})"
            )
            await ws_client(address, port, file_path, chunk_size)
            print("Connected successfully!")
            return  
        except ConnectionRefusedError:
            retries += 1
            print(f"Connection failed. Retrying in {delay} seconds...")
            await asyncio.sleep(delay)

    print("Max retries reached. Could not connect to the server.")

async def dual_role_mode(server_port,client_port, address, file_path, chunk_size):
    server_task = asyncio.create_task(start_server(server_port))
    await asyncio.sleep(2)
    client_task = asyncio.create_task(client_with_retries(address, client_port, file_path, chunk_size))
    await asyncio.gather(server_task, client_task)

if __name__ == "__main__":
    args = parse_cmd_line_args()
    if args.role == "server":
        asyncio.run(start_server(args.server_port))
    elif args.role == "client":
        asyncio.run(ws_client(args.address, args.client_port, args.filepath, args.chunk_size))
    elif args.role=="dual":
        asyncio.run(dual_role_mode(args.server_port, args.client_port, args.address, args.filepath, args.chunk_size))
