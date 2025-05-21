#!/bin/bash

# Start the server in the background
echo "[SCRIPT] Starting server..."
python3 server.py &
SERVER_PID=$!
echo "[SCRIPT] Server running with PID $SERVER_PID"

trap "echo '[SCRIPT] Ctrl+C detected. Killing server...'; kill $SERVER_PID; exit 1" SIGINT

# Give the server a moment to start
sleep 1
wait