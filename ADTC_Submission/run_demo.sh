#!/bin/bash

export PATH="$HOME/.cargo/bin:$PATH"

export PATH="$HOME/.cargo/bin:$PATH"

echo "========================================================="
echo "    SabiCore Elite: Native Desktop App (Tauri + GPU)     "
echo "========================================================="
echo "Starting the offline GPU inference engine (llama-server)..."

# Start the server in the background
./llama.cpp/build/bin/llama-server \
  -m ./llama.cpp/models/Llama-3.2-3B-Instruct/Llama-3.2-3B-Instruct-Q4_K_M.gguf \
  -c 2048 \
  -t 4 \
  --port 8080 > server_logs.txt 2>&1 &

SERVER_PID=$!

echo "Engine is warming up. Waiting 5 seconds..."
sleep 5

echo "Launching Native Tauri Application..."
cd SabiTrade_App
npm install
npm run tauri dev

echo "========================================================="
echo "Shutting down GPU engine..."
kill $SERVER_PID
