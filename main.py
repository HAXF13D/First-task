from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, DateTime, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
import requests
from credits import USER_NAME, PASSWORD, DB_NAME


# Конфигурация базы данных
SQLALCHEMY_URL = f'postgresql://{USER_NAME}:{PASSWORD}@localhost/{DB_NAME}'
db_engine = create_engine(SQLALCHEMY_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


class Base(DeclarativeBase):
    pass


# Таблица
class QuizQuestion(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, index=True)
    answer = Column(String)
    created_at = Column(DateTime, default=datetime.now)


# Создание таблицы, если не существует
Base.metadata.create_all(db_engine, checkfirst=True)

app = FastAPI()


# Модели
class QuestionRequest(BaseModel):
    questions_amount: int


# Маршруты
@app.post("/questions/")
def save_questions(questions: QuestionRequest):
    db = session_local()
    saved_questions = []

    while len(saved_questions) < questions.questions_amount:
        response = requests.get("https://jservice.io/api/random?count=1")
        data = response.json()
        if data:
            question_data = data[0]
            question = question_data['question']
            answer = question_data['answer']
            question_exists = db.query(
                QuizQuestion).filter(QuizQuestion.question == question).first()

            if not question_exists:
                new_question = QuizQuestion(question=question, answer=answer)
                db.add(new_question)
                db.commit()
                db.refresh(new_question)
                saved_questions.append(new_question)

    return saved_questions[-1] if saved_questions else {}
