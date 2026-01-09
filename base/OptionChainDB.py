import sqlite3
import json
import os
from datetime import datetime


class OptionChainDB:
    def __init__(self, db_name="145_bn.db", db_folder="./db"):
        self.db_folder = db_folder
        self.db_name = db_name

        os.makedirs(self.db_folder, exist_ok=True)
        self.db_path = os.path.join(self.db_folder, self.db_name)

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        self._init_db()

    # ----------------------------------------
    # Init + migrate schema
    # ----------------------------------------
    def _init_db(self):
        cursor = self.conn.cursor()

        # Create table (SAFE)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS selected_options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            option_type TEXT NOT NULL
                CHECK (option_type IN ('CE', 'PE')),
            strike INTEGER NOT NULL,
            ltp REAL NOT NULL,
            trade_date TEXT NOT NULL,
            trade_time TEXT NOT NULL,
            raw_json TEXT,
            UNIQUE(symbol, option_type, trade_date)
        );
        """)

        self._migrate_columns(cursor)
        self.conn.commit()

    # ----------------------------------------
    # Schema migration
    # ----------------------------------------
    def _column_exists(self, cursor, table, column):
        cursor.execute(f"PRAGMA table_info({table})")
        return column in [row[1] for row in cursor.fetchall()]

    def _migrate_columns(self, cursor):
        table = "selected_options"

        if not self._column_exists(cursor, table, "trade_time"):
            cursor.execute(
                "ALTER TABLE selected_options ADD COLUMN trade_time TEXT"
            )

        if not self._column_exists(cursor, table, "raw_json"):
            cursor.execute(
                "ALTER TABLE selected_options ADD COLUMN raw_json TEXT"
            )

    # ----------------------------------------
    # Insert / Replace today's data
    # ----------------------------------------
    def save_options_today(self, options):
        cursor = self.conn.cursor()

        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        now_time = now.strftime("%H:%M:%S")

        for opt in options:
            print(opt)
            cursor.execute("""
            INSERT OR REPLACE INTO selected_options (
                symbol, option_type, strike, ltp,
                trade_date, trade_time, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                opt.get("symbol"),
                opt.get("type"),
                opt.get("strike"),
                opt.get("ltp", 0),
                today,
                now_time,
                json.dumps(opt)
            ))

        self.conn.commit()

    # ----------------------------------------
    # Fetch today's options (dict)
    # ----------------------------------------
    def get_today_options_as_dict(self):
        # print("Fetch today's options (dict)")
        cursor = self.conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT symbol, option_type, strike, ltp, trade_date, trade_time
            FROM selected_options
            WHERE trade_date = ?
            ORDER BY strike
        """, (today,))

        return [
            {
                "symbol": row["symbol"],
                "type": row["option_type"],
                "strike": row["strike"],
                "ltp": row["ltp"],
                "date": row["trade_date"],
                "time": row["trade_time"]
            }
            for row in cursor.fetchall()
        ]

    # ----------------------------------------
    def close(self):
        self.conn.close()
