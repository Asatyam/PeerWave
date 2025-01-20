import websockets
import asyncio
import typing


async def receive_file(websocket):
    file_recv = await websocket.recv()
    output_file = "output.txt"
    try:
        with open(output_file, "wb") as file:
            file.write(file_recv)
        print(f" File saved as {output_file}")
    except:
        print("Error saving the file")


async def ws_server(websocket):
    print("WebSocket: Server started")

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
    print("Starting Server :)")
    async with websockets.serve(ws_server, "localhost", 7890):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
