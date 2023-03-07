from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
import psycopg2
import pandas as pd
from pydantic import BaseModel
import hashlib
import sqlquery
import string
import secrets
import datetime
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8000/user_table",
    "http://localhost:3000",
    "file:///home/batuhan/Documents/GitHub/html_table/index.html",
    "file:///home/batuhan/Documents/GitHub/html_table/index.html",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5173"

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conn = psycopg2.connect(
    host = os.getenv('POSTGRES_HOST'),
    database = os.getenv('POSTGRES_DB'),
    user = os.getenv('POSTGRES_USER'),
    password = os.getenv('POSTGRES_PASSWORD'),
)

async def create_table():
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS "users" (
	id serial PRIMARY KEY,
	email VARCHAR ( 50 ) UNIQUE NOT NULL,
	password VARCHAR NOT NULL,
	role VARCHAR (50) NOT NULL,
	token VARCHAR,
	expire_time VARCHAR,
	register_date VARCHAR
);  """)

class User(BaseModel):
    email: str
    password: str
    date: str

    
create_table()

@app.get("/users")
async def get_table():
    data_last = pd.read_sql_query("SELECT * FROM users",conn)
    print(data_last.to_dict("records"))
    return JSONResponse(
        content={
        "data": data_last.to_dict("records"),
        "success": True
        }
    )

@app.get("/user/{id}/")
async def get_user(
    id = int
):  
    info = {
        "id":id
    }
    
    data = pd.read_sql_query(sqlquery.get_user.format(**info),conn)
    print(data.to_dict("records"))
    return JSONResponse(
        content={
        "data":data.to_dict("records"),
        "success":True
        }
    )

@app.post("/register")
async def create_user(user: User):
    try:
        cur = conn.cursor()
        email = user.email
        password = user.password
        date = user.date
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        info ={

            "email":email,
            "password":hashed_password,
            "date":date,

        }
        
        cur.execute(sqlquery.insert_data.format(**info))
        conn.commit()
        cur.execute("SELECT * FROM users")
        results = cur.fetchall()
        conn.rollback()
        return JSONResponse(content=results)
    except psycopg2.errors.UniqueViolation:
        return "Mail adresi Kullanılmaktadır", status.HTTP_406_NOT_ACCEPTABLE