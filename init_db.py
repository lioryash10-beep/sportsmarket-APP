import sqlite3

def setup_database():
    # מתחברים לקובץ הנתונים (אם הוא לא קיים, פייתון ייצור אותו לבד הרגע)
    conn = sqlite3.connect("market.db")
    cursor = conn.cursor()

    # 1. יצירת טבלת משתמשים (Users)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            balance REAL NOT NULL
        )
    ''')

    # 2. יצירת טבלת מלאי שחקנים בשוק (Market)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market (
            player_id INTEGER PRIMARY KEY,
            current_supply INTEGER DEFAULT 0
        )
    ''')

    # 3. יצירת טבלת תיק השקעות (Portfolio) - מי מחזיק מה
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            user_id INTEGER,
            player_id INTEGER,
            shares INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, player_id),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    # בונוס: נכניס משתמש ניסיון ראשון למערכת כדי שיהיה לנו עם מי לסחור
    # ניתן לו 1000 מטבעות וירטואליים להתחלה
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, balance) 
        VALUES (1, "TestUser", 1000.0)
    ''')

    # שומרים את השינויים וסוגרים את החיבור
    conn.commit()
    conn.close()
    print("Database 'market.db' created successfully with all tables!")

if __name__ == "__main__":
    setup_database()