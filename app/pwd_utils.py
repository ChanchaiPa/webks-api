########################################################
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gen_password(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)    



########################################################
from fastapi import Cookie, HTTPException, status, Request
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY: str = "LUHH2xSdq9VF81NI/29whx4cqB2Hug8Aqh6R/uWCnuA="
ALGORITHM: str = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=3) ## ***** 3hour
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt    

def checkAuthorized(request: Request, token: Optional[str] = Cookie(None)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if (token ==None):
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        agent_id:  str = payload.get("agent_id")
        login: str = payload.get("login")
        level_id: str = payload.get("level_id")
        group_id: str = payload.get("group_id")
        if login is None or login == "":
            return False

        request.state.agent_id  = agent_id
        request.state.login = login
        request.state.level_id = level_id  
        request.state.group_id = group_id 
        return True
    except JWTError:
        raise HTTPException(status_code=400, detail="Unauthorized JWT")      
