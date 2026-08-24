# SabiCore Elite — ADTC Submission Report

## Problem

African SME economic activity is highly conversational and fragmented. A huge amount of commerce happens through WhatsApp conversations, SMS notifications, mobile money alerts, bank transfers, informal credit arrangements, and Pidgin/local language exchanges. The economic information exists — it's just trapped inside conversations and fragmented notifications.

Cloud-based AI tools require API fees, stable fiber, and sustained electricity. For a shop owner in Lagos, a market trader in Arusha, or a supplier in Dakar, these are not minor frictions — they are blockers. Sensitive business conversations sent to cloud APIs also raise privacy concerns for credit tracking and debt management.

## Solution

SabiCore Elite is an **offline financial intelligence layer** that converts the messy communication African businesses already use into structured business records and actions.

It does not try to be a chatbot or a QuickBooks clone. It does one thing well:

**Conversation → Understand → Structure → Remember → Act**

The core loop:
1. Receives messy business communication (WhatsApp, SMS, Pidgin, local languages)
2. Understands intent and economic meaning (not just keywords)
3. Structures it into financial state (who owes whom, how much, why, when)
4. Tracks the informal credit economy locally (debts, payments, remaining balances, due dates)
5. Generates actionable reminders and summaries — all offline

This is not "AI bookkeeping." This is turning informal economic activity into machine-readable financial intelligence.

## Why This Needs an LLM

A regex parser can extract "N50,000 from CHINEDU OKAFOR" from a structured SMS. It cannot handle:

> "Abeg remind me say Chinedu still owe me 45k from the last delivery. He said he'll pay after market day. And also Mama Adura don pay the remaining 20k wey she owe me from last month. So her own don finish."

This is how African SMEs actually communicate — mixed Pidgin/English, implicit context, multiple transactions in one message, cultural time references ("after market day"), and incomplete information.

The LLM does four things a parser cannot:

1. **Understands intent** — "abeg remind" = create a reminder, not just log text
2. **Resolves ambiguity** — "45k" = ₦45,000, "after market day" = due date
3. **Tracks credit state** — recognizes "Mama Adura don pay" = debt settled, updates ledger
4. **Takes action** — generates structured records with customer, amount, type, context, and status

### Demo Case: Multi-Turn Credit Tracking

**Input (WhatsApp conversation):**
```
[12/08/2026, 09:15] Mama Nkechi: Chinedu, the 20 bags of rice I supply you yesterday, you never pay the balance.
[12/08/2026, 09:20] Chinedu: Ah Mama no vex. I go balance you the remaining N150,000 next market day.
[15/08/2026, 14:00] Chinedu: Mama I don send N50,000 via OPay. Check your phone.
[15/08/2026, 14:05] Mama Nkechi: I don see am. So you still owe me N100,000.
[15/08/2026, 14:10] Chinedu: Yes Mama. I go pay the remaining before end of week.
```

**Model Output:**
```
Creditor: Mama Nkechi
Debtor: Chinedu
Original Amount: ₦150,000
Payments Made: ₦50,000 (via OPay, 15/08/2026)
Remaining Balance: ₦100,000
Due Terms: Before end of week
Current Status: Active — partial payment received, remainder pending
```

This is not text extraction. This is understanding an informal credit relationship across multiple messages and tracking its full lifecycle — locally, offline, in Pidgin.

## Design Decisions

| Decision | Rationale |
|---|---|
| **Llama-3.2-3B (Q4_K_M)** | Right size for 8GB laptops. 3.2B parameters confirmed by GGUF header. Instruction-tuned for structured extraction. Fits the ADTC thesis: small models optimized for the actual economic language of the user. |
| **Tauri (Rust + React)** | Native desktop app with small binary size. Rust backend for memory safety. |
| **llama.cpp server** | Battle-tested local inference engine. HTTP API for frontend communication. |
| **Q4_K_M quantization** | Optimal quality-to-size ratio. 2.02 GB on disk. |
| **Offline-first architecture** | Entire financial intelligence layer runs without internet. Sensitive business conversations never leave the device. |

## Constraints

- **Model size**: Must fit in RAM on a participant laptop (8GB+). Measured peak RSS: 3,217 MB.
- **No internet required**: Model downloads are one-time; all inference is local.
- **No GPU required**: llama.cpp runs on CPU fallback, though GPU acceleration (Metal/CUDA) is supported when available.
- **Accuracy vs. speed tradeoff**: A 3B model doesn't need to be a brilliant general-purpose reasoner. It needs to be excellent at one constrained task: converting messy real-world SME communication into structured business actions.

## Benchmarks — Measured via ADTC Profiler

All numbers measured by `adtc-profiler run --mode participant --output submission.json` on development hardware.

### Environment

| Component | Value |
|---|---|
| CPU | Apple M3 |
| RAM | 16 GB |
| GPU | Integrated (Metal available) |
| OS | macOS 26.5.2 arm64 |
| Measured on | participant_laptop |

### Profiler Results

| Metric | Measured Value |
|---|---|
| **Throughput** | 10.72 tokens/sec |
| **First token latency** | 10,996 ms |
| **Peak RSS** | 3,217 MB |
| **Steady-state RSS** | 3,090 MB |
| **Accuracy (arc_easy)** | 72% |
| **CPU utilization (p99)** | 72.4% |
| **Thermal throttling** | No |
| **Parameter count** | 3,212,749,888 (confirmed) |
| **Params match claim** | True |

### ADTC Scoring

| Component | Weight | Score |
|---|---|---|
| **S_ACC** (Accuracy) | 50% | 72.0 |
| **S_PERF** (Throughput) | 30% | 71.5 |
| **S_EFF** (Efficiency) | 20% | 54.0 |
| **P_THERMAL** | — | 0 (no penalty) |

**Estimated total: 68.2 / 100** (before African Use Case bonus)

### Note on Hardware

The ADTC reference hardware is an Intel Core i5 10th-12th gen, 8 GB DDR4, integrated graphics. Our development hardware is Apple M3. The profiler's `llama-bench` runs CPU-only on both platforms. Published benchmarks for similar 3B Q4_K_M models on Intel i5 hardware show comparable throughput ranges (10-12 t/s). Our measured numbers are within the expected performance envelope for this model class.

## How to Run

```bash
# 1. Download the model (~2 GB, one-time)
bash download_model.sh

# 2. Run the full application
bash run_demo.sh
```

The app launches at `http://localhost:5173` with the llama.cpp inference server running on port 8080.

## Files

```
ADTC_Submission/
├── metadata.json          # Submission metadata
├── download_model.sh      # Downloads the GGUF model
├── REPORT.md              # This file
├── run_demo.sh            # Launches server + Tauri app
├── .gitignore             # Excludes model/ and *.gguf
├── model/                 # Created by download_model.sh (not in git)
└── SabiTrade_App/         # Tauri application source
    ├── src/               # React frontend
    ├── src-tauri/         # Rust backend
    └── ...
```
