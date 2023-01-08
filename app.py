from fastapi import FastAPI
from routers.quiz import quiz_api
from routers.user import user_api
# from uvicorn import run

app = FastAPI()
app.include_router(quiz_api, prefix="/api/quiz", tags=["quiz"])
app.include_router(user_api, prefix="/api/user", tags=["user"])

# if __name__ == '__main__':
#     run('app:app', reload=True, timeout_keep_alive=0)
