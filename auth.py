from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database import get_user, user_collection
from typing import Optional
from models import UserModel, UpdateUserModel
from decouple import config

SECRET_KEY = config("SECRET_KEY") # Cambia esto por una clave segura
ALGORITHM = config("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexto de hashing para bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer es el esquema para manejar los tokens de autenticación
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Función para verificar la contraseña
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Función para hashear la contraseña
def get_password_hash(password):
    return pwd_context.hash(password)

# Crear un token de acceso JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Función para autenticar al usuario
async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user or not verify_password(password, user["hashed_password"]):  # Acceder al campo como un diccionario
        return False
    return user

# Obtener el usuario actual autenticado mediante el token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name: str = payload.get("sub")
        if user_name is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(user_name)
    if user is None:
        raise credentials_exception
    return UserModel(**user)


# Función para obtener el usuario desde el token
async def get_user_from_token(token: str) -> Optional[UpdateUserModel]:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name: str = payload.get("sub")
        if user_name is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_collection.find_one({"user_name": user_name})
    
    if user is None:
        raise credentials_exception
    
    return UpdateUserModel(id=str(user["_id"]), user_name=user["user_name"], training_level=user["training_level"])

async def get_user_id_from_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name: str = payload.get("sub")
        if user_name is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Aquí deberías buscar el ID del usuario usando el nombre de usuario (user_name) obtenido del token
    user = await UserModel.find_one({"user_name": user_name})  # Buscar en la base de datos por el nombre de usuario
    if user is None:
        raise credentials_exception

    return str(user.id)  # Retornar el ID del usuario en formato de cadena


