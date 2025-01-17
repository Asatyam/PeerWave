import websockets
import asyncio
import typing

async def ws_server(websocket):
    print("WebSocket: Server started")

    try:
        while True:
            name: str = await websocket.recv()
            age: int = await websocket.recv()

            if name == "" or age == "":
                print("Error Receiving Value from Client.")
                break
                
            print("Details Received from Client:")
            print(f"Name: {name}")
            print(f"Age: {age}")

            if int(age) < 18:
                await websocket.send(f"Sorry! {name}, You can't join the club.")
            else:
                await websocket.send(f"Welcome aboard, {name}.")
    except:
        print("Internal Server Error")

async def main():
    print("Starting Server :)")
    async with websockets.serve(ws_server, "localhost", 7890):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
