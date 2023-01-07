from fastapi import FastAPI
from routers.quiz import quiz_api

app = FastAPI()
app.include_router(quiz_api, prefix="/api/quiz", tags=["quiz"])