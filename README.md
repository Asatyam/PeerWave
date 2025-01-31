# P2P File Sharing Application

A decentralized peer-to-peer (P2P) file-sharing system built with **Python, FastAPI, WebSockets, and asyncio** that allows users to share and transfer files directly without relying on a central server.

## Features

- **Peer Registration & Discovery:** Uses a tracker server to maintain a list of active peers.
- **Fast File Transfer:** Implements WebSockets and chunk-based file transfer for efficient data exchange.
- **Searchable File Index:** Peers can search for files across the network.
- **Resilient Transfers:** Supports retry mechanisms for failed file transfers.
- **Secure Connections:** Uses **SSL/TLS encryption** for secure peer communication.
- **Metadata Verification:** Ensures file integrity using checksum validation.

## Tech Stack

- **Backend:** FastAPI (Tracker), WebSockets, asyncio
- **Networking:** WebSockets (ws, wss)
- **Security:** SSL/TLS (secure communication)
- **Database:** In-memory set-based peer tracking
- **Concurrency:** asyncio for efficient non-blocking operations

## Installation & Setup

### Prerequisites

Ensure you have the following installed:

- Python 3.9+
- pip (Python package manager)

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/p2p-file-sharing.git
cd p2p-file-sharing
```

### 2. Install Dependencies

```sh
pip install -r requirements.txt
```

### 3. Start the Tracker Server (FastAPI)

```sh
uvicorn tracker:app --host 0.0.0.0 --port 8000 --reload
```

This will run the tracker server at `http://localhost:8000`.

### 4. Start a Peer

#### Run as Server

```sh
python peer.py --role server --server-port 7890 --file-dir shared_files
```

#### Run as Client

```sh
python peer.py --role client --search-file myfile.txt
```

#### Run in Dual Mode (Server & Client)

```sh
python peer.py --role dual --server-port 7890 --file-dir shared_files --search-file myfile.txt
```

### 5. Searching for Files

You can search for available files on the tracker using:

```sh
python client.py --search-file myfile.txt
```

### 6. Downloading Files

Once you find a peer with the desired file, connect and download:

```sh
python client.py --filename myfile.txt
```

