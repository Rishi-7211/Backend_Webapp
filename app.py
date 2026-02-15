import pyodbc
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

connection_string = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=tcp:sqldatabse.database.windows.net,1433;"
    "Database=Sqldatabse;"
    "Uid=sqladmin;"
    "Pwd=Devops@123456;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Task(BaseModel):
    title: str
    description: str

# 🔹 Auto create table if not exists
def create_table_if_not_exists():
    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Tasks' AND xtype='U')
        CREATE TABLE Tasks (
            ID INT IDENTITY(1,1) PRIMARY KEY,
            Title VARCHAR(255),
            Description VARCHAR(MAX)
        )
        """)
        conn.commit()

# 🔹 Run at startup
@app.on_event("startup")
def startup_event():
    create_table_if_not_exists()

@app.get("/")
def health():
    return {"status": "running"}

@app.get("/api/tasks")
def get_tasks():
    tasks = []
    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ID, Title, Description FROM Tasks")
        for row in cursor.fetchall():
            tasks.append({
                "ID": row[0],
                "Title": row[1],
                "Description": row[2]
            })
    return tasks

@app.post("/api/tasks")
def create_task(task: Task):
    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Tasks (Title, Description) VALUES (?, ?)",
            task.title,
            task.description,
        )
        conn.commit()
    return {"message": "Task created"}

@app.get("/api/tasks/{task_id}")
def get_task(task_id: int):
    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ID, Title, Description FROM Tasks WHERE ID=?", task_id)
        row = cursor.fetchone()
        if row:
            return {"ID": row[0], "Title": row[1], "Description": row[2]}
    return {"message": "Task not found"}

@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Tasks SET Title=?, Description=? WHERE ID=?",
            task.title,
            task.description,
            task_id,
        )
        conn.commit()
    return {"message": "Task updated"}

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Tasks WHERE ID=?", task_id)
        conn.commit()
    return {"message": "Task deleted"}
