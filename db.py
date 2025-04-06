import sqlite3
from typing import Optional
from dataclasses import dataclass
from contextlib import contextmanager

clients = [
    {
        "name": "Mr. John",
        "debt": 1000,
        "pay_date": "March 30",
        "call_status": "pending",
    },
    {
        "name": "Ms. Jane",
        "debt": 2000,
        "pay_date": "April 15",
        "call_status": "pending",
    },
    {
        "name": "Mr. Smith",
        "debt": 3000,
        "pay_date": "May 10",
        "call_status": "pending",
    },
    {
        "name": "Ms. Johnson",
        "debt": 4000,
        "pay_date": "June 20",
        "call_status": "pending",
    },
]


@dataclass
class Client:
    id: int
    name: str
    debt: int
    pay_date: str
    call_status: str

class DB:
    def __init__(self, db_path: str = "auto_db.sqlite"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS clients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        debt INTEGER,
                        pay_date TEXT,
                        call_status TEXT
                    )
                    """
            )
            conn.commit()
    
    def add_client(self, client: Client):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                    INSERT INTO clients (name, debt, pay_date, call_status)
                    VALUES (?, ?, ?, ?)
                    """, (client.name, client.debt, client.pay_date, client.call_status))
            conn.commit()
        
    def insert_clients(self, clients: list[dict]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            client_tuples = [(client["name"], client["debt"], client["pay_date"], client["call_status"]) for client in clients]
            cursor.executemany("""
                    INSERT INTO clients (name, debt, pay_date, call_status)
                    VALUES (?, ?, ?, ?)
                    """, client_tuples)
            conn.commit()
    
    def get_client(self) -> Optional[Client]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                    SELECT id, name, debt, pay_date, call_status FROM clients WHERE call_status = 'pending'
                    """)
            result = cursor.fetchone()
            if result:
                return Client(
                    id=result[0],
                    name=result[1],
                    debt=result[2],
                    pay_date=result[3],
                    call_status=result[4]
                )
            return None
    
    def update_client_status(self, client_id: int, status: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                    UPDATE clients 
                    SET call_status = ? 
                    WHERE id = ?
                    """, (status, client_id))
            conn.commit()
            return cursor.rowcount > 0

if __name__ == "__main__":
    db = DB()
    db.insert_clients(clients)
    print(db.get_client())