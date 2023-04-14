from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.settings import init_db
from routers.quiz import quiz_api
from routers.user import user_api
from routers.edit_user import user_edit_api
from routers.group import group_api
from uvicorn import run

app = FastAPI(openapi_url="/api/openapi.json")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(quiz_api, prefix="/quiz", tags=["quiz"])
app.include_router(user_api, prefix="/user", tags=["user"])
app.include_router(user_edit_api, prefix="/edit-user", tags=["edit user"])
app.include_router(group_api, prefix="/group", tags=["group"])


@app.on_event("startup")
async def on_startup():
    await init_db()


if __name__ == '__main__':
    run('app:app', reload=True, timeout_keep_alive=0)
