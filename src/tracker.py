import fastapi
from pydantic import BaseModel
from datetime import datetime
import uuid

app = fastapi.FastAPI()


class Peer(BaseModel):
    ip: str
    port: int
    metadata: list | None
    last_active: datetime
    token: str
    files: list[str]


class PeerBody(BaseModel):
    ip: str
    port: int
    metadata: list
    files: list[str]

class Token(BaseModel):
    token: str


peers: list[Peer] = []


@app.post("/register")
async def register_peer(peerBody: PeerBody):
    token = str(uuid.uuid4())
    peer = Peer(
        ip=peerBody.ip,
        port=peerBody.port,
        metadata=peerBody.metadata,
        last_active=datetime.utcnow(),
        token=token,
        files=peerBody.files
    )

    peers.append(peer)
    return {
        "message": f"Peer {peer.ip}@{peer.port} saved to the tracker.",
        "token": token,
    }


@app.get("/peers")
async def get_peers(file: str | None = None):
    if not file:
        return {"peers": [peer.model_dump() for peer in peers]}

    res = []
    for peer in peers:
        if file in peer.files:
            res.append(peer)
    
    return {"peers": [peer.model_dump() for peer in res] }


@app.post("/deregister")
async def deregister_peer(token: Token):
    global peers
    peers = [peer for peer in peers if peer.token != token]
    return {"message": "Peer deregistered successfully!"}