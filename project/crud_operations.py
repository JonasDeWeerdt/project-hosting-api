from fastapi import HTTPException
from sqlalchemy.orm import Session
import auth
import models
import schemas
import subprocess


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    response = {'ansible_user': user.email,
                'ansible_uid': db.query(models.User).filter(models.User.id == user.id).get('uid'),
                'ansible_gid': db.query(models.User).filter(models.User.id == user.id).get('gid'),
                'ansible_password': user.password}

    playbook_path = "ansible/playbook.yml"
    ansible_command = f"ansible-playbook {playbook_path} --extra-vars="
    try:
        # Execute the Ansible playbook command
        subprocess.run(ansible_command, shell=True, check=True)
        # Playbook executed successfully
        return db_user
    except subprocess.CalledProcessError as e:
        # Playbook execution failed
        # Handle the error appropriately (e.g., logging, error response, etc.)
        # You can access the error message through e.stderr
        raise Exception(f"Failed to run Ansible playbook: {e.stderr}")


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def set_password(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    user_db = db.query(models.User).filter(
        models.User.email == user.email).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    user_db.hashed_password = hashed_password
    db.commit()

    return "success"
