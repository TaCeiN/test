from fastapi import FastAPI, HTTPException, Depends, Response
import uvicorn
from sqlalchemy.orm import Session
from hashingpassword import hash_password, verify_password
import DataBase
from pydantic import BaseModel, EmailStr, constr
import secrets




app = FastAPI()




####################### Подключение БД #########################


def get_db():
    db = DataBase.SessionLocal()
    try:
        yield db
    finally:
        db.close()


####################### Подключение БД #########################




####################### СХЕМЫ PyDantic #########################


class UserCreateInput(BaseModel):
    name: str
    email: EmailStr
    password: constr(min_length=8)

class UserCreateOutPut(BaseModel):
    success: bool
    user_id: int

class UserLoginInput(BaseModel):
    email: EmailStr
    password: constr(min_length=8)

class UserLoginOutput(BaseModel):
    success: bool
    user_id: int


####################### СХЕМЫ PyDantic #########################




####################### Регистрация #########################


@app.post("/register")
async def Register(user_creditinals: UserCreateInput, response: Response,db: Session = Depends(get_db)) -> UserCreateOutPut:
    # db.query(DataBase.DBUsers_creds) - выбор таблицы в бд, filter(DataBase.DBUsers_creds.email == user_creditinals.email).first() - фильтрация по первому совпадению
    existing_user = db.query(DataBase.DBUsers_creds).filter(DataBase.DBUsers_creds.email == user_creditinals.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = DataBase.DBUsers_creds(
        name=user_creditinals.name,
        email=user_creditinals.email,
        hashed_password=hash_password(user_creditinals.password),
    )

    # Создаем токен
    session_token = secrets.token_urlsafe(32)

    # Токен улетает в БД
    new_user.cookie = session_token
    db.commit()

    # ставим cookie в браузер
    response.set_cookie(key="session_token", value=session_token, httponly=True, max_age=120)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"success": True, "user_id": new_user.id}


####################### Регистрация #########################




####################### Логин #########################


@app.post("/login")
async def Login(user_creditinals: UserLoginInput, response: Response, db: Session = Depends(get_db)) -> UserLoginOutput:

    # Поиск по email
    existing_user = db.query(DataBase.DBUsers_creds).filter(DataBase.DBUsers_creds.email == user_creditinals.email).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверка пароля
    if not verify_password(user_creditinals.password, existing_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    # Создаем токен
    session_token = secrets.token_urlsafe(32)

    # Токен улетает в БД
    existing_user.cookie = session_token
    db.commit()

    # ставим cookie в браузер
    response.set_cookie(key="session_token", value=session_token, httponly=True, max_age=120)


    return {"success": True, "user_id": existing_user.id}


####################### Логин #########################



if __name__ == "__main__":
    uvicorn.run(app, port=8080)
