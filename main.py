from fastapi import FastAPI, HTTPException
import json
import ctypes
import os

app = FastAPI(title="Sports Market API")

# --- טעינת מנוע ה-C ---
engine = ctypes.CDLL(os.path.abspath("engine.dll"))

# פונקציית קנייה
engine.calculate_price.argtypes = [ctypes.c_float, ctypes.c_int]
engine.calculate_price.restype = ctypes.c_float

# פונקציית מכירה (הוספנו הרגע!)
engine.calculate_sell_price.argtypes = [ctypes.c_float, ctypes.c_int]
engine.calculate_sell_price.restype = ctypes.c_float

def load_data():
    try:
        with open("teams_data.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"error": "Data file not found."}

db_data = load_data()
market_supply = {}

# --- Endpoints ---

@app.get("/teams")
def get_all_teams():
    return db_data

@app.post("/trade/buy/{player_id}")
def buy_player_share(player_id: int):
    base_price = 100.0
    current_supply = market_supply.get(player_id, 0)
    
    price_to_pay = engine.calculate_price(base_price, current_supply)
    market_supply[player_id] = current_supply + 1
    
    return {
        "action": "buy",
        "player_id": player_id,
        "price_paid": price_to_pay,
        "new_market_supply": market_supply[player_id]
    }

@app.post("/trade/sell/{player_id}")
def sell_player_share(player_id: int):
    base_price = 100.0
    current_supply = market_supply.get(player_id, 0)
    
    # הגנה: אם מנסים למכור כשהשוק על 0, נחזיר שגיאה למשתמש
    if current_supply <= 0:
        raise HTTPException(status_code=400, detail="No shares available to sell in the market")
    
    # חישוב הכסף שהמשתמש מקבל מה-C
    price_to_receive = engine.calculate_sell_price(base_price, current_supply)
    
    # עדכון המאגר - הכמות יורדת ב-1
    market_supply[player_id] = current_supply - 1
    
    return {
        "action": "sell",
        "player_id": player_id,
        "price_received": price_to_receive,
        "new_market_supply": market_supply[player_id]
    }