import fastapi
from contextlib import asynccontextmanager
import pydantic
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid
import asyncio

@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    task = asyncio.create_task(remove_inactive_peers())
    yield
    task.cancel()
    await task

app = fastapi.FastAPI(lifespan=lifespan)


class Peer(BaseModel):
    ip: str
    port: int
    metadata: list | None
    last_active: datetime
    token: str


peers: list[Peer] = []


@app.post("/register")
async def register_peer(ip: str, port: int, metadata: list):
    token = str(uuid.uuid4())
    peer = Peer(
        ip=ip, port=port, metadata=metadata, last_active=datetime.utcnow(), token=token
    )

    peers.append(peer)
    return {"message": f"Peer {peer.ip}@{peer.port} saved to the tracker."}


@app.get("/peers")
async def get_peers(token: str):
    for d in peers:
        if d.token == token:
            d.last_active = datetime.utcnow()
    return {"peers": [peer.model_dump() for peer in peers]}


@app.delete("/deregister")
async def deregister_peer(token: str):
    global peers
    peers = [peer for peer in peers if peer.token != token]
    return {"message": "Peer deregistered successfully!"}


async def remove_inactive_peers():
    while True:
        current_time = datetime.utcnow()
        global peers
        peers = [
            peer
            for peer in peers
            if current_time - peer.last_active <= timedelta(minutes=10)
        ]
        await asyncio.sleep(600)

