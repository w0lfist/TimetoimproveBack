from fastapi import APIRouter, Depends, HTTPException, status
from database import get_users, get_user_id, create_user, get_user, get_user_email, update_user, edit_user_login, delete_user, update_user_o
from models import UserModel, UpdateUserModel, ObjectId, UpdatePasswordModel, DeleteUserModel
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, oauth2_scheme, get_current_user, pwd_context

user_route = APIRouter()


@user_route.get("/api/users/get")
async def get_all_users():
    all_users = await get_users()
    return all_users


@user_route.get("/api/users/{id}", response_model=UserModel)
async def get_one_user(id: str):
    one_user = await get_user_id(id)
    if one_user:
        return one_user
    raise HTTPException(404, f"User with id {id} not found")


@user_route.post("/api/users", response_model=UserModel)
async def create_one_user(User: UserModel):

    user_found = await get_user(User.user_name)
    user_found_email= await get_user_email(User.email)
    if user_found and user_found_email:
        raise HTTPException(409, "Esta cuenta ya esta registrada")
    if user_found:
        raise HTTPException(409, "El nombre de usuario ya esta registrado")
    if user_found_email:
        raise HTTPException(409, "El Correo electronico utilizado ya esta registrado")
    response = await create_user(User)
    if response:
        return response
    raise HTTPException(400, "something went wrong")
    


@user_route.put("/api/users/{id}", response_model=UserModel)
async def edit_user(id: str, user: UpdateUserModel):
    response = await update_user(id, user)
    if response:
        return response
    raise HTTPException(404, f"User with id {id} not found")



@user_route.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["user_name"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "first_login": user.get("first_login", True),  # Mantén esto para saber si es primer inicio
        "user_id": str(user["_id"]),  # Asegúrate de devolver el ID del usuario
        "user_name": user.get("user_name")  # Añadir el nombre de usuario aquí
    }




@user_route.put("/api/users/{id}/first_login")
async def update_first_login(id: str, update_data: UpdateUserModel):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid user ID.")
    
    user = await get_user_id(id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    
    await edit_user_login(id, update_data)
    return {"message": "User first login updated successfully."}


@user_route.get("/check-user-status")
async def check_user_status(token: str = Depends(oauth2_scheme)):
    # Obtén el usuario actual a partir del token
    user = await get_current_user(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    # Devuelve el estado del usuario, incluyendo el campo first_login
    return {
        "first_login": user.first_login  # Asegúrate de que el campo existe en tu modelo
    }

@user_route.put("/api/users/{id}/password")
async def update_password(id: str,update_password_model: UpdatePasswordModel):
    # Obtener el usuario por ID
    user = await get_user_id(id)  # Usa tu función para obtener el usuario
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    # Verificar la contraseña actual
    if not authenticate_user(user["user_name"], update_password_model.current_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña actual incorrecta")

    # Actualizar la contraseña
    hashed_password = pwd_context.hash(update_password_model.new_password)
    await update_user_o(id, {"hashed_password": hashed_password})  # Asumiendo que tienes esta función para actualizar el usuario

    return {"detail": "Contraseña actualizada exitosamente"}

@user_route.delete("/api/delete/user/{id}")
async def delete_user_endpoint(id: str, delete_user_model: DeleteUserModel):
    # Obtener el usuario por ID
    user = await get_user_id(id)  # Usa tu función para obtener el usuario
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Verificar la contraseña actual
    if not authenticate_user(user["user_name"], delete_user_model.current_password):
        raise HTTPException(status_code=401, detail="Contraseña actual incorrecta")

    # Si la autenticación es correcta, proceder a eliminar al usuario
    result = await delete_user(id)
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {"detail": "Usuario eliminado exitosamente"}
