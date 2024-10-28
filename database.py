from motor.motor_asyncio import AsyncIOMotorClient
from models import UserModel, ExerciseRoutineModel, TagsModel, PyObjectId, UpdateUserModel, UpdateTagsModel
from bson import ObjectId
from passlib.context import CryptContext
from typing import Optional
from fastapi import HTTPException


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)


client_users = AsyncIOMotorClient("mongodb+srv://Chris:Chris@timetoimprove.c17c0.mongodb.net/?retryWrites=true&w=majority&appName=TimeToImprove")
client_rutines = AsyncIOMotorClient("mongodb+srv://ttiappnews:hqZG0At2pI5wFOeU@rutines.bf1h9.mongodb.net/?retryWrites=true&w=majority&appName=rutines")

user_data_base = client_users.usersdatabase
user_collection = user_data_base.users

routines_data_base = client_rutines.routinedatabase
routines_collection = routines_data_base.routines

tags_data_base = client_users.tagsdatabase
tags_collection = tags_data_base.tags



async def get_user_id(id):
    user_id = await user_collection.find_one({"_id": ObjectId(id)})
    return user_id

async def get_user(user_name):
    user = await user_collection.find_one({"user_name": user_name})
    return user


async def get_user_email(email):
    user_email = await user_collection.find_one({"email": email})
    return user_email


async def get_users():
    Users = []
    cursor = user_collection.find({})
    async for document in cursor:
        Users.append(UserModel(**document))
    return Users


async def create_user(user: UserModel):
    # Hashear la contraseña
    hashed_password = get_password_hash(user.password)
    
    # Crear el diccionario del usuario, reemplazando la contraseña por su hash
    user_dict = user.dict()
    user_dict['hashed_password'] = hashed_password
    del user_dict['password']  # Eliminar el campo de la contraseña en texto plano

    # Insertar el nuevo usuario en la base de datos
    new_user = await user_collection.insert_one(user_dict)
    created_user = await user_collection.find_one({"_id": new_user.inserted_id})
    
    return created_user


async def update_user(id: str, data):
    user = {k:v for k, v in data.dict().items() if v is not None}
    print(user)
    await user_collection.update_one({"_id": ObjectId(id)}, {"$set": user})
    document = await user_collection.find_one({"_id": ObjectId(id)})
    return document

async def update_user_o(id: str, data):
    user = {k:v for k, v in data.items() if v is not None}
    print(user)
    await user_collection.update_one({"_id": ObjectId(id)}, {"$set": user})
    document = await user_collection.find_one({"_id": ObjectId(id)})
    return document

async def edit_user_login_o(id: str, user_data: UpdateUserModel):
    if not ObjectId.is_valid(id):
        raise ValueError("Invalid user ID.")
    response = await update_user_o(id, user_data)
    if response:
        return response
    raise HTTPException(404, f"User with id {id} not found")

async def edit_user_login(id: str, user_data: UpdateUserModel):
    if not ObjectId.is_valid(id):
        raise ValueError("Invalid user ID.")
    response = await update_user(id, user_data)
    if response:
        return response
    raise HTTPException(404, f"User with id {id} not found")

async def update_user_for_routine(id: str, data):
    user = {k: v for k, v in data.items() if v is not None}
    print(user)
    await user_collection.update_one({"_id": ObjectId(id)}, {"$set": user})
    document = await user_collection.find_one({"_id": ObjectId(id)})
    return document


async def delete_user(id: str):
    await user_collection.delete_one({"_id": ObjectId(id)})
    return True

async def update_user_first_login(user_id: ObjectId, value: bool):
    # Crear un diccionario para los campos que se van a actualizar
    update_data = {"first_login": value}

    # Actualizar solo el campo 'first_login'
    await UserModel.filter(id=user_id).update(**update_data)

async def get_tags():
    Tags = []
    cursor = tags_collection.find({})
    async for document in cursor:
        Tags.append(TagsModel(**document))
    return Tags

async def get_tags_user(tag_user_id):
    Tags = []
    cursor = tags_collection.find({"user_id": ObjectId(tag_user_id)})
    async for document in cursor:
        Tags.append(TagsModel(**document))
    return Tags

async def get_one_tag(id):
    tag_id = await tags_collection.find_one({"_id": ObjectId(id)})
    return tag_id

async def get_tag_day(day):
    tag_day = await tags_collection.find_one({"day": day})
    return tag_day

async def get_tag_user_id(user_id):
    tag_user_id = await tags_collection.find({"user_id": ObjectId(user_id)}).to_list(length=None)

    return tag_user_id

async def get_tag_user(user_id: PyObjectId, day: str ):
    tag = await tags_collection.find_one({"user_id": user_id, "day": day})
    return tag

async def create_tag(tag: TagsModel):
    # Convierte ObjectId a string antes de insertar
    tag_dict = tag.dict()
    tag_dict["user_id"] = tag_dict["user_id"] # Convierte a string si es ObjectId
    new_tag = await tags_collection.insert_one(tag_dict)
    
    # Asegúrate de que la respuesta contenga solo datos serializables
    created_tag = await tags_collection.find_one({"_id": new_tag.inserted_id})
    created_tag["_id"] = str(created_tag["_id"])  # Convierte a string

    return created_tag



async def update_tag(id: str, data):
    tag = {k:v for k, v in data.dict().items() if v is not None}
    print(tag)
    await tags_collection.update_one({"_id": ObjectId(id)}, {"$set": tag})
    document = await tags_collection.find_one({"_id": ObjectId(id)})
    return document

async def update_tags(id: str, data):

    if isinstance(data, dict):
        data = UpdateTagsModel(**data)

    tag = {k:v for k, v in data.dict().items() if v is not None}
    print(tag)
    await tags_collection.update_one({"_id": ObjectId(id)}, {"$set": tag})
    document = await tags_collection.find_one({"_id": ObjectId(id)})
    return document

async def delete_tag(id: str):
    # Intenta eliminar el documento de la colección
    result = await tags_collection.delete_one({"_id": ObjectId(id)})
    return result  # Devuelve el resultado de la operación de eliminación


async def create_base_routine():
    from routes.routines import get_base_routines

    base_routines = await get_base_routines()
    for routine in base_routines:
        # Verificar si la rutina ya existe en la base de datos
        existing_routine = await routines_collection.find_one({"name": routine.name})
        if not existing_routine:
            await routines_collection.insert_one(routine.dict(by_alias=True))


async def get_routines():
    Routines = []
    cursor = routines_collection.find({})
    async for document in cursor:
        Routines.append(ExerciseRoutineModel(**document))
    return Routines


async def get_routine_lvl_o(user_level: str) -> Optional[ExerciseRoutineModel]:
    routine = await routines_collection.find_one({"level": user_level})
    if routine:
        return ExerciseRoutineModel(**routine)
    return None

async def get_routine_id(id):
    routine_id = await routines_collection.find_one({"_id": ObjectId(id)})
    return routine_id

async def get_routine_id_o(id):
    routine_id = await routines_collection.find_one({"_id": ObjectId(id)})
    return ExerciseRoutineModel(**routine_id)


async def update_routine(id: str, data):
    routine = {k: v for k, v in data.items() if v is not None}
    print(routine)
    await routines_collection.update_one({"_id": ObjectId(id)}, {"$set": routine})
    document = await routines_collection.find_one({"_id": ObjectId(id)})
    return document


async def delete_routine(id: str):
    await routines_collection.delete_one({"_id": ObjectId(id)})
    return True


async def get_routine_lvl(level):
    routine = await routines_collection.find_one({"level": level})
    return routine

async def create_mod_routine(modify_level: str, level: str, user_id: PyObjectId):
    base_routine = await get_routine_lvl(level)
    rest_between_exercises = base_routine['rest_between_exercises']
    if not base_routine:
        raise HTTPException(status_code=404, detail="Base routine not found")

    new_exercises = base_routine['exercises']
    if modify_level == "mod_lev1":
        for exercise in new_exercises:
            exercise['rest_between_sets'] += 30
        rest_between_exercises += 45
    elif modify_level == "mod_lev2":
        new_exercises = [ex for ex in new_exercises if ex['exercise_type'] != "tren superior"]
    elif modify_level == "mod_lev3":
        new_exercises = [ex for ex in new_exercises if ex['exercise_type'] != "tren inferior"]

    new_routine = ExerciseRoutineModel(
        modify_level=modify_level,
        name=base_routine['name'] + " - Modificada",
        level=level,
        exercises=new_exercises,
        rest_between_exercises=rest_between_exercises,
        user_ids=[user_id]
    )
    inserted_routine = await routines_collection.insert_one(new_routine.dict())
    new_routine.id = inserted_routine.inserted_id

    current_user = await user_collection.find_one({"_id": ObjectId(user_id)})
    updated_routine_ids = [
        r_id for r_id in current_user['routine_ids']
        if not await routines_collection.find_one({"_id": r_id, "name": {"$regex": "cuerpo completo", "$options": "i"}})
    ]
    updated_routine_ids.append(new_routine.id)
    await edit_user_login_o(user_id, {"routine_ids": updated_routine_ids})

    return new_routine

async def get_routine_user(modify_level: str, level: str, user_id: PyObjectId):
    # Buscar rutina que coincida con `modify_level`, `level` y tenga "cuerpo completo" en el nombre
    routine = await routines_collection.find_one({
        "modify_level": modify_level,
        "level": level,
        "name": {"$regex": "cuerpo completo", "$options": "i"}
    })

    if routine:
        current_user = await user_collection.find_one({"_id": ObjectId(user_id)})
        # Reemplazar rutina existente si contiene "cuerpo completo"
        updated_routine_ids = [
            r_id for r_id in current_user['routine_ids']
            if not await routines_collection.find_one({"_id": r_id, "name": {"$regex": "cuerpo completo", "$options": "i"}})
        ]
        updated_routine_ids.append(routine['_id'])
        await update_user_for_routine(user_id, {"routine_ids": updated_routine_ids})

        return routine
    else:
        return await create_mod_routine(modify_level, level, user_id)
