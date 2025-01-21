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
        "-p",
        "--port",
        dest="port",
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


if __name__ == "__main__":
    args = parse_cmd_line_args()
    if args.role == "server":
        asyncio.run(start_server(args.port))
    elif args.role == "client":
        asyncio.run(ws_client(args.address, args.port, args.filepath, args.chunk_size))
    else:
        print("Invalid role")
