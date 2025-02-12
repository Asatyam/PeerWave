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
    files: list[str]

    def __hash__(self):
        return hash((self.ip, self.port))

    def __eq__(self, other):
        if not isinstance(other, Peer):
            return False
        return self.ip == other.ip and self.port == other.port


class PeerBody(BaseModel):
    ip: str
    port: int
    metadata: list
    files: list[str]

class Token(BaseModel):
    token: str

peers: set[Peer] = set()


@app.post("/register")
async def register_peer(peerBody: PeerBody):
    peer = Peer(
        ip=peerBody.ip,
        port=peerBody.port,
        metadata=peerBody.metadata,
        last_active=datetime.utcnow(),
        files=peerBody.files,
    )

    peers.add(peer)
    return {
        "message": f"Peer {peer.ip}@{peer.port} saved to the tracker.",
    }


@app.get("/peers")
async def get_peers():
    response = {"peers": [peer.model_dump() for peer in peers]}
    return response


@app.get("/search")
async def search_files(file: str):
    response = []
    for peer in peers:
        if file in peer.files:
            response.append(peer)

    return response


@app.post("/deregister")
async def deregister_peer(token: Token):
    global peers
    peers = set([peer for peer in peers if peer.token != token])
    return {"message": "Peer deregistered successfully!"}
