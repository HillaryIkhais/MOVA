# MOVA

**Offline financial intelligence for African SMEs.**

MOVA turns messy WhatsApp messages, OPay SMS, and Pidgin voice-note transcripts into structured financial records — completely offline on an 8GB laptop.

---

## The Problem

40 million African SMEs track their money through WhatsApp messages. No structure. No ledger. No visibility. A shop owner in Lagos with 40 credit customers loses ₦50,000–₦100,000 per year from forgotten debts and missed collections.

Cloud-based AI requires internet, API fees, and stable electricity. These are blockers, not features, for the businesses that need financial intelligence most.

## The Solution

MOVA does one thing: **message in → structured record out.**

```
Input:  "Chinedu still dey owe me 85k for the last delivery."
Output: {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}
```

It understands Nigerian English, Nigerian Pidgin, Yoruba, Igbo, and Hausa. It handles "85k", "N50,000", "forty five thousand" formats. It correctly distinguishes "I owe X" (payable) from "X owes me" (receivable) — the hardest problem in informal financial NLP.

## How It Works

1. Paste a business message (WhatsApp, SMS, voice-note transcript)
2. MOVA extracts: **customer**, **amount**, **type** (receivable/payable), **status** (outstanding/paid)
3. View your financial dashboard: who owes you, who you owe, net position

No account. No cloud. No internet.

## Model

- **Llama 3.2 3B Instruct** (Q4_K_M quantization)
- 3.2B parameters, 2 GB on disk
- Runs on CPU (no GPU required)
- 7.3 tokens/second on Apple M3
- Peak RAM: 4 GB

## Benchmark Results

130-example Nigerian economic benchmark (50 English, 50 Pidgin, 30 messy/ambiguous):

| Metric | Score |
|---|---|
| Entity extraction | 98% |
| Amount extraction | 88% |
| Debt direction | 92% |
| Status detection | 91% |
| Full record (all 4 fields) | 78% |

Debt direction improved from 35% → 92% via targeted prompt engineering with explicit direction rules and few-shot payable examples.

## Hardware Requirements

Runs on the hardware Africa already has:
- Intel Core i5 (10th–12th gen) or Apple M-series
- 8 GB RAM
- No GPU required
- No internet required after model download

## Quick Start

```bash
# Download the model (~2 GB, one-time)
bash download_model.sh

# Run the application
bash run_demo.sh
```

App launches at `http://localhost:5173` with llama.cpp inference server on port 8080.

## Project Structure

```
ADTC_Submission/
├── metadata.json          # Submission metadata
├── download_model.sh      # Downloads the GGUF model
├── REPORT.md              # Full technical report
├── run_demo.sh            # Launches server + app
├── .gitignore             # Excludes model/ and *.gguf
├── model/                 # Created by download_model.sh
├── mova-app/              # Tauri + React application
│   ├── src/               # React frontend
│   ├── src-tauri/         # Rust backend
│   └── ...
├── nigerian_benchmark.py  # 130-example benchmark suite
├── language_benchmark.py  # Multi-language test suite
├── benchmark_results.json # Benchmark scoring data
└── language_benchmark.json # Language test results
```

## Languages

| Language | Status | Full Accuracy | Direction |
|---|---|---|---|
| Nigerian English | Verified | 62% | 90% |
| Nigerian Pidgin | Verified | 54% | 88% |
| Messy/Ambiguous | Verified | 50% | 80% |
| Yoruba | Experimental | 40% | — |
| Igbo | Experimental | 55% | — |
| Hausa | Experimental | 50% | — |

## License

Built for ADTC 2026.
