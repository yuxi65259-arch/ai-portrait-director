"""SQLite 数据库 — 用户 / 积分 / 支付记录"""
import sqlite3, os, uuid, time

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            api_key TEXT UNIQUE NOT NULL,
            credits INTEGER DEFAULT 0,
            created_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS credit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            amount INTEGER NOT NULL,
            log_type TEXT NOT NULL,
            description TEXT DEFAULT '',
            created_at REAL NOT NULL
        );
    """)
    conn.commit()
    conn.close()


def create_user(username: str) -> dict:
    conn = get_db()
    uid = str(uuid.uuid4())[:8]
    api_key = "px-" + str(uuid.uuid4()).replace("-", "")[:24]
    now = time.time()
    conn.execute(
        "INSERT INTO users (id, username, api_key, credits, created_at) VALUES (?,?,?,?,?)",
        (uid, username, api_key, 100, now),  # 新用户赠送 100 积分
    )
    conn.commit()
    conn.close()
    return {"id": uid, "username": username, "api_key": api_key, "credits": 100}


def get_user_by_key(api_key: str) -> dict:
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE api_key = ?", (api_key,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_credits(user_id: str) -> int:
    conn = get_db()
    row = conn.execute("SELECT credits FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row["credits"] if row else 0


def add_credits(user_id: str, amount: int, description: str = "充值") -> int:
    conn = get_db()
    conn.execute("UPDATE users SET credits = credits + ? WHERE id = ?", (amount, user_id))
    conn.execute(
        "INSERT INTO credit_log (user_id, amount, log_type, description, created_at) VALUES (?,?,?,?,?)",
        (user_id, amount, "charge", description, time.time()),
    )
    conn.commit()
    row = conn.execute("SELECT credits FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row["credits"]


def consume_credits(user_id: str, amount: int, description: str = "生成图片") -> dict:
    """扣积分，返回 {success: bool, credits: int, error: str}"""
    conn = get_db()
    row = conn.execute("SELECT credits FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        conn.close()
        return {"success": False, "credits": 0, "error": "用户不存在"}
    if row["credits"] < amount:
        conn.close()
        return {"success": False, "credits": row["credits"], "error": f"积分不足，需要 {amount} 积分，当前 {row['credits']} 积分"}
    conn.execute("UPDATE users SET credits = credits - ? WHERE id = ?", (amount, user_id))
    conn.execute(
        "INSERT INTO credit_log (user_id, amount, log_type, description, created_at) VALUES (?,?,?,?,?)",
        (user_id, -amount, "consume", description, time.time()),
    )
    conn.commit()
    new_credits = conn.execute("SELECT credits FROM users WHERE id = ?", (user_id,)).fetchone()["credits"]
    conn.close()
    return {"success": True, "credits": new_credits, "error": ""}


# 初始化
init_db()
