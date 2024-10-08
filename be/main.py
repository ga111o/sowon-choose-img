from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()

origins = [
    "http://localhost:8080",
    "https://ga111o.github.io/sowon-choose-img/",
    "https://ga111o.github.io/sowon-choose-img",
    "http://3.34.29.189"
    "http://3.34.29.189/"
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
    elapsedTime: float
    isCorrect: bool
    difficulty: str


init_db()


@app.post("/save/")
async def save_score(score: Score):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scores (age, gender, phone, score, real_image, generated_image, elapsedTime, is_correct, difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (score.age, score.gender, score.phone, score.score, score.realImage, score.generatedImage, score.elapsedTime, score.isCorrect, score.difficulty))
            conn.commit()
            return {"message": "Score saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class fetchScore(BaseModel):
    age: int
    gender: str
    phone: str
    difficulty: str


@app.post("/fetch_score/")
async def fetch_score(fetchScore: fetchScore):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()

            # 자신의 점수를 가져오는 쿼리
            cursor.execute('''
                SELECT SUM(is_correct) AS total_correct, SUM(elapsedTime) AS total_time
                FROM scores
                WHERE age = ? AND gender = ? AND phone = ? AND difficulty = ?
            ''', (fetchScore.age, fetchScore.gender, fetchScore.phone, fetchScore.difficulty))
            result = cursor.fetchone()
            total_correct = result[0] if result[0] is not None else 0
            total_time = result[1] if result[1] is not None else 0

            # 자신의 점수로 순위를 매기기 위한 쿼리
            cursor.execute('''
                SELECT COUNT(*) FROM (
                    SELECT SUM(is_correct) AS total_correct
                    FROM scores
                    WHERE age = ? AND gender = ? AND difficulty = ?
                    GROUP BY phone
                    HAVING total_correct > ?
                )
            ''', (fetchScore.age, fetchScore.gender, fetchScore.difficulty, total_correct))
            rank = cursor.fetchone()[0] + 1  # 순위는 1부터 시작

            # 상위 10명의 점수를 가져오는 쿼리
            cursor.execute('''
                SELECT phone, SUM(is_correct) AS total_correct
                FROM scores
                WHERE difficulty = ?
                GROUP BY phone
                ORDER BY total_correct DESC
                LIMIT 10
            ''', (fetchScore.difficulty,))
            top_scores = cursor.fetchall()

            top_10 = [{"phone": phone, "total_correct": total}
                      for phone, total in top_scores]

            return {
                "total_correct": total_correct,
                "total_time": total_time,
                "rank": rank,
                "top_10": top_10
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
