from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .schemas import TokenData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")

#Command for generating secret key "openssl rand -hex 32"
SECRET_KEY = "e007c5f110800d63681cd19e974af485c9193fd5d2016eccb4bd66a4bfbd734d"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
                )
        token_data = TokenData(email=email)
        return {"email": email}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
            )
