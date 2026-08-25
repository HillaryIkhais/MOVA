#!/usr/bin/env python3
"""MOVA Language Benchmark — Tests economic extraction across 5 Nigerian languages."""

import json
import subprocess
import time
import re

SERVER_URL = "http://127.0.0.1:8084/completion"

SYSTEM_PROMPT = """You are MOVA, an offline financial intelligence system for African SMEs.
You extract structured financial data from business messages.
Always respond with EXACTLY these fields and nothing else:
customer: [name]
amount: [amount]
type: [receivable/payable]
status: [outstanding/paid/disputed]
due: [date or "not specified"]
"""

# Test cases: same economic event, different languages
TEST_CASES = {
    "English": [
        {"input": "Chinedu owes me 85,000 naira for the last delivery.", "expected": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
        {"input": "Mama Adura paid 20,000 naira yesterday. Her debt is settled.", "expected": {"customer": "Mama Adura", "amount": "20000", "type": "receivable", "status": "paid"}},
        {"input": "I need to pay Alhaji Bello 250,000 for 50 bags of rice.", "expected": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
        {"input": "Chinedu sent 50,000 via OPay. Reference 20260817001.", "expected": {"customer": "Chinedu", "amount": "50000", "type": "receivable", "status": "paid"}},
        {"input": "Uncle Emeka still owes 45k from last month's supply.", "expected": {"customer": "Uncle Emeka", "amount": "45000", "type": "receivable", "status": "outstanding"}},
    ],
    "Nigerian Pidgin": [
        {"input": "Chinedu still dey owe me 85k for that delivery.", "expected": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
        {"input": "Mama Adura don pay her 20k. Her own don finish.", "expected": {"customer": "Mama Adura", "amount": "20000", "type": "receivable", "status": "paid"}},
        {"input": "I wan pay Alhaji Bello 250k for 50 bags of rice.", "expected": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
        {"input": "Chinedu don send 50k via OPay.", "expected": {"customer": "Chinedu", "amount": "50000", "type": "receivable", "status": "paid"}},
        {"input": "Uncle Emeka still owe me 45k from last month.", "expected": {"customer": "Uncle Emeka", "amount": "45000", "type": "receivable", "status": "outstanding"}},
    ],
    "Yoruba": [
        {"input": "Chinedu ò sí ìde ọ̀kẹ̀ àádọ́ta-àádọ́ta fún ìrán àṣàyàn.", "expected": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
        {"input": "Mama Adura ti san ọ̀kẹ̀ àádọ́ta lánà. Ó ti parí.", "expected": {"customer": "Mama Adura", "amount": "20000", "type": "receivable", "status": "paid"}},
        {"input": "Mo nilòóò sí Alhaji Bello ọ̀kẹ̀ àádọ́ta-àádọ́ta-àádọ́ta fún bága ìrísì.", "expected": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
        {"input": "Chinedu ti rán ọ̀kẹ̀ àádọ́ta nípasẹ̀ OPay.", "expected": {"customer": "Chinedu", "amount": "50000", "type": "receivable", "status": "paid"}},
        {"input": "Bàbá Emeka kò sí ìde ọ̀kẹ̀ àádọ́ta-àádọ́ta fún oṣù kanna.", "expected": {"customer": "Bàbá Emeka", "amount": "45000", "type": "receivable", "status": "outstanding"}},
    ],
    "Igbo": [
        {"input": "Chinedu adịghị ya ihe ọ̀nụ alafa indè abụọ na ise nke ntinye ego.", "expected": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
        {"input": "Mama Adura agụzịrị aka ọ̀nụ alafa indè. Emeela.", "expected": {"customer": "Mama Adura", "amount": "20000", "type": "receivable", "status": "paid"}},
        {"input": "A chọrọ m ka m tinye ego Alhaji Bello ọ̀nụ alafa indè abụọ na ise maka rice.", "expected": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
        {"input": "Chinedu ezitere ọ̀nụ alafa indè site na OPay.", "expected": {"customer": "Chinedu", "amount": "50000", "type": "receivable", "status": "paid"}},
        {"input": "Nna Emeka ka nọ na ọ̀nụ alafa abụọ na ise nke ọnwa gara aga.", "expected": {"customer": "Nna Emeka", "amount": "45000", "type": "receivable", "status": "outstanding"}},
    ],
    "Hausa": [
        {"input": "Chinedu bai biya kuɗin kaya guda 85 ba.", "expected": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
        {"input": "Mama Adura ta biya kuɗinta na 20 wata jiya. An gama.", "expected": {"customer": "Mama Adura", "amount": "20000", "type": "receivable", "status": "paid"}},
        {"input": "Ina bukatar biya Alhaji Bello kuɗi 250 donQuantity 50 na shinkafa.", "expected": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
        {"input": "Chinedu ya aika kuɗi 50 ta hanyar OPay.", "expected": {"customer": "Chinedu", "amount": "50000", "type": "receivable", "status": "paid"}},
        {"input": "Uncle Emeka har yanzu yana da bil 45 na wata baya.", "expected": {"customer": "Uncle Emeka", "amount": "45000", "type": "receivable", "status": "outstanding"}},
    ],
}


def query_model(prompt: str) -> str:
    """Query the llama-server and return the response."""
    payload = json.dumps({
        "prompt": prompt,
        "n_predict": 256,
        "temperature": 0.1,
    })
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "30", SERVER_URL, "-d", payload],
            capture_output=True, text=True, timeout=35
        )
        data = json.loads(result.stdout)
        return data.get("content", "")
    except Exception as e:
        return f"ERROR: {e}"


def extract_fields(response: str) -> dict:
    """Extract structured fields from model response."""
    fields = {}
    for line in response.split("\n"):
        line = line.strip().lower()
        if "customer:" in line:
            fields["customer"] = line.split("customer:")[-1].strip()
        elif "amount:" in line:
            amt = line.split("amount:")[-1].strip()
            amt = re.sub(r"[^\d]", "", amt)
            fields["amount"] = amt
        elif "type:" in line:
            t = line.split("type:")[-1].strip()
            fields["type"] = "receivable" if "rec" in t else "payable" if "pay" in t else t
        elif "status:" in line:
            s = line.split("status:")[-1].strip()
            if "paid" in s or "settled" in s or "done" in s:
                fields["status"] = "paid"
            elif "outstanding" in s or "unpaid" in s or "pending" in s or "owes" in s:
                fields["status"] = "outstanding"
            else:
                fields["status"] = s
        elif "due:" in line:
            fields["due"] = line.split("due:")[-1].strip()
    return fields


def score_match(expected: dict, actual: dict) -> dict:
    """Score how well the actual extraction matches expected."""
    scores = {}
    for key in ["customer", "amount", "type", "status"]:
        exp_val = expected.get(key, "").lower()
        act_val = actual.get(key, "").lower()
        if key == "amount":
            scores[key] = exp_val == act_val
        elif key in ("type", "status"):
            scores[key] = exp_val in act_val or act_val in exp_val
        else:
            scores[key] = exp_val in act_val or act_val in exp_val
    return scores


def main():
    print("=" * 60)
    print("MOVA Language Benchmark — Economic Extraction")
    print("=" * 60)

    results = {}

    for lang, tests in TEST_CASES.items():
        print(f"\n--- {lang} ({len(tests)} tests) ---")
        lang_scores = []

        for i, test in enumerate(tests):
            prompt = f"{SYSTEM_PROMPT}\n\nUser: {test['input']}\n\n### Response:\n"
            print(f"  Test {i+1}: {test['input'][:50]}...", end=" ")
            response = query_model(prompt)
            actual = extract_fields(response)
            scores = score_match(test["expected"], actual)

            correct = sum(scores.values())
            total = len(scores)
            lang_scores.append(correct / total)

            status = "PASS" if correct == total else f"PARTIAL ({correct}/{total})"
            print(status)

        avg = sum(lang_scores) / len(lang_scores) if lang_scores else 0
        results[lang] = {"accuracy": avg, "tests": len(tests), "per_test": lang_scores}
        print(f"  → {lang} accuracy: {avg:.0%} ({sum(1 for s in lang_scores if s == 1.0)}/{len(tests)} perfect)")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    overall_correct = 0
    overall_total = 0
    for lang, r in results.items():
        perfect = sum(1 for s in r["per_test"] if s == 1.0)
        print(f"  {lang:20s} {r['accuracy']:.0%}  ({perfect}/{r['tests']} perfect)")
        overall_correct += perfect
        overall_total += r["tests"]
    overall = overall_correct / overall_total if overall_total else 0
    print(f"\n  OVERALL:            {overall:.0%}  ({overall_correct}/{overall_total} perfect)")

    # Save results
    with open("language_benchmark.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to language_benchmark.json")


if __name__ == "__main__":
    main()
