# MOVA

Offline financial intelligence for African SMEs.

## What It Does

MOVA converts messy WhatsApp messages, OPay SMS, and Pidgin business conversations into structured financial records — completely offline on an 8GB laptop.

## Tech Stack

- **Model**: Llama 3.2 3B Instruct (Q4_K_M quantization)
- **Inference**: llama.cpp (local, CPU-only)
- **Desktop App**: Tauri (Rust + React)
- **Frontend**: React, TypeScript, Vite
- **Deployment**: Fully offline, no cloud, no API calls

## Setup

```bash
# Download the model (~2 GB, one-time)
bash download_model.sh

# Run the application
bash run_demo.sh
```

App launches at `http://localhost:5173` with llama.cpp inference server on port 8080.

## How It Works

1. Paste a business message (WhatsApp, SMS, Pidgin, English, Yoruba, Igbo, Hausa)
2. MOVA extracts: customer, amount, type (receivable/payable), status (outstanding/paid)
3. View your financial dashboard — who owes you, who you owe, net position

## Project Structure

```
mova-app/
├── src/              # React frontend
├── src-tauri/        # Rust backend (Tauri)
├── index.html        # Entry point
├── package.json
└── vite.config.ts
```
