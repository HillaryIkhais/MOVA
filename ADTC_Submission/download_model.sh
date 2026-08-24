#!/bin/bash
set -e

MODEL_DIR="./model"
MODEL_FILE="$MODEL_DIR/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
MODEL_URL="https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf?download=true"

echo "==========================================="
echo "  SabiCore Elite — Model Downloader"
echo "==========================================="

mkdir -p "$MODEL_DIR"

if [ -f "$MODEL_FILE" ]; then
  echo "Model already exists at $MODEL_FILE"
  echo "Skipping download."
else
  echo "Downloading Llama-3.2-3B-Instruct Q4_K_M..."
  echo "Source: HuggingFace (bartowski/Meta-Llama-3.2-3B-Instruct-GGUF)"
  echo ""
  echo "This may take several minutes depending on your connection."
  echo ""

  curl -L --progress-bar -o "$MODEL_FILE" "$MODEL_URL"

  echo ""
  echo "Download complete."
fi

echo ""
echo "Model ready: $MODEL_FILE"
echo "Run the app with: bash run_demo.sh"
