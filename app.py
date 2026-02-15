import pyodbc
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Connection string with ODBC Driver 17
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

# Health endpoint (important for Azure)
@app.get("/")
def health():
    return {"status": "running"}

# Get all tasks
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

# Get task by ID
@app.get("/api/tasks/{task_id}")
def get_task(task_id: int):
    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ID, Title, Description FROM Tasks WHERE ID=?", task_id)
        row = cursor.fetchone()
        if row:
            return {"ID": row[0], "Title": row[1], "Description": row[2]}
    return {"message": "Task not found"}

# Create task
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

# Update task
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

# Delete task
@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Tasks WHERE ID=?", task_id)
        conn.commit()
    return {"message": "Task deleted"}
