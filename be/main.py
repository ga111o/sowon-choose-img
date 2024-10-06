from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()

origins = [
    "http://localhost:8080",
    "https://ga111o.github.io/sowon-choose-img/",
    "https://ga111o.github.io/sowon-choose-img",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE = './festival.db'


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                age INTEGER,
                gender TEXT,
                phone TEXT,
                score INTEGER,
                real_image TEXT,
                generated_image TEXT,
                is_correct BOOLEAN
            )
        ''')
        conn.commit()


class Score(BaseModel):
    age: int
    gender: str
    phone: str
    score: int
    realImage: str
    generatedImage: str
    isCorrect: bool


init_db()


@app.post("/save/")
async def save_score(score: Score):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scores (age, gender, phone, score, real_image, generated_image, is_correct)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (score.age, score.gender, score.phone, score.score, score.realImage, score.generatedImage, score.isCorrect))
            conn.commit()
            return {"message": "Score saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
