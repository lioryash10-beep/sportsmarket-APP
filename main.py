from fastapi import FastAPI, HTTPException
import json
import ctypes
import os
import sqlite3

app = FastAPI(title="Sports Market API")

# --- טעינת מנוע ה-C ---
engine = ctypes.CDLL(os.path.abspath("engine.dll"))
engine.calculate_price.argtypes = [ctypes.c_float, ctypes.c_int]
engine.calculate_price.restype = ctypes.c_float
engine.calculate_sell_price.argtypes = [ctypes.c_float, ctypes.c_int]
engine.calculate_sell_price.restype = ctypes.c_float

def load_data():
    try:
        with open("teams_data.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"error": "Data file not found."}

db_data = load_data()

# --- Endpoints ---

@app.get("/teams")
def get_all_teams():
    return db_data

@app.post("/trade/buy/{player_id}")
def buy_player_share(player_id: int):
    user_id = 1 # כרגע אנחנו משתמשים במשתמש הניסיון (TestUser) שיצרנו
    base_price = 100.0
    
    # חיבור למסד הנתונים
    conn = sqlite3.connect("market.db")
    cursor = conn.cursor()
    
    # 1. בודקים כמה מניות כבר יש בשוק לשחקן הזה
    cursor.execute("SELECT current_supply FROM market WHERE player_id = ?", (player_id,))
    result = cursor.fetchone()
    current_supply = result[0] if result else 0
    
    # 2. מחשבים את המחיר דרך ה-C
    price_to_pay = engine.calculate_price(base_price, current_supply)
    
    # 3. בודקים כמה כסף יש למשתמש
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    user_balance = cursor.fetchone()[0]
    
    # מנגנון הגנה: אין כסף? אין קנייה!
    if user_balance < price_to_pay:
        conn.close()
        raise HTTPException(status_code=400, detail="Not enough balance!")
        
    # 4. ביצוע העסקה
    new_balance = user_balance - price_to_pay
    new_supply = current_supply + 1
    
    # מורידים את הכסף מהמשתמש
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    
    # מעדכנים את כמות המניות בשוק
    if result:
        cursor.execute("UPDATE market SET current_supply = ? WHERE player_id = ?", (new_supply, player_id))
    else:
        cursor.execute("INSERT INTO market (player_id, current_supply) VALUES (?, ?)", (player_id, new_supply))
        
    # מוסיפים את המניה לתיק ההשקעות של המשתמש
    cursor.execute("SELECT shares FROM portfolio WHERE user_id = ? AND player_id = ?", (user_id, player_id))
    if cursor.fetchone():
        cursor.execute("UPDATE portfolio SET shares = shares + 1 WHERE user_id = ? AND player_id = ?", (user_id, player_id))
    else:
        cursor.execute("INSERT INTO portfolio (user_id, player_id, shares) VALUES (?, ?, 1)", (user_id, player_id))
        
    conn.commit()
    conn.close()
    
    return {
        "action": "buy",
        "player_id": player_id,
        "price_paid": price_to_pay,
        "new_wallet_balance": new_balance,
        "new_market_supply": new_supply
    }

@app.post("/trade/sell/{player_id}")
def sell_player_share(player_id: int):
    user_id = 1
    base_price = 100.0
    
    conn = sqlite3.connect("market.db")
    cursor = conn.cursor()
    
    # 1. בודקים אם למשתמש יש בכלל את המניה הזו כדי למכור אותה
    cursor.execute("SELECT shares FROM portfolio WHERE user_id = ? AND player_id = ?", (user_id, player_id))
    portfolio_result = cursor.fetchone()
    
    if not portfolio_result or portfolio_result[0] <= 0:
        conn.close()
        raise HTTPException(status_code=400, detail="You do not own any shares of this player!")
        
    # 2. בודקים מה המצב בשוק
    cursor.execute("SELECT current_supply FROM market WHERE player_id = ?", (player_id,))
    current_supply = cursor.fetchone()[0]
    
    # 3. מחשבים כמה כסף המשתמש יקבל
    price_to_receive = engine.calculate_sell_price(base_price, current_supply)
    
    # 4. ביצוע המכירה
    # מוסיפים כסף למשתמש
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (price_to_receive, user_id))
    # מורידים את המניה מהשוק
    cursor.execute("UPDATE market SET current_supply = current_supply - 1 WHERE player_id = ?", (player_id,))
    # מורידים את המניה מהתיק האישי של המשתמש
    cursor.execute("UPDATE portfolio SET shares = shares - 1 WHERE user_id = ? AND player_id = ?", (user_id, player_id))
    
    # שולפים את היתרה המעודכנת כדי להראות לו
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    new_balance = cursor.fetchone()[0]
    
    conn.commit()
    conn.close()
    
    return {
        "action": "sell",
        "player_id": player_id,
        "price_received": price_to_receive,
        "new_wallet_balance": new_balance,
        "new_market_supply": current_supply - 1
    }