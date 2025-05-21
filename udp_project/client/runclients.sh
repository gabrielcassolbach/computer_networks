#!/bin/bash

# Number of clients to start
NUM_CLIENTS=5

# Start clients in the background
echo "[SCRIPT] Starting $NUM_CLIENTS clients..."
for ((i=1; i<=NUM_CLIENTS; i++)); do
    python3 client.py 1mb_file &
done

# Wait for all clients to finish
wait
echo "[SCRIPT] All clients finished."

echo "[SCRIPT] Done."
