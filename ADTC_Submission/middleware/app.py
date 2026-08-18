import json
import asyncio
import httpx
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import database

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

database.init_db()

class TradeInput(BaseModel):
    text: str

LLAMA_SERVER_URL = "http://localhost:8080/completion"

async def process_trade_stream(text: str):
    yield f"data: {json.dumps({'thought': 'Initializing Safety Console...'})}\n\n"
    await asyncio.sleep(0.5)
    yield f"data: {json.dumps({'thought': 'Parsing entities from raw input...'})}\n\n"
    
    prompt = f"""
Extract the accounting information from the following text into JSON format.
Only return valid JSON with these exact keys: "item_name" (string), "quantity" (number), "unit_price" (number), "total_price" (number). If a value is missing, infer it or use 0.

Text: "{text}"
JSON:"""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(LLAMA_SERVER_URL, json={
                "prompt": prompt,
                "n_predict": 128,
                "temperature": 0.1,
                "stop": ["}"]
            })
            
            yield f"data: {json.dumps({'thought': 'Received raw tokens from model. Validating JSON...'})}\n\n"
            await asyncio.sleep(0.3)
            
            raw_json = response.json().get("content", "") + "}"
            
            try:
                parsed_data = json.loads(raw_json)
            except json.JSONDecodeError:
                yield f"data: {json.dumps({'thought': '[WARNING] Invalid JSON received. Engaging heuristic fallback.', 'level': 'warn'})}\n\n"
                parsed_data = {"item_name": "Unknown", "quantity": 1, "unit_price": 0, "total_price": 0}
            
            item = parsed_data.get("item_name", "Unknown")
            qty = parsed_data.get("quantity", 1)
            price = parsed_data.get("unit_price", 0)
            total = parsed_data.get("total_price", qty * price)
            
            yield f"data: {json.dumps({'thought': f'Extracted: {qty}x {item} @ {price}'})}\n\n"
            yield f"data: {json.dumps({'thought': 'Engaging Deterministic Math Verification...'})}\n\n"
            await asyncio.sleep(0.5)
            
            verified = True
            expected_total = qty * price
            if total != expected_total:
                yield f"data: {json.dumps({'thought': f'[ERROR] LLM Math Hallucination detected: calculated {total}, expected {expected_total}. Correcting...', 'level': 'error'})}\n\n"
                total = expected_total
                verified = False
            else:
                yield f"data: {json.dumps({'thought': '[PASS] Math verified.'})}\n\n"
                
            yield f"data: {json.dumps({'thought': 'Persisting to SQLite Database...'})}\n\n"
            
            database.log_transaction(text, item, qty, price, total, verified)
            
            final_result = {
                "status": "success",
                "data": {
                    "item": item,
                    "quantity": qty,
                    "unit_price": price,
                    "total_price": total,
                    "verified": verified
                }
            }
            yield f"data: {json.dumps({'result': final_result})}\n\n"
            
    except Exception as e:
        yield f"data: {json.dumps({'thought': f'[FATAL] Engine connection failed: {str(e)}', 'level': 'error'})}\n\n"

@app.post("/api/trade")
async def handle_trade(trade: TradeInput):
    return StreamingResponse(process_trade_stream(trade.text), media_type="text/event-stream")
