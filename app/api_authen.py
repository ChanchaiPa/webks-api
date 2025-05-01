from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db_session
from app.schemas.user_entity import UserEntity
from app.schemas import schema
from app import pwd_utils
import time
import pathlib


router = APIRouter()
@router.post("/authen/login")
def login(login: schema.Login, response: Response, db_session: Session = Depends(get_db_session) ): 
    time.sleep(1) ## for test
    _user = db_session.query(UserEntity).filter( UserEntity.login==login.username ).first()
    if not _user:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message" : "Login Fail."})
    if not pwd_utils.verify_password(login.password, _user.password):
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message" : "Login Fail.."})

    user = schema.User(
        agent_id  = _user.agent_id,
        login     = _user.login,
        first_name= _user.first_name,
        last_name = "" if _user.last_name is None else _user.last_name,
        level_id  = _user.level_id,
        group_id  = _user.group_id,
        is_active = _user.is_active
    )
    result = user.dict()
    result['token'] = pwd_utils.create_access_token(data={"agent_id": _user.agent_id, "login": _user.login, "level_id": _user.level_id, "group_id": _user.group_id})
    result['message'] = ""

    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.set_cookie(key="token", 
        value=result['token'], 
        path="/webks", 
        httponly=True, 
        max_age=3*60*60)   ## ***** 3hour
    return result


@router.post("/authen/logout")
def logout(login: schema.Login, response: Response):
    time.sleep(1) ## for test
    response = JSONResponse(content="Success")
    if login:
        response.set_cookie(key="token", 
            value="", 
            path="/webks", 
            httponly=True, 
            max_age=0)
    return response

