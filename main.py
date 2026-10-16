import models
from database import engine
from fastapi import FastAPI
from routers import todos, users, auth, admin

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)
app.include_router(admin.router)
