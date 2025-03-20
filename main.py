from fastapi import FastAPI, HTTPException, Response, Depends
from sqlalchemy import select

from fastapi.middleware.cors import CORSMiddleware

from depencies import SessionDependency
from schemas import Login, Task, ItemId, TaskToChange
from models import Users, Tasks

from authx import AuthX, AuthXConfig

from passlib.context import CryptContext


app = FastAPI()

config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]
security = AuthX(config=config)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Утилита для хэширования паролей
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def get_current_user(token: str = Depends(security)) -> dict:
    if not token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return token  # Возвращаем содержание токена (например, информацию о пользователе)

@app.get("/")
async def main():
    return {"message": "Hello1"}


@app.post("/reg")
async def reg(session: SessionDependency, reg_data: Login):
    hashed_password = hash_password(reg_data.password)
    
    user = Users(name=reg_data.name, password=hashed_password)
    session.add(user)
    
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существет")

    return {"name": user.name, "password": user.password}


@app.post("/login")
async def login(session: SessionDependency, login_data: Login, response: Response):
    user = session.query(Users).filter(Users.name == login_data.name).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    
    if not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")

    access_token = security.create_access_token(uid="12345")
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, access_token)
    
    return {"access_token": access_token}



@app.post("/task")
async def create_task(session: SessionDependency, task_data: Task):
    task = Tasks(**task_data.dict())
    # print(task.task)
    session.add(task)

    try:
        session.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Ошибка при добавлении задачи")

    return {"task": task.task, "done": task.done}

@app.get("/tasks")
async def get_tasks(session: SessionDependency):
    task = session.query(Tasks).all()
    # print(task)
    return {"tasks": task}


@app.delete("/task")
async def delete_task(session: SessionDependency, task_id: ItemId):
    try:
        task_delete = session.query(Tasks).filter(Tasks.id == task_id.id).first()
        session.delete(task_delete)
        session.commit()
    except Exception as e:
        print(e)
    return {"Удалено": True}


@app.patch("/task")
async def patch_task(session: SessionDependency, task_to_change: TaskToChange):
    task = session.query(Tasks).filter(Tasks.id == task_to_change.id).first()

    if task is not None:
        for key, value in task_to_change.dict(exclude_unset=True).items():
            setattr(task, key, value)
        session.commit()
    return {'status': 'ok'}


origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)