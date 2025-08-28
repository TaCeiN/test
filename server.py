from fastapi import FastAPI, HTTPException, Depends
import uvicorn
from sqlalchemy.orm import Session
from hashingpassword import hash_password, verify_password
import DataBase
from pydantic import BaseModel, EmailStr, constr

app = FastAPI()

def get_db():
    db = DataBase.SessionLocal()
    try:
        yield db
    finally:
        db.close()




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


@app.post("/register")
async def Register(user_creditinals: UserCreateInput, db: Session = Depends(get_db)) -> UserCreateOutPut:
    # db.query(DataBase.DBUsers) - выбор таблицы в бд, filter(DataBase.DBUsers.email == user_creditinals.email).first() - фильтрация по первому совпадению
    existing_user = db.query(DataBase.DBUsers).filter(DataBase.DBUsers.email == user_creditinals.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = DataBase.DBUsers(
        name=user_creditinals.name,
        email=user_creditinals.email,
        hashed_password=hash_password(user_creditinals.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"success": True, "user_id": new_user.id}


@app.post("/login")
async def Login(user_creditinals: UserLoginInput, db: Session = Depends(get_db)) -> UserLoginOutput:
    existing_user = db.query(DataBase.DBUsers).filter(DataBase.DBUsers.email == user_creditinals.email).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user_creditinals.password, existing_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    return {"success": True, "user_id": existing_user.id}

if __name__ == "__main__":
    uvicorn.run(app, port=8080)
