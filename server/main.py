import websockets
import asyncio
import ssl
import pathlib

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
ssl_context.load_cert_chain(localhost_pem)

async def receive_file(websocket):
    file_recv = await websocket.recv()
    output_file = "output.txt"
    try:
        # Open the file and write in binary mode
        with open(output_file, "wb") as file:
            file.write(file_recv)
        print(f" File saved as {output_file}")
    except:
        print("Error saving the file")


async def ws_server(websocket):
    
    client_address = websocket.remote_address
    print(f"New client connected: {client_address}")

    try:
        while True:
            metadata = await websocket.recv()
            print(metadata)
            msg = input("Do you wish to receive the file(Yes/No)")
            await websocket.send(msg)
            if msg == "Yes":
                await receive_file(websocket)
    except:
        print("Internal Server Error")


async def main():
    async with websockets.serve(ws_server, "localhost", 7890, ssl=ssl_context):
        print("Started Server :)")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
