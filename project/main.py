from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import os
import crud_operations
import models
import schemas
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import auth
from database import SessionLocal, engine


print("We are in the main.......")
if not os.path.exists('.\sqlitedb'):
    print("Making folder.......")
    os.makedirs('.\sqlitedb')

print("Creating tables.......")
models.Base.metadata.create_all(bind=engine)
print("Tables created.......")

app = FastAPI()


 
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Add the JWT case sub with the subject(user)
    access_token = auth.create_access_token(
        data={"sub": user.email}
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    users = crud_operations.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/playbook", response_model=str)
def deploy_cluster(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme), playbook: str = None, inventory: str = None):
    return crud_operations.deploy_cluster(db, playbook, inventory)

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud_operations.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_operations.create_user(db=db, user=user)


@app.put("/users")
def change_password(user: schemas.UserCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_user = crud_operations.get_user_by_email(db, email=user.email)
    return crud_operations.set_password(db=db, user=user)


@app.on_event("startup")
async def populate_users_table(db: Session = Depends(get_db)):
    # Add your logic to populate the users table with initial data
    user = [{"id": "1","email":"string", "password": "string", "uid": 2001, "gid": 2001}]
    db.add(user)
    db.commit()