#!/bin/bash

# Number of clients to start
NUM_CLIENTS=1

# Start clients in the background
echo "[SCRIPT] Starting $NUM_CLIENTS clients..."
for ((i=1; i<=NUM_CLIENTS; i++)); do
    python3 client.py 104324.tct  &
done

# Wait for all clients to finish
wait
echo "[SCRIPT] All clients finished."

echo "[SCRIPT] Done."


#

## vamos testar o grandao!diff nao tenho o arquivo base do 1mb