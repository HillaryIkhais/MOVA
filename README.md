# MOVA

**Offline financial intelligence for African SMEs.**

MOVA turns messy WhatsApp messages, OPay SMS, and Pidgin voice-note transcripts into structured financial records — completely offline on an 8GB laptop.

---

## The Problem

40 million African SMEs track their money through WhatsApp messages. A shop owner in Lagos with 40 credit customers has no structure, no ledger, no visibility. She loses an estimated ₦50,000–₦100,000 per year from forgotten debts and missed collections.

Cloud-based AI requires internet, API fees, and stable electricity. These are blockers, not features, for the businesses that need financial intelligence most. Sensitive business conversations sent to cloud APIs also raise privacy concerns for credit tracking and debt management.

## The Solution

MOVA does one thing: **message in → structured record out.**

```
Input:  "Chinedu still dey owe me 85k for the last delivery."
Output: {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}
```

It understands Nigerian English, Nigerian Pidgin, Yoruba, Igbo, and Hausa. It handles "85k", "N50,000", "forty five thousand" formats. It correctly distinguishes "I owe X" (payable) from "X owes me" (receivable) — the hardest problem in informal financial NLP.

### Core Loop

1. Receives messy business communication (WhatsApp, SMS, Pidgin, local languages)
2. Understands intent and economic meaning (not just keywords)
3. Structures it into financial state (who owes whom, how much, why, when)
4. Tracks the informal credit economy locally (debts, payments, remaining balances, due dates)
5. Generates actionable reminders and summaries — all offline

### Why This Needs an LLM

A regex parser can extract "N50,000 from CHINEDU OKAFOR" from a structured SMS. It cannot handle:

> "Abeg remind me say Chinedu still owe me 45k from the last delivery. He said he'll pay after market day. And also Mama Adura don pay the remaining 20k wey she owe me from last month. So her own don finish."

This is how African SMEs actually communicate — mixed Pidgin/English, implicit context, multiple transactions in one message, cultural time references ("after market day"), and incomplete information.

The LLM does four things a parser cannot:

1. **Understands intent** — "abeg remind" = create a reminder, not just log text
2. **Resolves ambiguity** — "45k" = ₦45,000, "after market day" = due date
3. **Tracks credit state** — recognizes "Mama Adura don pay" = debt settled, updates ledger
4. **Takes action** — generates structured records with customer, amount, type, context, and status

## Demo Cases

### Pidgin Debt Extraction

**Input:**
```
Chinedu still dey owe me 85k for that delivery.
```

**Output:**
```json
{"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}
```

### Payment Settlement

**Input:**
```
Mama Adura don pay her 20k. Her own don finish.
```

**Output:**
```json
{"customer": "Mama Adura", "amount": "20000", "type": "receivable", "status": "paid"}
```

### Supplier Payment

**Input:**
```
I wan pay Alhaji Bello 250k for 50 bags of rice.
```

**Output:**
```json
{"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}
```

### Yoruba Debt

**Input:**
```
Chinedu ti ko si ide 85k fun awon ohun ti mo fun ni.
```

**Output:**
```json
{"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}
```

### OPay SMS

**Input:**
```
OPay: You have received N50,000.00 from CHINEDU OKAFOR. Ref: 20260817001.
```

**Output:**
```json
{"customer": "CHINEDU OKAFOR", "amount": "50000", "type": "receivable", "status": "paid"}
```

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

### Results by Language

| Language | Full Accuracy | Direction | Status |
|---|---|---|---|
| Nigerian English | 62% | 90% | 100% |
| Nigerian Pidgin | 54% | 88% | 88% |
| Messy/Ambiguous | 50% | 80% | 80% |
| Yoruba | 40% | — | — |
| Igbo | 55% | — | — |
| Hausa | 50% | — | — |

### Key Finding

The model's biggest weakness was **debt direction** — flipping "I owe X" to receivable. With targeted prompt engineering (explicit direction rules + few-shot examples), payable direction accuracy improved from **35% to 92%**. This is the core of MOVA's value: correctly understanding who owes whom in informal African commerce.

## Hardware Requirements

Runs on the hardware Africa already has:

- Intel Core i5 (10th–12th gen) or Apple M-series
- 8 GB RAM
- No GPU required
- No internet required after model download

## Profiler Results

| Metric | Value |
|---|---|
| Throughput | 7.32 tokens/sec |
| Peak RSS | 4,017 MB |
| Accuracy (arc_easy) | 72% |
| Thermal throttling | No |
| Parameter count | 3,212,749,888 (confirmed) |

### ADTC Scoring

| Component | Weight | Score |
|---|---|---|
| S_ACC (Accuracy) | 50% | 72.0 |
| S_PERF (Throughput) | 30% | 48.8 |
| S_EFF (Efficiency) | 20% | 42.6 |
| P_THERMAL | — | 0 (no penalty) |

**Estimated total: 59.2 / 100** (before African Use Case bonus)

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

## Design Decisions

| Decision | Rationale |
|---|---|
| **Llama-3.2-3B (Q4_K_M)** | Right size for 8GB laptops. Instruction-tuned for structured extraction. Fits the ADTC thesis: small models optimized for the actual economic language of the user. |
| **Tauri (Rust + React)** | Native desktop app with small binary size. Rust backend for memory safety. |
| **llama.cpp server** | Battle-tested local inference engine. HTTP API for frontend communication. |
| **Q4_K_M quantization** | Optimal quality-to-size ratio. 2.02 GB on disk. |
| **Offline-first architecture** | Entire financial intelligence layer runs without internet. Sensitive business conversations never leave the device. |

## Built With

- Llama 3.2 3B Instruct (Q4_K_M)
- llama.cpp
- Tauri (Rust + React)
- TypeScript
- Vite

## License

Built for ADTC 2026.
