#!/usr/bin/env python3
"""
MOVA Nigerian Economic Benchmark — 150 examples
40% English, 40% Pidgin, 20% Messy/Ambiguous

Measures: entity accuracy, amount accuracy, direction accuracy, status accuracy, full-record accuracy
"""

import json
import subprocess
import re
import time
from collections import defaultdict

SERVER_URL = "http://127.0.0.1:8084/completion"

# ============================================================
# BENCHMARK DATA — 150 examples
# ============================================================

BENCHMARK = [
    # ===== ENGLISH (60 examples) =====

    # --- Simple receivables ---
    {"lang": "English", "cat": "receivable_simple", "input": "Chinedu owes me 85,000 naira for the last delivery.", "expected": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
    {"lang": "English", "cat": "receivable_simple", "input": "Mama Nkechi still owes 45,000 from the rice supply.", "expected": {"customer": "Mama Nkechi", "amount": "45000", "type": "receivable", "status": "outstanding"}},
    {"lang": "English", "cat": "receivable_simple", "input": "Uncle Emeka is owing me 120,000 for yam delivery.", "expected": {"customer": "Uncle Emeka", "amount": "120000", "type": "receivable", "status": "outstanding"}},
    {"lang": "English", "cat": "receivable_simple", "input": "Alhaji Bello's balance is 250,000 naira outstanding.", "expected": {"customer": "Alhaji Bello", "amount": "250000", "type": "receivable", "status": "outstanding"}},
    {"lang": "English", "cat": "receivable_simple", "input": "Chidinma still has 35,000 pending from last week.", "expected": {"customer": "Chidinma", "amount": "35000", "type": "receivable", "status": "outstanding"}},
    {"lang": "English", "cat": "receivable_simple", "input": "Igwe owes me 90,000 for the December stock.", "expected": {"customer": "Igwe", "amount": "90000", "type": "receivable", "status": "outstanding"}},
    {"lang": "English", "cat": "receivable_simple", "input": "Ngozi still has an outstanding balance of 55,000.", "expected": {"customer": "Ngozi", "amount": "55000", "type": "receivable", "status": "outstanding"}},
    {"lang": "English", "cat": "receivable_simple", "input": "Emeka is yet to pay the 75,000 he owes.", "expected": {"customer": "Emeka", "amount": "75000", "type": "receivable", "status": "outstanding"}},
    {"lang": "English", "cat": "receivable_simple", "input": "Chinedu's debt of 40,000 is still pending.", "expected": {"customer": "Chinedu", "amount": "40000", "type": "receivable", "status": "outstanding"}},
    {"lang": "English", "cat": "receivable_simple", "input": "Amina owes 65,000 for the fabric supply.", "expected": {"customer": "Amina", "amount": "65000", "type": "receivable", "status": "outstanding"}},

    # --- Simple payables ---
    {"lang": "English", "cat": "payable_simple", "input": "I need to pay Alhaji Bello 250,000 for 50 bags of rice.", "expected": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
    {"lang": "English", "cat": "payable_simple", "input": "I owe Mama Nkechi 80,000 for the palm oil supply.", "expected": {"customer": "Mama Nkechi", "amount": "80000", "type": "payable", "status": "outstanding"}},
    {"lang": "English", "cat": "payable_simple", "input": "I still need to pay Chinedu 15,000 change.", "expected": {"customer": "Chinedu", "amount": "15000", "type": "payable", "status": "outstanding"}},
    {"lang": "English", "cat": "payable_simple", "input": "We owe Alhaji Ibrahim 300,000 for cement.", "expected": {"customer": "Alhaji Ibrahim", "amount": "300000", "type": "payable", "status": "outstanding"}},
    {"lang": "English", "cat": "payable_simple", "input": "I need to settle Uncle Emeka's 50,000 balance.", "expected": {"customer": "Uncle Emeka", "amount": "50000", "type": "payable", "status": "outstanding"}},
    {"lang": "English", "cat": "payable_simple", "input": "I owe Chief Okafor 175,000 for the building materials.", "expected": {"customer": "Chief Okafor", "amount": "175000", "type": "payable", "status": "outstanding"}},
    {"lang": "English", "cat": "payable_simple", "input": "My balance with Alhaji Musa is 95,000.", "expected": {"customer": "Alhaji Musa", "amount": "95000", "type": "payable", "status": "outstanding"}},
    {"lang": "English", "cat": "payable_simple", "input": "I still owe Mama Adura 42,000 for beans.", "expected": {"customer": "Mama Adura", "amount": "42000", "type": "payable", "status": "outstanding"}},
    {"lang": "English", "cat": "payable_simple", "input": "I need to pay Chidinma 28,000 for the wrappers.", "expected": {"customer": "Chidinma", "amount": "28000", "type": "payable", "status": "outstanding"}},
    {"lang": "English", "cat": "payable_simple", "input": "We have 60,000 outstanding with Alhaji Bello.", "expected": {"customer": "Alhaji Bello", "amount": "60000", "type": "payable", "status": "outstanding"}},

    # --- Paid receivables ---
    {"lang": "English", "cat": "receivable_paid", "input": "Mama Adura paid 20,000 naira yesterday. Her debt is settled.", "expected": {"customer": "Mama Adura", "amount": "20000", "type": "receivable", "status": "paid"}},
    {"lang": "English", "cat": "receivable_paid", "input": "Chinedu sent 50,000 via OPay. Reference 20260817001.", "expected": {"customer": "Chinedu", "amount": "50000", "type": "receivable", "status": "paid"}},
    {"lang": "English", "cat": "receivable_paid", "input": "Uncle Emeka paid 200,000 for the December supply.", "expected": {"customer": "Uncle Emeka", "amount": "200000", "type": "receivable", "status": "paid"}},
    {"lang": "English", "cat": "receivable_paid", "input": "Mama Nkechi settled her 35,000 debt in full.", "expected": {"customer": "Mama Nkechi", "amount": "35000", "type": "receivable", "status": "paid"}},
    {"lang": "English", "cat": "receivable_paid", "input": "Ngozi has cleared her 65,000 balance.", "expected": {"customer": "Ngozi", "amount": "65000", "type": "receivable", "status": "paid"}},
    {"lang": "English", "cat": "receivable_paid", "input": "I received 45,000 from Alhaji Ibrahim. All settled.", "expected": {"customer": "Alhaji Ibrahim", "amount": "45000", "type": "receivable", "status": "paid"}},
    {"lang": "English", "cat": "receivable_paid", "input": "Chidinma paid 80,000 yesterday. Her account is clear.", "expected": {"customer": "Chidinma", "amount": "80000", "type": "receivable", "status": "paid"}},
    {"lang": "English", "cat": "receivable_paid", "input": "Emeka settled the 90,000 he owed from January.", "expected": {"customer": "Emeka", "amount": "90000", "type": "receivable", "status": "paid"}},
    {"lang": "English", "cat": "receivable_paid", "input": "Amina sent 55,000 via bank transfer. Done.", "expected": {"customer": "Amina", "amount": "55000", "type": "receivable", "status": "paid"}},
    {"lang": "English", "cat": "receivable_paid", "input": "Chinedu has paid 100,000. Balance is now zero.", "expected": {"customer": "Chinedu", "amount": "100000", "type": "receivable", "status": "paid"}},

    # --- Paid payables ---
    {"lang": "English", "cat": "payable_paid", "input": "I sent 250,000 to Alhaji Bello for the rice.", "expected": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "paid"}},
    {"lang": "English", "cat": "payable_paid", "input": "I paid Mama Nkechi 80,000 for palm oil.", "expected": {"customer": "Mama Nkechi", "amount": "80000", "type": "payable", "status": "paid"}},
    {"lang": "English", "cat": "payable_paid", "input": "Transferred 15,000 to Chinedu for the change.", "expected": {"customer": "Chinedu", "amount": "15000", "type": "payable", "status": "paid"}},
    {"lang": "English", "cat": "payable_paid", "input": "I settled Alhaji Ibrahim's 300,000 today.", "expected": {"customer": "Alhaji Ibrahim", "amount": "300000", "type": "payable", "status": "paid"}},
    {"lang": "English", "cat": "payable_paid", "input": "Paid Uncle Emeka 50,000 via bank transfer.", "expected": {"customer": "Uncle Emeka", "amount": "50000", "type": "payable", "status": "paid"}},
    {"lang": "English", "cat": "payable_paid", "input": "I've cleared Chief Okafor's 175,000.", "expected": {"customer": "Chief Okafor", "amount": "175000", "type": "payable", "status": "paid"}},
    {"lang": "English", "cat": "payable_paid", "input": "Sent 95,000 to Alhaji Musa. We're even.", "expected": {"customer": "Alhaji Musa", "amount": "95000", "type": "payable", "status": "paid"}},
    {"lang": "English", "cat": "payable_paid", "input": "I transferred 42,000 to Mama Adura for the beans.", "expected": {"customer": "Mama Adura", "amount": "42000", "type": "payable", "status": "paid"}},
    {"lang": "English", "cat": "payable_paid", "input": "Paid Chidinma 28,000 cash yesterday.", "expected": {"customer": "Chidinma", "amount": "28000", "type": "payable", "status": "paid"}},
    {"lang": "English", "cat": "payable_paid", "input": "Alhaji Bello's 60,000 has been settled.", "expected": {"customer": "Alhaji Bello", "amount": "60000", "type": "payable", "status": "paid"}},

    # --- Amount formats ---
    {"lang": "English", "cat": "amount_format", "input": "Chinedu owes me 85k.", "expected": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
    {"lang": "English", "cat": "amount_format", "input": "I need to pay N250,000 to Alhaji Bello.", "expected": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
    {"lang": "English", "cat": "amount_format", "input": "Mama Nkechi paid N35,000 yesterday.", "expected": {"customer": "Mama Nkechi", "amount": "35000", "type": "receivable", "status": "paid"}},
    {"lang": "English", "cat": "amount_format", "input": "Uncle Emeka owes 45 thousand naira.", "expected": {"customer": "Uncle Emeka", "amount": "45000", "type": "receivable", "status": "outstanding"}},
    {"lang": "English", "cat": "amount_format", "input": "I owe Alhaji Ibrahim 200k.", "expected": {"customer": "Alhaji Ibrahim", "amount": "200000", "type": "payable", "status": "outstanding"}},
    {"lang": "English", "cat": "amount_format", "input": "Chidinma's debt is ₦55,000.", "expected": {"customer": "Chidinma", "amount": "55000", "type": "receivable", "status": "outstanding"}},
    {"lang": "English", "cat": "amount_format", "input": "I paid 150k to Chief Okafor.", "expected": {"customer": "Chief Okafor", "amount": "150000", "type": "payable", "status": "paid"}},
    {"lang": "English", "cat": "amount_format", "input": "Ngozi owes me N65,000 for fabric.", "expected": {"customer": "Ngozi", "amount": "65000", "type": "receivable", "status": "outstanding"}},
    {"lang": "English", "cat": "amount_format", "input": "Alhaji Musa is owed 95,000.", "expected": {"customer": "Alhaji Musa", "amount": "95000", "type": "payable", "status": "outstanding"}},
    {"lang": "English", "cat": "amount_format", "input": "Emeka sent N90,000. Done.", "expected": {"customer": "Emeka", "amount": "90000", "type": "receivable", "status": "paid"}},

    # ===== NIGERIAN PIDGIN (60 examples) =====

    # --- Simple receivables ---
    {"lang": "Pidgin", "cat": "receivable_simple", "input": "Chinedu still dey owe me 85k for that delivery.", "expected": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "receivable_simple", "input": "Mama Nkechi never pay the 45k wey she owe me.", "expected": {"customer": "Mama Nkechi", "amount": "45000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "receivable_simple", "input": "Uncle Emeka still dey owe me 120k for yam.", "expected": {"customer": "Uncle Emeka", "amount": "120000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "receivable_simple", "input": "Alhaji Bello balance still dey 250k.", "expected": {"customer": "Alhaji Bello", "amount": "250000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "receivable_simple", "input": "Chidinma owe me 35k from last week.", "expected": {"customer": "Chidinma", "amount": "35000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "receivable_simple", "input": "Igwe still dey owe 90k for December stock.", "expected": {"customer": "Igwe", "amount": "90000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "receivable_simple", "input": "Ngozi balance still dey 55k.", "expected": {"customer": "Ngozi", "amount": "55000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "receivable_simple", "input": "Emeka never pay the 75k wey e owe.", "expected": {"customer": "Emeka", "amount": "75000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "receivable_simple", "input": "Chinedu 40k still dey pending.", "expected": {"customer": "Chinedu", "amount": "40000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "receivable_simple", "input": "Amina still dey owe me 65k for fabric.", "expected": {"customer": "Amina", "amount": "65000", "type": "receivable", "status": "outstanding"}},

    # --- Simple payables ---
    {"lang": "Pidgin", "cat": "payable_simple", "input": "I wan pay Alhaji Bello 250k for 50 bags of rice.", "expected": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "payable_simple", "input": "I owe Mama Nkechi 80k for palm oil.", "expected": {"customer": "Mama Nkechi", "amount": "80000", "type": "payable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "payable_simple", "input": "I still dey owe Chinedu 15k change.", "expected": {"customer": "Chinedu", "amount": "15000", "type": "payable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "payable_simple", "input": "We owe Alhaji Ibrahim 300k for cement.", "expected": {"customer": "Alhaji Ibrahim", "amount": "300000", "type": "payable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "payable_simple", "input": "I need settle Uncle Emeka 50k balance.", "expected": {"customer": "Uncle Emeka", "amount": "50000", "type": "payable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "payable_simple", "input": "I owe Chief Okafor 175k for building materials.", "expected": {"customer": "Chief Okafor", "amount": "175000", "type": "payable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "payable_simple", "input": "My balance with Alhaji Musa na 95k.", "expected": {"customer": "Alhaji Musa", "amount": "95000", "type": "payable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "payable_simple", "input": "I still dey owe Mama Adura 42k for beans.", "expected": {"customer": "Mama Adura", "amount": "42000", "type": "payable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "payable_simple", "input": "I need pay Chidinma 28k for wrapper.", "expected": {"customer": "Chidinma", "amount": "28000", "type": "payable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "payable_simple", "input": "We get 60k wey we still dey owe Alhaji Bello.", "expected": {"customer": "Alhaji Bello", "amount": "60000", "type": "payable", "status": "outstanding"}},

    # --- Paid receivables ---
    {"lang": "Pidgin", "cat": "receivable_paid", "input": "Mama Adura don pay her 20k. Her own don finish.", "expected": {"customer": "Mama Adura", "amount": "20000", "type": "receivable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "receivable_paid", "input": "Chinedu don send 50k via OPay.", "expected": {"customer": "Chinedu", "amount": "50000", "type": "receivable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "receivable_paid", "input": "Uncle Emeka don pay 200k for December supply.", "expected": {"customer": "Uncle Emeka", "amount": "200000", "type": "receivable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "receivable_paid", "input": "Mama Nkechi don settle the 35k wey she owe me.", "expected": {"customer": "Mama Nkechi", "amount": "35000", "type": "receivable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "receivable_paid", "input": "Ngozi don clear her 65k balance.", "expected": {"customer": "Ngozi", "amount": "65000", "type": "receivable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "receivable_paid", "input": "I don collect 45k from Alhaji Ibrahim. Done.", "expected": {"customer": "Alhaji Ibrahim", "amount": "45000", "type": "receivable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "receivable_paid", "input": "Chidinma don pay 80k yesterday. Her own clear.", "expected": {"customer": "Chidinma", "amount": "80000", "type": "receivable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "receivable_paid", "input": "Emeka don settle the 90k wey e owe from January.", "expected": {"customer": "Emeka", "amount": "90000", "type": "receivable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "receivable_paid", "input": "Amina don send 55k through bank.", "expected": {"customer": "Amina", "amount": "55000", "type": "receivable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "receivable_paid", "input": "Chinedu don pay 100k. Balance don zero.", "expected": {"customer": "Chinedu", "amount": "100000", "type": "receivable", "status": "paid"}},

    # --- Paid payables ---
    {"lang": "Pidgin", "cat": "payable_paid", "input": "I don send 250k to Alhaji Bello for rice.", "expected": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "payable_paid", "input": "I don pay Mama Nkechi 80k for palm oil.", "expected": {"customer": "Mama Nkechi", "amount": "80000", "type": "payable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "payable_paid", "input": "I don transfer 15k give Chinedu for change.", "expected": {"customer": "Chinedu", "amount": "15000", "type": "payable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "payable_paid", "input": "I don settle Alhaji Ibrahim 300k today.", "expected": {"customer": "Alhaji Ibrahim", "amount": "300000", "type": "payable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "payable_paid", "input": "I don pay Uncle Emeka 50k through bank.", "expected": {"customer": "Uncle Emeka", "amount": "50000", "type": "payable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "payable_paid", "input": "Chief Okafor 175k don clear.", "expected": {"customer": "Chief Okafor", "amount": "175000", "type": "payable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "payable_paid", "input": "I don send 95k give Alhaji Musa. We don even.", "expected": {"customer": "Alhaji Musa", "amount": "95000", "type": "payable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "payable_paid", "input": "I don transfer 42k give Mama Adura for beans.", "expected": {"customer": "Mama Adura", "amount": "42000", "type": "payable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "payable_paid", "input": "I don pay Chidinma 28k cash yesterday.", "expected": {"customer": "Chidinma", "amount": "28000", "type": "payable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "payable_paid", "input": "Alhaji Bello 60k don settle.", "expected": {"customer": "Alhaji Bello", "amount": "60000", "type": "payable", "status": "paid"}},

    # --- Pidgin amount formats ---
    {"lang": "Pidgin", "cat": "amount_format", "input": "Chinedu owe me 85k o.", "expected": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "amount_format", "input": "I wan pay N250,000 give Alhaji Bello.", "expected": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "amount_format", "input": "Mama Nkechi don pay N35,000.", "expected": {"customer": "Mama Nkechi", "amount": "35000", "type": "receivable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "amount_format", "input": "Uncle Emeka still dey owe 45 thousand.", "expected": {"customer": "Uncle Emeka", "amount": "45000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "amount_format", "input": "I owe Alhaji Ibrahim 200k.", "expected": {"customer": "Alhaji Ibrahim", "amount": "200000", "type": "payable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "amount_format", "input": "Chidinma debt na N55,000.", "expected": {"customer": "Chidinma", "amount": "55000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "amount_format", "input": "I don pay 150k give Chief Okafor.", "expected": {"customer": "Chief Okafor", "amount": "150000", "type": "payable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "amount_format", "input": "Ngozi still owe me N65,000 for fabric.", "expected": {"customer": "Ngozi", "amount": "65000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Pidgin", "cat": "amount_format", "input": "Alhaji Musa don collect 95k.", "expected": {"customer": "Alhaji Musa", "amount": "95000", "type": "payable", "status": "paid"}},
    {"lang": "Pidgin", "cat": "amount_format", "input": "Emeka don send N90,000. Don finish.", "expected": {"customer": "Emeka", "amount": "90000", "type": "receivable", "status": "paid"}},

    # ===== MESSY / AMBIGUOUS (30 examples) =====

    # --- Code-switched ---
    {"lang": "Messy", "cat": "code_switch", "input": "Chinedu never balance the 85k, he go pay after market day.", "expected": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "code_switch", "input": "Mama Adura don settle the 20k wey she owe me from last month.", "expected": {"customer": "Mama Adura", "amount": "20000", "type": "receivable", "status": "paid"}},
    {"lang": "Messy", "cat": "code_switch", "input": "I need to pay Alhaji Bello the 250k for rice, he don deliver.", "expected": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "code_switch", "input": "Uncle Emeka still dey owe me 45k, e say e go pay next week.", "expected": {"customer": "Uncle Emeka", "amount": "45000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "code_switch", "input": "I don send the 50k to Mama Nkechi through her GTBank account.", "expected": {"customer": "Mama Nkechi", "amount": "50000", "type": "payable", "status": "paid"}},
    {"lang": "Messy", "cat": "code_switch", "input": "Chinedu paid 85k but I think say na 95k e owe me.", "expected": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "paid"}},
    {"lang": "Messy", "cat": "code_switch", "input": "Alhaji Bello say my balance don become 300k but I think na 250k.", "expected": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "code_switch", "input": "Mama Nkechi still dey owe me for the rice wey I supply am last week.", "expected": {"customer": "Mama Nkechi", "amount": "0", "type": "receivable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "code_switch", "input": "I pay Chinedu 45k but e say I still owe am 15k for change.", "expected": {"customer": "Chinedu", "amount": "15000", "type": "payable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "code_switch", "input": "Uncle Emeka don pay 200k but I no see am for my account.", "expected": {"customer": "Uncle Emeka", "amount": "200000", "type": "receivable", "status": "paid"}},

    # --- Multi-transaction messages ---
    {"lang": "Messy", "cat": "multi_tx", "input": "So Chinedu owe me 85k and Mama Adura don pay her 20k.", "expected": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "multi_tx", "input": "I need pay Alhaji Bello 250k but I also collect 50k from Chinedu.", "expected": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "multi_tx", "input": "Uncle Emeka owe me 45k and I owe Mama Nkechi 80k.", "expected": {"customer": "Uncle Emeka", "amount": "45000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "multi_tx", "input": "Mama Adura pay 20k, Chinedu pay 50k, Alhaji Bello still dey wait.", "expected": {"customer": "Mama Adura", "amount": "20000", "type": "receivable", "status": "paid"}},
    {"lang": "Messy", "cat": "multi_tx", "input": "I pay Alhaji Ibrahim 300k and I collect 90k from Igwe.", "expected": {"customer": "Alhaji Ibrahim", "amount": "300000", "type": "payable", "status": "paid"}},
    {"lang": "Messy", "cat": "multi_tx", "input": "Chidinma owe 55k, Ngozi pay 65k, Emeka still dey owe 75k.", "expected": {"customer": "Chidinma", "amount": "55000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "multi_tx", "input": "I pay Chief Okafor 175k and Alhaji Musa 95k today.", "expected": {"customer": "Chief Okafor", "amount": "175000", "type": "payable", "status": "paid"}},
    {"lang": "Messy", "cat": "multi_tx", "input": "Amina pay 55k, Chinedu owe 40k, Mama Adura balance 42k.", "expected": {"customer": "Amina", "amount": "55000", "type": "receivable", "status": "paid"}},
    {"lang": "Messy", "cat": "multi_tx", "input": "Alhaji Bello deliver 50 bags rice, I owe 250k. Chinedu collect 10 bags, e owe 85k.", "expected": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "multi_tx", "input": "Mama Nkechi owe 45k, Uncle Emeka pay 200k, I still owe Chinedu 15k.", "expected": {"customer": "Mama Nkechi", "amount": "45000", "type": "receivable", "status": "outstanding"}},

    # --- Disputed / uncertain ---
    {"lang": "Messy", "cat": "disputed", "input": "Chinedu say he don pay 85k but I no see am.", "expected": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "disputed", "input": "Mama Nkechi say her balance na 35k but I think na 45k.", "expected": {"customer": "Mama Nkechi", "amount": "35000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "disputed", "input": "Alhaji Bello say I owe am 300k but I say na 250k.", "expected": {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "disputed", "input": "Uncle Emeka claim say e don pay 200k, I never see the money.", "expected": {"customer": "Uncle Emeka", "amount": "200000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "disputed", "input": "I think Chinedu owe me 85k but e say na 75k.", "expected": {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "disputed", "input": "Mama Adura say she pay 20k but the alert never show.", "expected": {"customer": "Mama Adura", "amount": "20000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "disputed", "input": "Alhaji Ibrahim say my balance don change to 350k.", "expected": {"customer": "Alhaji Ibrahim", "amount": "350000", "type": "payable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "disputed", "input": "Chidinma say she pay 55k yesterday, I never confirm.", "expected": {"customer": "Chidinma", "amount": "55000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "disputed", "input": "I be say Emeka owe 75k but e claim say e don pay.", "expected": {"customer": "Emeka", "amount": "75000", "type": "receivable", "status": "outstanding"}},
    {"lang": "Messy", "cat": "disputed", "input": "Ngozi say her debt don clear but I no see the 65k.", "expected": {"customer": "Ngozi", "amount": "65000", "type": "receivable", "status": "outstanding"}},
]


# ============================================================
# SYSTEM PROMPT — optimized with few-shot examples
# ============================================================

SYSTEM_PROMPT = """You are MOVA, an offline financial intelligence system for African SMEs.
You extract structured financial data from business messages.

KEY RULE:
- "I owe X" = PAYABLE (you must pay X)
- "X owes me" or "X still dey owe me" = RECEIVABLE (X must pay you)

Examples:
"I owe Chinedu 15k" -> {"customer": "Chinedu", "amount": "15000", "type": "payable", "status": "outstanding"}
"Chinedu owe me 85k" -> {"customer": "Chinedu", "amount": "85000", "type": "receivable", "status": "outstanding"}
"I need to pay Alhaji Bello 250k" -> {"customer": "Alhaji Bello", "amount": "250000", "type": "payable", "status": "outstanding"}
"Alhaji Bello owe me 250k" -> {"customer": "Alhaji Bello", "amount": "250000", "type": "receivable", "status": "outstanding"}
"Mama Adura don pay 20k" -> {"customer": "Mama Adura", "amount": "20000", "type": "receivable", "status": "paid"}
"I don pay Mama Nkechi 80k" -> {"customer": "Mama Nkechi", "amount": "80000", "type": "payable", "status": "paid"}

Output ONLY valid JSON. No explanation:
{"customer": "name", "amount": "number", "type": "receivable or payable", "status": "outstanding or paid"}
"""


def query_model(prompt: str) -> str:
    """Query the llama-server and return the response."""
    payload = json.dumps({
        "prompt": prompt,
        "n_predict": 128,
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


def extract_json(text: str) -> dict:
    """Extract JSON from model response."""
    text = text.strip()
    # Try to find JSON in the response
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except:
                pass
    # Try to find any JSON-like object
    match = re.search(r'\{[^}]+\}', text)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    return {}


def normalize_amount(val: str) -> str:
    """Normalize amount to plain number string."""
    val = val.strip()
    val = re.sub(r'[₦$,\s]', '', val)
    val = val.replace('k', '000').replace('K', '000')
    val = re.sub(r'thousand', '000', val, flags=re.IGNORECASE)
    return val


def score_example(example: dict, response: str) -> dict:
    """Score a single example against model response."""
    parsed = extract_json(response)
    expected = example["expected"]

    scores = {}

    # Entity accuracy (customer name)
    exp_customer = expected["customer"].lower()
    act_customer = parsed.get("customer", "").lower()
    scores["entity"] = exp_customer in act_customer or act_customer in exp_customer

    # Amount accuracy
    exp_amount = normalize_amount(expected["amount"])
    act_amount = normalize_amount(parsed.get("amount", ""))
    scores["amount"] = exp_amount == act_amount

    # Direction accuracy (type)
    exp_type = expected["type"]
    act_type = parsed.get("type", "").lower()
    scores["direction"] = exp_type in act_type

    # Status accuracy
    exp_status = expected["status"]
    act_status = parsed.get("status", "").lower()
    if exp_status == "paid":
        scores["status"] = any(w in act_status for w in ["paid", "settled", "done", "clear", "finish"])
    else:
        scores["status"] = any(w in act_status for w in ["outstanding", "pending", "unpaid", "owe"])

    # Full record (all 4 fields correct)
    scores["full"] = all(scores.values())

    return scores


def main():
    print("=" * 70)
    print("MOVA Nigerian Economic Benchmark — 150 Examples")
    print("=" * 70)

    # Check server is running
    try:
        result = subprocess.run(["curl", "-s", "--max-time", "5", "http://127.0.0.1:8084/health"],
                              capture_output=True, text=True, timeout=10)
        if "ok" not in result.stdout:
            print("ERROR: llama-server not running on port 8084")
            return
    except:
        print("ERROR: llama-server not running")
        return

    results = []
    lang_scores = defaultdict(lambda: {"entity": [], "amount": [], "direction": [], "status": [], "full": []})
    cat_scores = defaultdict(lambda: {"entity": [], "amount": [], "direction": [], "status": [], "full": []})

    total = len(BENCHMARK)
    for i, example in enumerate(BENCHMARK):
        prompt = f"{SYSTEM_PROMPT}\n\nUser: {example['input']}\n\nResponse:"
        print(f"  [{i+1:3d}/{total}] {example['lang']:8s} {example['cat']:20s} ", end="", flush=True)

        response = query_model(prompt)
        scores = score_example(example, response)

        lang_scores[example["lang"]]["entity"].append(scores["entity"])
        lang_scores[example["lang"]]["amount"].append(scores["amount"])
        lang_scores[example["lang"]]["direction"].append(scores["direction"])
        lang_scores[example["lang"]]["status"].append(scores["status"])
        lang_scores[example["lang"]]["full"].append(scores["full"])

        cat_scores[example["cat"]]["entity"].append(scores["entity"])
        cat_scores[example["cat"]]["amount"].append(scores["amount"])
        cat_scores[example["cat"]]["direction"].append(scores["direction"])
        cat_scores[example["cat"]]["status"].append(scores["status"])
        cat_scores[example["cat"]]["full"].append(scores["full"])

        status = "PASS" if scores["full"] else "FAIL"
        print(f"{status}")

        results.append({"example": example, "response": response, "scores": scores, "parsed": extract_json(response)})

    # Summary by language
    print("\n" + "=" * 70)
    print("RESULTS BY LANGUAGE")
    print("=" * 70)
    for lang in ["English", "Pidgin", "Messy"]:
        s = lang_scores[lang]
        n = len(s["entity"])
        if n == 0:
            continue
        print(f"\n  {lang} ({n} examples):")
        print(f"    Entity:    {sum(s['entity'])/n:.0%}")
        print(f"    Amount:    {sum(s['amount'])/n:.0%}")
        print(f"    Direction: {sum(s['direction'])/n:.0%}")
        print(f"    Status:    {sum(s['status'])/n:.0%}")
        print(f"    FULL:      {sum(s['full'])/n:.0%}")

    # Summary by category
    print("\n" + "=" * 70)
    print("RESULTS BY CATEGORY")
    print("=" * 70)
    for cat in sorted(cat_scores.keys()):
        s = cat_scores[cat]
        n = len(s["entity"])
        print(f"  {cat:20s} {n:3d} examples  full={sum(s['full'])/n:.0%}  entity={sum(s['entity'])/n:.0%}  amount={sum(s['amount'])/n:.0%}  direction={sum(s['direction'])/n:.0%}  status={sum(s['status'])/n:.0%}")

    # Overall
    all_entity = [x for s in lang_scores.values() for x in s["entity"]]
    all_amount = [x for s in lang_scores.values() for x in s["amount"]]
    all_direction = [x for s in lang_scores.values() for x in s["direction"]]
    all_status = [x for s in lang_scores.values() for x in s["status"]]
    all_full = [x for s in lang_scores.values() for x in s["full"]]
    n = len(all_entity)

    print(f"\n  OVERALL ({n} examples):")
    print(f"    Entity:    {sum(all_entity)/n:.0%}")
    print(f"    Amount:    {sum(all_amount)/n:.0%}")
    print(f"    Direction: {sum(all_direction)/n:.0%}")
    print(f"    Status:    {sum(all_status)/n:.0%}")
    print(f"    FULL:      {sum(all_full)/n:.0%}")

    # Save results
    with open("benchmark_results.json", "w") as f:
        json.dump({
            "total": n,
            "overall": {
                "entity": sum(all_entity)/n,
                "amount": sum(all_amount)/n,
                "direction": sum(all_direction)/n,
                "status": sum(all_status)/n,
                "full": sum(all_full)/n,
            },
            "by_language": {lang: {k: sum(v)/len(v) for k, v in scores.items()} for lang, scores in lang_scores.items()},
            "by_category": {cat: {k: sum(v)/len(v) for k, v in scores.items()} for cat, scores in cat_scores.items()},
            "details": results,
        }, f, indent=2)

    print(f"\nFull results saved to benchmark_results.json")


if __name__ == "__main__":
    main()
