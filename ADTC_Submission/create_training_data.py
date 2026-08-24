#!/usr/bin/env python3
"""Create training dataset for SabiCore economic extraction fine-tuning."""

import json

SYSTEM_PROMPT = """You are SabiCore, an offline financial intelligence system for African SMEs.
You extract structured financial data from business messages.

RULES:
- "X owes me Y" → X is the customer, type = receivable (they owe YOU money)
- "I owe X Y" or "I need to pay X Y" → X is the customer, type = payable (YOU owe them)
- "X paid me Y" → X is the customer, type = receivable, status = paid
- "I paid X Y" → X is the customer, type = payable, status = paid

Output ONLY valid JSON with these keys. No extra text, no explanation:
{"customer": "name", "amount": "number", "type": "receivable or payable", "status": "outstanding or paid"}
"""

# Training examples: 10 per language across 5 languages
TRAINING_DATA = [
    # ===== ENGLISH =====
    {"language": "English", "input": "Chinedu owes me 85,000 naira for the last delivery.", "output": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
    {"language": "English", "input": "Mama Adura paid 20,000 naira yesterday. Her debt is settled.", "output": {"customer": "Mama Adura", "amount": "20000", "type": "receivable", "status": "paid"}},
    {"language": "English", "input": "I need to pay Alhaji Bello 250,000 for 50 bags of rice.", "output": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
    {"language": "English", "input": "Uncle Emeka still owes 45,000 from last month's supply.", "output": {"customer": "Uncle Emeka", "amount": "45000", "type": "receivable", "status": "outstanding"}},
    {"language": "English", "input": "I sent 50,000 to Mama Nkechi via bank transfer.", "output": {"customer": "Mama Nkechi", "amount": "50000", "type": "payable", "status": "paid"}},
    {"language": "English", "input": "Chinedu's balance is still 120,000 naira outstanding.", "output": {"customer": "Chinedu", "amount": "120000", "type": "receivable", "status": "outstanding"}},
    {"language": "English", "input": "Alhaji Bello delivered 100 bags, I owe him 500,000.", "output": {"customer": "Alhaji Bello", "amount": "500000", "type": "payable", "status": "outstanding"}},
    {"language": "English", "input": "Mama Nkechi settled her 35,000 debt in full.", "output": {"customer": "Mama Nkechi", "amount": "35000", "type": "receivable", "status": "paid"}},
    {"language": "English", "input": "I owe Chinedu 15,000 change from last transaction.", "output": {"customer": "Chinedu", "amount": "15000", "type": "payable", "status": "outstanding"}},
    {"language": "English", "input": "Uncle Emeka paid 200,000 for the December supply.", "output": {"customer": "Uncle Emeka", "amount": "200000", "type": "receivable", "status": "paid"}},

    # ===== NIGERIAN PIDGIN =====
    {"language": "Nigerian Pidgin", "input": "Chinedu still dey owe me 85k for that delivery.", "output": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
    {"language": "Nigerian Pidgin", "input": "Mama Adura don pay her 20k. Her own don finish.", "output": {"customer": "Mama Adura", "amount": "20000", "type": "receivable", "status": "paid"}},
    {"language": "Nigerian Pidgin", "input": "I wan pay Alhaji Bello 250k for 50 bags of rice.", "output": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
    {"language": "Nigerian Pidgin", "input": "Uncle Emeka still owe me 45k from last month.", "output": {"customer": "Uncle Emeka", "amount": "45000", "type": "receivable", "status": "outstanding"}},
    {"language": "Nigerian Pidgin", "input": "I don send 50k to Mama Nkechi through bank.", "output": {"customer": "Mama Nkechi", "amount": "50000", "type": "payable", "status": "paid"}},
    {"language": "Nigerian Pidgin", "input": "Chinedu balance still dey 120k, e never pay.", "output": {"customer": "Chinedu", "amount": "120000", "type": "receivable", "status": "outstanding"}},
    {"language": "Nigerian Pidgin", "input": "Alhaji Bello bring 100 bags, I owe am 500k.", "output": {"customer": "Alhaji Bello", "amount": "500000", "type": "payable", "status": "outstanding"}},
    {"language": "Nigerian Pidgin", "input": "Mama Nkechi don settle the 35k wey she owe me.", "output": {"customer": "Mama Nkechi", "amount": "35000", "type": "receivable", "status": "paid"}},
    {"language": "Nigerian Pidgin", "input": "I still dey owe Chinedu 15k change from last time.", "output": {"customer": "Chinedu", "amount": "15000", "type": "payable", "status": "outstanding"}},
    {"language": "Nigerian Pidgin", "input": "Uncle Emeka don pay 200k for the December supply.", "output": {"customer": "Uncle Emeka", "amount": "200000", "type": "receivable", "status": "paid"}},

    # ===== YORUBA =====
    {"language": "Yoruba", "input": "Chinedu ò sí ìde ọ̀kẹ̀ àádọ́ta-àádọ́ta fún ìrán àṣàyàn.", "output": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
    {"language": "Yoruba", "input": "Mama Adura ti san ọ̀kẹ̀ àádọ́ta lánà. Ó ti parí.", "output": {"customer": "Mama Adura", "amount": "20000", "type": "receivable", "status": "paid"}},
    {"language": "Yoruba", "input": "Mo nilòóò sí Alhaji Bello ọ̀kẹ̀ àádọ́ta-àádọ́ta-àádọ́ta fún bága ìrísì.", "output": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
    {"language": "Yoruba", "input": "Bàbá Emeka kò sí ìde ọ̀kẹ̀ àádọ́ta-àádọ́ta fún oṣù kanna.", "output": {"customer": "Bàbá Emeka", "amount": "45000", "type": "receivable", "status": "outstanding"}},
    {"language": "Yoruba", "input": "Mo rán ọ̀kẹ̀ àádọ́ta sí Mama Nkechi nípasẹ̀ bánkì.", "output": {"customer": "Mama Nkechi", "amount": "50000", "type": "payable", "status": "paid"}},
    {"language": "Yoruba", "input": "Ìwọ̀jọ́ Chinedu jẹ́ ọ̀kẹ̀ àádọ́ta-àádọ́ta-àádọ́ta àádọ́ta.", "output": {"customer": "Chinedu", "amount": "120000", "type": "receivable", "status": "outstanding"}},
    {"language": "Yoruba", "input": "Alhaji Bello mú ọ̀kẹ̀ àádọ́ta-àádọ́ta-àádọ́ta-àádọ́ta sí mi.", "output": {"customer": "Alhaji Bello", "amount": "500000", "type": "payable", "status": "outstanding"}},
    {"language": "Yoruba", "input": "Mama Nkechi ti parí ọ̀kẹ̀ àádọ́ta-àádọ́ta tí ó jẹ́.", "output": {"customer": "Mama Nkechi", "amount": "35000", "type": "receivable", "status": "paid"}},
    {"language": "Yoruba", "input": "Mo ò sí ìde ọ̀kẹ̀ àádọ́ta fún Chinedu.", "output": {"customer": "Chinedu", "amount": "15000", "type": "payable", "status": "outstanding"}},
    {"language": "Yoruba", "input": "Bàbá Emeka ti san ọ̀kẹ̀ àádọ́ta-àádọ́ta fún ìrán kẹ̀ẹ̀dọ́gún.", "output": {"customer": "Bàbá Emeka", "amount": "200000", "type": "receivable", "status": "paid"}},

    # ===== IGBO =====
    {"language": "Igbo", "input": "Chinedu adịghị ya ihe ọ̀nụ alafa indè abụọ na ise nke ntinye ego.", "output": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
    {"language": "Igbo", "input": "Mama Adura agụzịrị aka ọ̀nụ alafa indè. Emeela.", "output": {"customer": "Mama Adura", "amount": "20000", "type": "receivable", "status": "paid"}},
    {"language": "Igbo", "input": "A chọrọ m ka m tinye ego Alhaji Bello ọ̀nụ alafa indè abụọ na ise maka rice.", "output": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
    {"language": "Igbo", "input": "Nna Emeka ka nọ na ọ̀nụ alafa abụọ na ise nke ọnwa gara aga.", "output": {"customer": "Nna Emeka", "amount": "45000", "type": "receivable", "status": "outstanding"}},
    {"language": "Igbo", "input": "Ezitere m ọ̀nụ alafa indè Mama Nkechi site na banị.", "output": {"customer": "Mama Nkechi", "amount": "50000", "type": "payable", "status": "paid"}},
    {"language": "Igbo", "input": "Chinedu ka nọ na ọ̀nụ alafa indè abụọ na ise.", "output": {"customer": "Chinedu", "amount": "120000", "type": "receivable", "status": "outstanding"}},
    {"language": "Igbo", "input": "Alhaji Bello were ego ọ̀nụ alafa indè abụọ na ise na ise.", "output": {"customer": "Alhaji Bello", "amount": "500000", "type": "payable", "status": "outstanding"}},
    {"language": "Igbo", "input": "Mama Nkechi agụzịrị aka ọ̀nụ alafa abụọ na ise.", "output": {"customer": "Mama Nkechi", "amount": "35000", "type": "receivable", "status": "paid"}},
    {"language": "Igbo", "input": "A na m debi ego Chinedu ọ̀nụ alafa ise.", "output": {"customer": "Chinedu", "amount": "15000", "type": "payable", "status": "outstanding"}},
    {"language": "Igbo", "input": "Nna Emeka agụzịrị aka ọ̀nụ alafa abụọ na ise.", "output": {"customer": "Nna Emeka", "amount": "200000", "type": "receivable", "status": "paid"}},

    # ===== HAUSA =====
    {"language": "Hausa", "input": "Chinedu bai biya kuɗin kaya guda 85 ba.", "output": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
    {"language": "Hausa", "input": "Mama Adura ta biya kuɗinta na 20 wata jiya. An gama.", "output": {"customer": "Mama Adura", "amount": "20000", "type": "receivable", "status": "paid"}},
    {"language": "Hausa", "input": "Ina bukatar biya Alhaji Bello kuɗi 250 don Quantity 50 na shinkafa.", "output": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
    {"language": "Hausa", "input": "Uncle Emeka har yanzu yana da bil 45 na wata baya.", "output": {"customer": "Uncle Emeka", "amount": "45000", "type": "receivable", "status": "outstanding"}},
    {"language": "Hausa", "input": "Na aika 50 zuwa Mama Nkechi ta hanyar banki.", "output": {"customer": "Mama Nkechi", "amount": "50000", "type": "payable", "status": "paid"}},
    {"language": "Hausa", "input": "Chinedu har yanzu yana da kuɗi 120.", "output": {"customer": "Chinedu", "amount": "120000", "type": "receivable", "status": "outstanding"}},
    {"language": "Hausa", "input": "Alhaji Bello ya kawo kaya 100, ina biyansa 500.", "output": {"customer": "Alhaji Bello", "amount": "500000", "type": "payable", "status": "outstanding"}},
    {"language": "Hausa", "input": "Mama Adura ta biya kuɗinta na 35.", "output": {"customer": "Mama Adura", "amount": "35000", "type": "receivable", "status": "paid"}},
    {"language": "Hausa", "input": "Ina biyan Chinedu kuɗi 15 na canjin.", "output": {"customer": "Chinedu", "amount": "15000", "type": "payable", "status": "outstanding"}},
    {"language": "Hausa", "input": "Uncle Emeka ya biya 200 don kayan Disamba.", "output": {"customer": "Uncle Emeka", "amount": "200000", "type": "receivable", "status": "paid"}},

    # ===== CODE-SWITCHED (mixed English/Pidgin) =====
    {"language": "Code-switched", "input": "Chinedu never balance the 85k, he go pay after market day.", "output": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
    {"language": "Code-switched", "input": "Mama Adura don settle the 20k wey she owe me from last month.", "output": {"customer": "Mama Adura", "amount": "20000", "type": "receivable", "status": "paid"}},
    {"language": "Code-switched", "input": "I need to pay Alhaji Bello the 250k for rice, he don deliver.", "output": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
    {"language": "Code-switched", "input": "Uncle Emeka still dey owe me 45k, e say e go pay next week.", "output": {"customer": "Uncle Emeka", "amount": "45000", "type": "receivable", "status": "outstanding"}},
    {"language": "Code-switched", "input": "I don send the 50k to Mama Nkechi through her GTBank account.", "output": {"customer": "Mama Nkechi", "amount": "50000", "type": "payable", "status": "paid"}},
]


def format_conversation(example):
    """Format as chat template for Llama 3.2."""
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": example["input"]},
            {"role": "assistant", "content": json.dumps(example["output"])}
        ]
    }


def main():
    dataset = [format_conversation(ex) for ex in TRAINING_DATA]

    with open("training_dataset.jsonl", "w") as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")

    print(f"Created {len(dataset)} training examples")
    print(f"Languages: {set(ex['language'] for ex in TRAINING_DATA)}")
    print(f"Saved to training_dataset.jsonl")

    # Also save the raw data for reference
    with open("training_data_raw.json", "w") as f:
        json.dump(TRAINING_DATA, f, indent=2)


if __name__ == "__main__":
    main()
